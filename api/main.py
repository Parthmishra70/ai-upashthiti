from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base64
from pydantic import BaseModel
import uvicorn
from collections import defaultdict, Counter

app = FastAPI(
    title="AI Upashthiti - Face Recognition API",
    description="Face Recognition Attendance System API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to initialize face recognition model
model = None
try:
    import insightface
    model = insightface.app.FaceAnalysis(name='buffalo_l')
    model.prepare(ctx_id=-1)  # Use CPU
    print("✅ InsightFace model loaded successfully")
except ImportError:
    print("⚠️ InsightFace not available, using fallback face detection")
    model = None
except Exception as e:
    print(f"⚠️ InsightFace initialization failed: {e}")
    model = None

# Data models
class StudentRegistration(BaseModel):
    name: str
    student_id: Optional[str] = None

class AttendanceRecord(BaseModel):
    name: str
    timestamp: str
    confidence: float
    student_id: Optional[str] = None

class AttendanceStats(BaseModel):
    total_students: int
    present_today: int
    attendance_rate: float
    recent_entries: List[AttendanceRecord]

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_embeddings_db():
    try:
        with open("embeddings_db.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_embeddings_db(db):
    with open("embeddings_db.json", "w") as f:
        json.dump(db, f)

def load_attendance_records():
    records = []
    try:
        with open('attendance.csv', 'r') as f:
            for line in f:
                if 'Attendance Saved:' in line or 'Saved:' in line:
                    # Parse different formats
                    if 'Attendance Saved:' in line:
                        parts = line.split('time:')
                        if len(parts) >= 2:
                            name_part = parts[0].replace('Attendance Saved:', '').strip()
                            time_part = parts[1].split('Threshold:')[0].strip()
                            threshold_part = parts[1].split('Threshold:')[1].strip().replace('(', '').replace(')', '').replace(',', '')
                            
                            records.append({
                                'name': name_part,
                                'timestamp': time_part,
                                'confidence': float(threshold_part)
                            })
                    elif 'Saved:' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            name = parts[0].replace('Saved:', '').strip()
                            time_part = parts[1].replace('time:', '').strip()
                            threshold = parts[2].replace('threshold(', '').replace(')', '').strip()
                            
                            records.append({
                                'name': name,
                                'timestamp': time_part,
                                'confidence': float(threshold)
                            })
    except FileNotFoundError:
        pass
    return records

def save_attendance_record(name: str, confidence: float):
    timestamp = datetime.now()
    with open('attendance.csv', 'a') as f:
        f.write(f'Attendance Saved: {name} time: {timestamp} Threshold: ({confidence:.2f})\n')

def detect_faces_opencv(img):
    """Fallback face detection using OpenCV"""
    try:
        # Load OpenCV's pre-trained face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Convert to format similar to InsightFace
        detected_faces = []
        for (x, y, w, h) in faces:
            # Create a simple face object
            face_obj = type('Face', (), {})()
            face_obj.bbox = np.array([x, y, x+w, y+h])
            # Generate a simple embedding (this is a placeholder)
            face_region = gray[y:y+h, x:x+w]
            if face_region.size > 0:
                # Simple feature extraction (resize to fixed size and flatten)
                resized = cv2.resize(face_region, (64, 64))
                face_obj.embedding = resized.flatten().astype(np.float32)
            else:
                face_obj.embedding = np.random.rand(4096).astype(np.float32)
            detected_faces.append(face_obj)
        
        return detected_faces
    except Exception as e:
        print(f"OpenCV face detection error: {e}")
        return []

@app.get("/")
async def root():
    status = "online"
    face_engine = "InsightFace" if model else "OpenCV (Fallback)"
    return {
        "message": "AI Upashthiti Face Recognition API", 
        "version": "1.0.0", 
        "status": status,
        "face_engine": face_engine
    }

@app.post("/api/register")
async def register_student(
    name: str,
    file: UploadFile = File(...),
    student_id: Optional[str] = None
):
    """Register a new student with their face image"""
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Extract face embedding
        if model:
            faces = model.get(img)
        else:
            faces = detect_faces_opencv(img)
        
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the image")
        
        embedding = faces[0].embedding
        
        # Load existing database
        db = load_embeddings_db()
        
        # Save embedding
        db[name] = {
            "embedding": embedding.tolist(),
            "student_id": student_id,
            "registered_at": datetime.now().isoformat()
        }
        
        save_embeddings_db(db)
        
        return {
            "message": f"Student {name} registered successfully",
            "student_id": student_id,
            "faces_detected": len(faces)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recognize")
async def recognize_face(file: UploadFile = File(...)):
    """Recognize faces in an uploaded image"""
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Load database
        db = load_embeddings_db()
        if not db:
            raise HTTPException(status_code=404, detail="No registered students found")
        
        # Detect faces
        if model:
            faces = model.get(img)
        else:
            faces = detect_faces_opencv(img)
        
        if len(faces) == 0:
            return {"message": "No faces detected", "recognized_faces": []}
        
        recognized_faces = []
        
        for face in faces:
            embedding = face.embedding
            best_match = None
            best_score = 0
            
            for name, data in db.items():
                if isinstance(data, dict):
                    ref_emb = data["embedding"]
                    student_id = data.get("student_id")
                else:
                    ref_emb = data
                    student_id = None
                
                score = cosine_similarity(embedding, ref_emb)
                if score > best_score:
                    best_score = score
                    best_match = name
            
            # Lower threshold for OpenCV fallback
            threshold = 0.6 if model else 0.3
            if best_score > threshold:
                # Save attendance record
                save_attendance_record(best_match, best_score)
                
                recognized_faces.append({
                    "name": best_match,
                    "confidence": round(best_score, 3),
                    "student_id": student_id,
                    "bbox": face.bbox.tolist()
                })
        
        return {
            "message": f"Recognized {len(recognized_faces)} faces",
            "recognized_faces": recognized_faces,
            "total_faces_detected": len(faces)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students")
async def get_registered_students():
    """Get list of all registered students"""
    try:
        db = load_embeddings_db()
        students = []
        
        for name, data in db.items():
            if isinstance(data, dict):
                students.append({
                    "name": name,
                    "student_id": data.get("student_id"),
                    "registered_at": data.get("registered_at")
                })
            else:
                students.append({
                    "name": name,
                    "student_id": None,
                    "registered_at": None
                })
        
        return {"students": students, "total": len(students)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/today")
async def get_today_attendance():
    """Get today's attendance records"""
    try:
        records = load_attendance_records()
        today = datetime.now().date()
        
        today_records = []
        for record in records:
            try:
                record_date = datetime.fromisoformat(record['timestamp'].replace(' ', 'T')).date()
                if record_date == today:
                    today_records.append(record)
            except:
                continue
        
        # Get unique attendees for today
        unique_attendees = list(set(record['name'] for record in today_records))
        
        return {
            "date": today.isoformat(),
            "total_entries": len(today_records),
            "unique_students": len(unique_attendees),
            "records": today_records[-20:],  # Last 20 records
            "attendees": unique_attendees
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/stats")
async def get_attendance_stats():
    """Get attendance statistics"""
    try:
        db = load_embeddings_db()
        records = load_attendance_records()
        
        total_students = len(db)
        today = datetime.now().date()
        
        # Today's unique attendees
        today_attendees = set()
        recent_entries = []
        
        for record in records:
            try:
                record_date = datetime.fromisoformat(record['timestamp'].replace(' ', 'T')).date()
                if record_date == today:
                    today_attendees.add(record['name'])
                
                # Keep recent entries (last 10)
                if len(recent_entries) < 10:
                    recent_entries.insert(0, {
                        "name": record['name'],
                        "timestamp": record['timestamp'],
                        "confidence": record['confidence']
                    })
            except:
                continue
        
        present_today = len(today_attendees)
        attendance_rate = (present_today / total_students * 100) if total_students > 0 else 0
        
        return {
            "total_students": total_students,
            "present_today": present_today,
            "attendance_rate": round(attendance_rate, 1),
            "recent_entries": recent_entries
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/history")
async def get_attendance_history(days: int = 7):
    """Get attendance history for specified number of days"""
    try:
        records = load_attendance_records()
        
        # Group by date
        daily_attendance = defaultdict(set)
        
        for record in records:
            try:
                record_date = datetime.fromisoformat(record['timestamp'].replace(' ', 'T')).date()
                daily_attendance[record_date.isoformat()].add(record['name'])
            except:
                continue
        
        # Get last N days
        history = []
        for i in range(days):
            date = (datetime.now().date() - timedelta(days=i)).isoformat()
            attendees = list(daily_attendance.get(date, set()))
            history.append({
                "date": date,
                "count": len(attendees),
                "attendees": attendees
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/students/{student_name}")
async def delete_student(student_name: str):
    """Delete a registered student"""
    try:
        db = load_embeddings_db()
        
        if student_name not in db:
            raise HTTPException(status_code=404, detail="Student not found")
        
        del db[student_name]
        save_embeddings_db(db)
        
        return {"message": f"Student {student_name} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)