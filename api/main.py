from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Optional
import uvicorn
import warnings

# Suppress ONNX Runtime warnings about CUDA
warnings.filterwarnings("ignore", message=".*CUDAExecutionProvider.*")
warnings.filterwarnings("ignore", message=".*Specified provider.*")

app = FastAPI(
    title="AI Upashthiti - Face Recognition API",
    description="Simple Face Recognition API",
    version="1.0.0"
)

# CORS middleware - Fixed for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize face recognition model with error handling
model = None
try:
    import insightface
    print("🔄 Loading InsightFace Buffalo model...")
    
    # Force CPU-only execution for Railway compatibility
    model = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    model.prepare(ctx_id=-1)
    print("✅ InsightFace Buffalo model loaded successfully on CPU")
except Exception as e:
    print(f"❌ InsightFace initialization failed: {e}")
    model = None

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
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        return {}

def save_embeddings_db(db):
    try:
        with open("embeddings_db.json", "w") as f:
            json.dump(db, f)
    except Exception as e:
        print(f"Error saving embeddings: {e}")

def save_attendance_record(name: str, confidence: float):
    try:
        timestamp = datetime.now()
        with open('attendance.csv', 'a') as f:
            f.write(f'Attendance Saved: {name} time: {timestamp} Threshold: ({confidence:.2f})\n')
    except Exception as e:
        print(f"Error saving attendance: {e}")

@app.get("/")
async def root():
    return {
        "message": "AI Upashthiti Face Recognition API", 
        "version": "1.0.0", 
        "status": "online",
        "buffalo_model": model is not None,
        "cors_enabled": True
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
            detail="Face recognition model not available"
        )
    
    try:
        # Read and decode image with error handling
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format or corrupted file")
        
        # Check image size
        if img.shape[0] < 50 or img.shape[1] < 50:
            raise HTTPException(status_code=400, detail="Image too small - minimum 50x50 pixels required")
        
        # Extract face embedding
        faces = model.get(img)
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the image")
        
        # Use the largest face if multiple detected
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
        embedding = face.embedding
        
        # Load and save to database
        db = load_embeddings_db()
        db[name] = {
            "embedding": embedding.tolist(),
            "student_id": student_id,
            "registered_at": datetime.now().isoformat()
        }
        save_embeddings_db(db)
        
        return {
            "message": f"Student {name} registered successfully",
            "student_id": student_id,
            "faces_detected": len(faces),
            "model_used": "buffalo_l"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/recognize")
async def recognize_face(file: UploadFile = File(...)):
    """Recognize faces in an uploaded image"""
    if not model:
        raise HTTPException(
            status_code=503, 
            detail="Face recognition model not available"
        )
    
    try:
        # Read and validate file
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Check file size (limit to 10MB)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large - maximum 10MB allowed")
        
        # Decode image
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format or corrupted file")
        
        # Check image dimensions
        if img.shape[0] < 50 or img.shape[1] < 50:
            raise HTTPException(status_code=400, detail="Image too small - minimum 50x50 pixels required")
        
        # Resize if image is too large (to prevent memory issues)
        max_dimension = 1024
        if img.shape[0] > max_dimension or img.shape[1] > max_dimension:
            scale = max_dimension / max(img.shape[0], img.shape[1])
            new_width = int(img.shape[1] * scale)
            new_height = int(img.shape[0] * scale)
            img = cv2.resize(img, (new_width, new_height))
        
        # Load database
        db = load_embeddings_db()
        if not db:
            return {
                "message": "No registered students found", 
                "recognized_faces": [], 
                "total_faces_detected": 0
            }
        
        # Detect faces
        faces = model.get(img)
        if len(faces) == 0:
            return {
                "message": "No faces detected in image", 
                "recognized_faces": [], 
                "total_faces_detected": 0
            }
        
        recognized_faces = []
        
        for face in faces:
            try:
                embedding = face.embedding
                best_match = None
                best_score = 0
                
                # Compare with all registered students
                for name, data in db.items():
                    try:
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
                    except Exception as e:
                        print(f"Error comparing with {name}: {e}")
                        continue
                
                # Check if match is above threshold
                if best_score > 0.6:  # 60% confidence threshold
                    save_attendance_record(best_match, best_score)
                    
                    recognized_faces.append({
                        "name": best_match,
                        "confidence": round(best_score, 3),
                        "student_id": student_id,
                        "bbox": face.bbox.tolist()
                    })
            except Exception as e:
                print(f"Error processing face: {e}")
                continue
        
        return {
            "message": f"Processed {len(faces)} faces, recognized {len(recognized_faces)} students",
            "recognized_faces": recognized_faces,
            "total_faces_detected": len(faces),
            "model_used": "buffalo_l"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Recognition error: {e}")
        raise HTTPException(status_code=500, detail=f"Recognition failed: {str(e)}")

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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "buffalo_model_loaded": model is not None,
        "insightface_available": model is not None,
        "execution_provider": "CPUExecutionProvider"
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
    uvicorn.run(app, host="0.0.0.0", port=port)