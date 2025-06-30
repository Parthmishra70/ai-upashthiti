import insightface
import cv2
import numpy as np
import json
from datetime import datetime

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

model = insightface.app.FaceAnalysis(name='buffalo_l')
model.prepare(ctx_id=0)

with open("embeddings_db.json", "r") as f:
    db = json.load(f)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = model.get(frame)

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        embedding = face.embedding
        best_match = "Unknown"
        best_score = 0

        for name, ref_emb in db.items():
            score = cosine_similarity(embedding, ref_emb)
            if score > 0.7:
                best_score = score
                best_match = name
                with open('attandance.csv','a') as a:
                    a.write(f'Saved: {name}, time: {datetime.now()} threshold({score})\n')
        label = f"{best_match} ({best_score:.2f})" if best_score > 0.5 else "Unknown"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
