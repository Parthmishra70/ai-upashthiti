import cv2
import insightface
import numpy as np
import json
import os
from datetime import datetime

# ======= CONFIGURATION =======
input_path = "/Users/parthmishra/Desktop/Upashthiti/model2_InsightFace/input.mp4"
output_path = "/Users/parthmishra/Desktop/Upashthiti/model2_InsightFace/output.mp4"
db_path = "/Users/parthmishra/Desktop/Upashthiti/model2_InsightFace/embeddings_db2.json"
attendance_path = "/Users/parthmishra/Desktop/Upashthiti/model2_InsightFace/attandance.csv"

# ======= Load Face Detection Model =======
model = insightface.app.FaceAnalysis(name='buffalo_l')
model.prepare(ctx_id=0)

# ======= Check or Create Embedding DB =======
if not os.path.exists(db_path):
    dummy_embedding = np.random.rand(512).tolist()
    with open(db_path, "w") as f:
        json.dump({"TestUser": dummy_embedding}, f)

# ======= Load Embeddings =======
with open(db_path, "r") as f:
    db = json.load(f)

# ======= Open Video =======
cap = cv2.VideoCapture(input_path)
if not cap.isOpened():
    print(f"❌ Video '{input_path}' open nahi ho raha. Check path or format.")
    exit()

# ======= Video Properties =======
fps = cap.get(cv2.CAP_PROP_FPS)
frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("🎥 FPS:", fps)
print("📐 Resolution:", frame_w, "x", frame_h)

if fps == 0 or frame_w == 0 or frame_h == 0:
    print("❌ FPS ya resolution galat aa raha hai. File corrupt banegi.")
    cap.release()
    exit()

# ======= Setup Output Writer =======
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_w, frame_h))

# ======= Frame Loop =======
frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    faces = model.get(frame)
    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        embedding = face.embedding
        best_match = None
        best_score = 0

        for name, ref_emb in db.items():
            score = np.dot(embedding, ref_emb) / (np.linalg.norm(embedding) * np.linalg.norm(ref_emb))
            if score > best_score:
                best_score = score
                best_match = name


        # ✅ Show Name and Box (NO BLUR)
        label = best_match if best_score > 0.5 else "Unknown"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # ======= Attendance Log =======
        if best_score > 0.5:
            label = best_match
            with open(attendance_path, 'a') as a:
                a.write(f'{best_match}, {datetime.now()}, Score: {best_score:.2f}, Frame: {frame_count}\n')
                print(f"→ Match: {best_match}, Score: {best_score}")
        else:
            label = "Unknown"

        # Show on screen
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Write to output video
    out.write(frame)
  

    print(f"📽 Processing frame {frame_count}...", end='\r')

# ======= Finish =======
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"\n✅ DONE: Face detection complete!\n🎬 Saved video: {output_path}\n📝 Attendance: {attendance_path}")
