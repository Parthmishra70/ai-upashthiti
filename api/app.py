from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import cv2
import io
import json
from datetime import datetime
import csv
import os
import base64
import glob
from insightface.app import FaceAnalysis

# Configurations
EMBEDDINGS_DB_PATH = "embeddings_db.json"
ATTENDANCE_LOG_PATH = "attendance.csv"
THRESHOLD = 0.5

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load face recognition model with error handling
model = None
try:
    print("🔄 Loading InsightFace Buffalo model...")
    model = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    model.prepare(ctx_id=-1)  # Use CPU for Railway compatibility
    print("✅ InsightFace Buffalo model loaded successfully")
except Exception as e:
    print(f"❌ Failed to initialize face model: {str(e)}")
    model = None

# Load database embeddings
db = {}
try:
    if os.path.exists(EMBEDDINGS_DB_PATH):
        with open(EMBEDDINGS_DB_PATH, "r") as f:
            db = json.load(f)
        print(f"✅ Loaded {len(db)} face embeddings from database")
    else:
        print("ℹ️ No existing embeddings database found, creating new one")
        db = {}
except Exception as e:
    print(f"⚠️ Failed to load embeddings database: {str(e)}")
    db = {}

# Cosine similarity function
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Record attendance in CSV
def log_attendance(name, score):
    try:
        with open(ATTENDANCE_LOG_PATH, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), name, f"{score:.2f}"])
    except Exception as e:
        print(f"Error logging attendance: {e}")

# Optional mask: blur
def mask_face(image):
    return cv2.GaussianBlur(image, (99, 99), 30)

def compute_average_embedding(embeddings):
    if not embeddings:
        return None
    arr = np.array(embeddings)
    return arr.mean(axis=0).tolist()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "message": "AI Upashthiti Face Recognition API",
        "version": "1.0.0",
        "status": "online",
        "face_engine": "InsightFace Buffalo" if model else "❌ InsightFace Not Available",
        "buffalo_model": model is not None,
        "registered_faces": len(db)
    })

@app.route('/api/register', methods=['POST'])
def register_faces():
    """
    Scans the 'train' directory, computes embeddings for each person,
    and updates embeddings_db.json with the average embedding per person.
    """
    if not model:
        return jsonify({"error": "Face recognition model not available"}), 503
    
    TRAIN_DIR = "train"
    new_db = {}

    if not os.path.exists(TRAIN_DIR):
        return jsonify({"error": f"'{TRAIN_DIR}' folder not found"}), 400

    try:
        for person_name in os.listdir(TRAIN_DIR):
            person_path = os.path.join(TRAIN_DIR, person_name)
            if not os.path.isdir(person_path):
                continue
            
            embeddings = []
            for img_path in glob.glob(os.path.join(person_path, "*")):
                try:
                    img = cv2.imread(img_path)
                    if img is None:
                        continue
                    faces = model.get(img)
                    if not faces:
                        continue
                    # Use the largest face (if multiple)
                    face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
                    if face.embedding is not None:
                        embeddings.append(face.embedding.tolist())
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
            
            avg_emb = compute_average_embedding(embeddings)
            if avg_emb is not None:
                new_db[person_name] = avg_emb

        # Save to embeddings_db.json
        with open(EMBEDDINGS_DB_PATH, "w") as f:
            json.dump(new_db, f, indent=2)
        
        # Update global db
        global db
        db = new_db

        return jsonify({
            "status": "success", 
            "registered": list(new_db.keys()),
            "count": len(new_db)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register-single', methods=['POST'])
def register_single_face():
    """Register a single person with uploaded image"""
    if not model:
        return jsonify({"error": "Face recognition model not available"}), 503
    
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({"error": "Missing file or name"}), 400

    file = request.files['file']
    name = request.form['name']
    
    if not file or not file.content_type.startswith('image/'):
        return jsonify({"error": "File must be an image"}), 400

    try:
        # Read and process image
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        faces = model.get(img_bgr)
        if not faces:
            return jsonify({"error": "No face detected in image"}), 400

        # Use the largest face
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
        
        if face.embedding is None:
            return jsonify({"error": "Could not extract face embedding"}), 400

        # Save embedding to database
        global db
        db[name] = face.embedding.tolist()
        
        with open(EMBEDDINGS_DB_PATH, "w") as f:
            json.dump(db, f, indent=2)

        return jsonify({
            "status": "success",
            "message": f"Successfully registered {name}",
            "faces_detected": len(faces)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded image for face recognition"""
    if not model:
        return jsonify({"error": "Face recognition model not available"}), 503
    
    if 'frame' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['frame']
    if not file or not file.content_type.startswith('image/'):
        return jsonify({"error": "File must be an image"}), 400

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        faces = model.get(img_bgr)
        results = []

        for face in faces:
            if face.embedding is None:
                continue

            x1, y1, x2, y2 = list(map(int, face.bbox))
            face_img = img_bgr[y1:y2, x1:x2]

            # Mask and encode to base64
            masked_face = mask_face(face_img)
            _, buffer = cv2.imencode('.jpg', masked_face)
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            face_data_url = f"data:image/jpeg;base64,{face_base64}"

            # Face matching
            best_score = 0.0
            best_match = "Unknown"

            for name, ref_emb in db.items():
                score = cosine_similarity(face.embedding, np.array(ref_emb))
                if score > best_score:
                    best_score = score
                    best_match = name

            # Use match if above threshold
            if best_score >= THRESHOLD:
                detected_name = best_match
                log_attendance(detected_name, best_score)

                result = {
                    "name": detected_name,
                    "confidence": best_score,
                    "image": face_data_url,
                    "datetime": datetime.now().isoformat()
                }
                results.append(result)
            else:
                # If not recognized, still return but mark as unknown
                results.append({
                    "name": "Unknown",
                    "confidence": best_score,
                    "image": face_data_url,
                    "datetime": datetime.now().isoformat()
                })

        return jsonify({
            "results": results,
            "total_faces": len(faces),
            "recognized_faces": len([r for r in results if r["name"] != "Unknown"])
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get list of registered students"""
    students = []
    for name in db.keys():
        students.append({
            "name": name,
            "registered_at": datetime.now().isoformat()  # Placeholder
        })
    
    return jsonify({
        "students": students,
        "total": len(students)
    })

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get attendance records"""
    try:
        records = []
        if os.path.exists(ATTENDANCE_LOG_PATH):
            with open(ATTENDANCE_LOG_PATH, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3:
                        records.append({
                            "timestamp": row[0],
                            "name": row[1],
                            "confidence": float(row[2])
                        })
        
        return jsonify({
            "records": records[-50:],  # Last 50 records
            "total": len(records)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def detailed_health():
    """Detailed health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "buffalo_model_loaded": model is not None,
        "insightface_available": model is not None,
        "registered_faces": len(db),
        "embeddings_file_exists": os.path.exists(EMBEDDINGS_DB_PATH),
        "attendance_file_exists": os.path.exists(ATTENDANCE_LOG_PATH)
    })

# Run the server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5174))
    print(f"🚀 Starting AI Upashthiti API on port {port}")
    print(f"🤖 Buffalo model status: {'✅ Loaded' if model else '❌ Not Available'}")
    print(f"👥 Registered faces: {len(db)}")
    app.run(host="0.0.0.0", port=port, debug=False)