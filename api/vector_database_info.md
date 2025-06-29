# 🧠 Face Embeddings Vector Database

## What is this file?

The `embeddings_db.json` file is your **face vector database** that stores the mathematical representations (embeddings) of each registered student's face.

## How it works:

### 🔢 **Face Vectors (Embeddings)**
Each student's face is converted into a **512-dimensional vector** by the InsightFace Buffalo model:

```json
{
  "Pathak": [2.0179107189178467, -0.6208834052085876, -1.784844160079956, ...],
  "Parth Mishra": [0.801777720451355, 1.7803161144256592, 0.2419009953737259, ...]
}
```

### 🧮 **Vector Comparison Process**

1. **Registration**: When you register a student, their face photo is converted to a 512-number vector
2. **Recognition**: When recognizing faces, new photos are also converted to vectors
3. **Similarity**: The system compares vectors using **cosine similarity**
4. **Matching**: If similarity > 60%, it's considered a match

### 📊 **Cosine Similarity Formula**

```python
def cosine_similarity(vector_a, vector_b):
    dot_product = np.dot(vector_a, vector_b)
    magnitude_a = np.linalg.norm(vector_a)
    magnitude_b = np.linalg.norm(vector_b)
    return dot_product / (magnitude_a * magnitude_b)
```

### 🎯 **Current Database**

Your database contains **2 registered students**:

1. **Pathak** - 512-dimensional face vector
2. **Parth Mishra** - 512-dimensional face vector

### 🔍 **How Recognition Works**

1. Upload a photo → Extract face → Generate 512-number vector
2. Compare with **Pathak's vector** → Calculate similarity score
3. Compare with **Parth Mishra's vector** → Calculate similarity score
4. If any score > 0.6 (60%) → Match found!
5. Return the best match with confidence score

### 💾 **Database Structure**

```json
{
  "student_name": [
    dimension_1, dimension_2, dimension_3, ..., dimension_512
  ]
}
```

Each number represents a specific facial feature encoded by the AI model.

### 🚀 **Why This Works**

- **Unique**: Each person's face creates a unique vector pattern
- **Consistent**: Same person's photos create similar vectors
- **Fast**: Vector comparison is mathematically efficient
- **Accurate**: Buffalo model creates highly distinctive embeddings

Your face recognition system is now powered by this vector database! 🎉