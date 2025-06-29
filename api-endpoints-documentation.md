# 🚀 AI Upashthiti API - Complete Endpoints Documentation

## 🌐 Base URL
```
https://web-production-13b09.up.railway.app
```

## 📋 Available Endpoints

### 1. 🎥 **Streaming Face Recognition** (NEW!)
```http
POST /api/analyze
Content-Type: multipart/form-data
Body: file (image/video frame)
```

**Purpose:** Real-time streaming face recognition for other websites
**Use Case:** Video streams, live cameras, continuous monitoring

**Response:**
```json
{
  "results": [
    {
      "name": "Pathak",
      "confidence": 0.85,
      "student_id": "STU001",
      "image": "data:image/jpeg;base64,/9j/...", // Masked face
      "datetime": "2025-06-29T16:45:30.123456",
      "bbox": [100, 150, 200, 250]
    }
  ],
  "total_faces": 2,
  "recognized_faces": 1,
  "message": "Processed 2 faces, recognized 1 students",
  "model_used": "buffalo_l",
  "timestamp": "2025-06-29T16:45:30.123456"
}
```

### 2. 🔍 **Single Image Recognition**
```http
POST /api/analyze
Content-Type: multipart/form-data
Body: file (image)
```

**Purpose:** Recognize faces in uploaded images
**Use Case:** Photo uploads, batch processing

### 3. 👤 **Student Registration**
```http
POST /api/register
Content-Type: multipart/form-data
Body: name, file, student_id (optional)
```

**Purpose:** Register new students in the system

### 4. 👥 **Get Students**
```http
GET /api/students
```

**Purpose:** Get list of all registered students

### 5. 📊 **Attendance Statistics**
```http
GET /api/attendance/stats
```

**Purpose:** Get attendance statistics and recent activity

### 6. 📅 **Today's Attendance**
```http
GET /api/attendance/today
```

**Purpose:** Get today's attendance records

### 7. 📈 **Attendance History**
```http
GET /api/attendance/history?days=7
```

**Purpose:** Get attendance history for specified days

### 8. 🗑️ **Delete Student**
```http
DELETE /api/students/{student_name}
```

**Purpose:** Remove a student from the system

### 9. 🏥 **Health Check**
```http
GET /api/health
```

**Purpose:** Check API status and model availability

## 🎯 Key Differences: `/api/analyze` vs `/api/analyze`

| Feature | `/api/analyze` (Streaming) | `/api/analyze` (Single) |
|---------|---------------------------|---------------------------|
| **Purpose** | Real-time streaming | Single image processing |
| **Use Case** | Video feeds, live cameras | Photo uploads |
| **Response** | Masked face images | Recognition results only |
| **Privacy** | Faces are blurred | No face masking |
| **Attendance** | Auto-logged | Auto-logged |
| **Performance** | Optimized for speed | Standard processing |

## 🌐 Integration Examples

### JavaScript (Any Website)
```javascript
// Streaming integration
const formData = new FormData();
formData.append('file', videoFrameBlob);

const response = await fetch('https://web-production-13b09.up.railway.app/api/analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Recognized students:', result.results);
```

### Python Integration
```python
import requests

# Streaming frame analysis
def analyze_frame(image_path):
    url = "https://web-production-13b09.up.railway.app/api/analyze"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    return response.json()

# Usage
result = analyze_frame('camera_frame.jpg')
for face in result['results']:
    if face['name'] != 'Unknown':
        print(f"Recognized: {face['name']} ({face['confidence']*100:.1f}%)")
```

### cURL Examples
```bash
# Analyze streaming frame
curl -X POST "https://web-production-13b09.up.railway.app/api/analyze" \
  -F "file=@frame.jpg"

# Get students
curl "https://web-production-13b09.up.railway.app/api/students"

# Health check
curl "https://web-production-13b09.up.railway.app/api/health"
```

## 🔧 Technical Details

- **Model:** InsightFace Buffalo_L
- **Execution:** CPU-optimized for Railway
- **Confidence Threshold:** 60% (0.6)
- **CORS:** Enabled for all origins
- **Face Masking:** Gaussian blur for privacy
- **Attendance Logging:** Automatic CSV logging

## 🎥 Real-World Use Cases

1. **School Attendance Systems**
   - Live classroom monitoring
   - Automatic attendance marking
   - Real-time student recognition

2. **Office Check-in Systems**
   - Employee entry monitoring
   - Automatic time tracking
   - Security access control

3. **Event Management**
   - Guest check-in
   - VIP recognition
   - Attendance tracking

4. **Security Systems**
   - Access control
   - Visitor monitoring
   - Alert systems

## 🚀 Getting Started

1. **Test the API:** Use the streaming integration example
2. **Register students:** POST to `/api/register`
3. **Start streaming:** Send frames to `/api/analyze`
4. **Monitor results:** Check attendance via `/api/attendance/stats`

Your AI Upashthiti API is now ready for real-time streaming integration! 🎉