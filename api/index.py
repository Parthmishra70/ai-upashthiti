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
from insightface.app import FaceAnalysis

# Configurations
EMBEDDINGS_DB_PATH = "embeddings_db.json"
ATTENDANCE_LOG_PATH = "attendance.csv"
THRESHOLD = 0.5

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load face recognition model
try:
    providers = ["CUDAExecutionProvider"] if cv2.cuda.getCudaEnabledDeviceCount() > 0 else ["CPUExecutionProvider"]
    model = FaceAnalysis(name="buffalo_l", providers=providers)
    model.prepare(ctx_id=0)
except Exception as e:
    raise RuntimeError(f"Failed to initialize face model: {str(e)}")

# Load database embeddings
try:
    with open(EMBEDDINGS_DB_PATH, "r") as f:
        db = json.load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load embeddings database: {str(e)}")

# Cosine similarity function
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Record attendance in CSV
def log_attendance(name, score):
    with open(ATTENDANCE_LOG_PATH, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), name, f"{score:.2f}"])


# Optional mask: blur
def mask_face(image):
    return cv2.GaussianBlur(image, (99, 99), 30)

def compute_average_embedding(embeddings):
    if not embeddings:
        return None
    arr = np.array(embeddings)
    return arr.mean(axis=0).tolist()

@app.route('/api/register', methods=['POST'])
def register_faces():
    """
    Scans the 'train' directory, computes embeddings for each person,
    and updates embeddings_db.json with the average embedding per person.
    """
    TRAIN_DIR = "train"
    new_db = {}

    if not os.path.exists(TRAIN_DIR):
        return jsonify({"error": f"'{TRAIN_DIR}' folder not found"}), 400

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
                    embeddings.append(face.embedding)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        avg_emb = compute_average_embedding(embeddings)
        if avg_emb is not None:
            new_db[person_name] = avg_emb

    # Save to embeddings_db.json
    with open(EMBEDDINGS_DB_PATH, "w") as f:
        json.dump(new_db, f, indent=2)

    return jsonify({"status": "success", "registered": list(new_db.keys())})


@app.route('/api/analyze', methods=['POST'])
def analyze():
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
                    "image": face_data_url,
                    "datetime": datetime.now().isoformat()
                }

                results.append(result)
            else:
                # If not recognized, skip saving
                results.append({
                    "name": "Unknown",
                    "image": face_data_url,
                    "datetime": datetime.now().isoformat()
                })

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5174)