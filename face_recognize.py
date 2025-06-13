import insightface
import cv2
import numpy as np
import json
import os
from datetime import datetime

path = 'test_images'
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

model = insightface.app.FaceAnalysis(name='buffalo_l')
model.prepare(ctx_id=0)

with open("embeddings_db.json", "r") as f:
    db = json.load(f)



for student_name in os.listdir(path):
    img_path = os.path.join(path,student_name)    # img_path = os.path.join(student_name)
    
    print(img_path)
    img = cv2.imread(img_path)
    faces = model.get(img)

    if len(faces) == 0:
        print("❌ No face found.")
    else:
        face = faces[0]
        embedding = face.embedding
        best_match = None
        best_score = 0

        for name, ref_emb in db.items():
            score = cosine_similarity(embedding, ref_emb)
            if score > best_score:
                best_score = score
                best_match = name
            with open('attandance.csv','a') as a:
                a.write(f'Attandance Saved:  {best_match} time: {datetime.now()} Threshold: ({best_score:.2f}),\n')
        print(f"✅ Best Match: {best_match} ({best_score:.2f})" if best_score > 0.5 else "❌ No match found.")
