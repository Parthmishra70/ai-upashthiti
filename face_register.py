import insightface
import cv2
import os
import numpy as np
import json


'''
name='buffalo_l': This selects the model configuration named buffalo_l, which includes:

RetinaFace for detection

ArcFace (large version) for 512-dimensional face embeddings

Landmark localization for alignment

'''


model = insightface.app.FaceAnalysis(name='buffalo_l')
model.prepare(ctx_id=0)

db = {}
path = "registered_faces"

for student_name in os.listdir(path):
    student_folder = os.path.join(path, student_name)

    # Skip if not a directory
    if not os.path.isdir(student_folder):
        continue

    for student_img in os.listdir(student_folder):
        img_path = os.path.join(student_folder, student_img)

        # Only process image files
        if not img_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        img = cv2.imread(img_path)
        faces = model.get(img)
        if len(faces) == 0:
            print(f"❌ No face found in {img_path}")
            continue

        embedding = faces[0].embedding
        db[student_name] = embedding.tolist()
        print(f"✅ Saved embedding for {student_name}")
        break  # only take one image per student

# Save to JSON
with open("embeddings_db.json", "w") as f:
    json.dump(db, f)

print("✅ All face embeddings registered successfully.")