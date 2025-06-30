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
import warnings

# Suppress ONNX Runtime warnings about CUDA
warnings.filterwarnings("ignore", message=".*CUDAExecutionProvider.*")
warnings.filterwarnings("ignore", message=".*Specified provider.*")

app = FastAPI(
    title="AI Upashthiti - Face Recognition API",
    description="Face Recognition Attendance System API with Streaming Support",
    version="1.0.0"
)

# CORS middleware - FIXED for your domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for streaming
        "https://zp1v56uxy8rdx5ypatb0ockcb9tr6a-oci3--3000--cb7c0bca.local-credentialless.webcontainer-api.io",
        "http://localhost:3000",
        "https://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize face recognition model with Buffalo
model = None
try:
    import insightface
    import os
    print("🔄 Loading InsightFace Buffalo model...")
    
    # Set model path from environment variable
    model_path = os.getenv('INSIGHTFACE_MODEL_PATH', '/root/.insightface/models')
    os.environ['INSIGHTFACE_HOME'] = os.path.dirname(model_path)
    
    # Force CPU-only execution for Railway compatibility
    model = insightface.app.FaceAnalysis(
        name='buffalo_l',
        root=model_path,
        providers=['CPUExecutionProvider']  # Only use CPU
    )
    model.prepare(ctx_id=-1)  # Use CPU for Railway compatibility
    print(f"✅ InsightFace Buffalo model loaded successfully from {model_path}")
    print(f"📂 Model cache location: {os.getenv('INSIGHTFACE_HOME')}")
except ImportError as e:
    print(f"❌ InsightFace not available: {e}")
    print("⚠️ Face recognition will not work without InsightFace")
    model = None
except Exception as e:
    print(f"❌ InsightFace initialization failed: {e}")
    print("⚠️ Trying to continue without InsightFace...")
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

# Optional mask: blur faces for privacy
def mask_face(image):
    return cv2.GaussianBlur(image, (99, 99), 30)

@app.get("/")
async def root():
    status = "online"
    face_engine = "InsightFace Buffalo (CPU)" if model else "❌ InsightFace Not Available"
    return {
        "message": "AI Upashthiti Face Recognition API", 
        "version": "1.0.0", 
        "status": status,
        "face_engine": face_engine,
        "buffalo_model": model is not None,
        "execution_provider": "CPUExecutionProvider",
        "cors_enabled": True,
        "streaming_support": True,
        "endpoints": {
            "register": "POST /api/register",
            "recognize": "POST /api/analyze", 
            "analyze": "POST /api/analyze (for streaming)",
            "students": "GET /api/students",
            "health": "GET /api/health"
        }
    }

@app.post("/api/register")
async def register_student(
    name: str,
    file: UploadFile = File(...),
    student_id: Optional[str] = None
):
    """Register a new student with their face image"""
    if not model:
        raise HTTPException(
            status_code=503, 
            detail="Face recognition model not available. InsightFace Buffalo model required."
        )
    
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Extract face embedding using Buffalo model
        faces = model.get(img)
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
            "message": f"Student {name} registered successfully with Buffalo model",
            "student_id": student_id,
            "faces_detected": len(faces),
            "model_used": "buffalo_l",
            "execution_provider": "CPUExecutionProvider"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def recognize_face(file: UploadFile = File(...)):
    """Recognize faces in an uploaded image using Buffalo model"""
    if not model:
        raise HTTPException(
            status_code=503, 
            detail="Face recognition model not available. InsightFace Buffalo model required."
        )
    
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
        
        # Detect faces using Buffalo model
        faces = model.get(img)
        if len(faces) == 0:
            return {
                "message": "No faces detected", 
                "recognized_faces": [], 
                "total_faces_detected": 0, 
                "model_used": "buffalo_l",
                "execution_provider": "CPUExecutionProvider"
            }
        
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
            
            if best_score > 0.6:  # Buffalo model confidence threshold
                # Save attendance record
                save_attendance_record(best_match, best_score)
                
                recognized_faces.append({
                    "name": best_match,
                    "confidence": round(best_score, 3),
                    "student_id": student_id,
                    "bbox": face.bbox.tolist()
                })
        
        return {
            "message": f"Recognized {len(recognized_faces)} faces using Buffalo model",
            "recognized_faces": recognized_faces,
            "total_faces_detected": len(faces),
            "model_used": "buffalo_l",
            "execution_provider": "CPUExecutionProvider"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_stream_frame(file: UploadFile = File(...)):
    """
    🎥 STREAMING ENDPOINT - Analyze frame from video stream
    
    This endpoint is designed for real-time streaming from other websites.
    It processes individual frames and returns face detection results with masked faces.
    
    Usage by other websites:
    - Send video frames as they capture them
    - Get real-time face recognition results
    - Receive masked face images for privacy
    - Get attendance logging with timestamps
    """
    if not model:
        raise HTTPException(
            status_code=503, 
            detail="Face recognition model not available"
        )
    
    try:
        # Read and decode frame
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Load database
        db = load_embeddings_db()
        if not db:
            return {
                "results": [],
                "total_faces": 0,
                "recognized_faces": 0,
                "message": "No registered students in database"
            }
        
        # Detect faces using Buffalo model
        faces = model.get(img_bgr)
        results = []
        
        for face in faces:
            if face.embedding is None:
                continue

            x1, y1, x2, y2 = list(map(int, face.bbox))
            face_img = img_bgr[y1:y2, x1:x2]

            # Mask face for privacy (blur)
            masked_face = mask_face(face_img)
            _, buffer = cv2.imencode('.jpg', masked_face)
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            face_data_url = f"data:image/jpeg;base64,{face_base64}"

            # Face matching
            best_score = 0.0
            best_match = "Unknown"
            student_id = None

            for name, data in db.items():
                if isinstance(data, dict):
                    ref_emb = data["embedding"]
                    sid = data.get("student_id")
                else:
                    ref_emb = data
                    sid = None
                
                score = cosine_similarity(face.embedding, np.array(ref_emb))
                if score > best_score:
                    best_score = score
                    best_match = name
                    student_id = sid

            # Use match if above threshold
            if best_score >= 0.6:  # 60% confidence threshold
                detected_name = best_match
                save_attendance_record(detected_name, best_score)

                result = {
                    "name": detected_name,
                    "confidence": round(best_score, 3),
                    "student_id": student_id,
                    "image": face_data_url,  # Masked face image
                    "datetime": datetime.now().isoformat(),
                    "bbox": [x1, y1, x2, y2]
                }
                results.append(result)
            else:
                # Unknown face - still return but mark as unknown
                results.append({
                    "name": "Unknown",
                    "confidence": round(best_score, 3),
                    "student_id": None,
                    "image": face_data_url,  # Masked face image
                    "datetime": datetime.now().isoformat(),
                    "bbox": [x1, y1, x2, y2]
                })

        return {
            "results": results,
            "total_faces": len(faces),
            "recognized_faces": len([r for r in results if r["name"] != "Unknown"]),
            "message": f"Processed {len(faces)} faces, recognized {len([r for r in results if r['name'] != 'Unknown'])} students",
            "model_used": "buffalo_l",
            "timestamp": datetime.now().isoformat()
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "buffalo_model_loaded": model is not None,
        "insightface_available": model is not None,
        "execution_provider": "CPUExecutionProvider",
        "warnings_suppressed": True,
        "cors_enabled": True,
        "streaming_ready": True
    }

# Add OPTIONS handler for CORS preflight
@app.options("/{full_path:path}")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting AI Upashthiti API on port {port}")
    print(f"🤖 Buffalo model status: {'✅ Loaded (CPU)' if model else '❌ Not Available'}")
    print(f"🔧 Execution Provider: CPUExecutionProvider")
    print(f"🌐 CORS enabled for all origins")
    print(f"🎥 Streaming endpoint ready: /api/analyze")
    uvicorn.run(app, host="0.0.0.0", port=port)