# AI Upashthiti - Face Recognition Attendance System

A comprehensive face recognition attendance system with web API and dashboard interface.

## 🚀 **LIVE API DEPLOYMENT**

**Your AI Upashthiti API is now live at:**
```
https://web-production-13b09.up.railway.app
```

**Interactive API Documentation:**
```
https://web-production-13b09.up.railway.app/docs
```

## Features

### 🎯 Core Functionality
- **Face Registration**: Register students with their photos using Buffalo model
- **Real-time Recognition**: Recognize faces from uploaded images with 60% confidence threshold
- **Attendance Tracking**: Automatic attendance logging with timestamps
- **Student Management**: Add, view, and remove registered students

### 📊 Analytics & Reporting
- **Live Dashboard**: Real-time attendance statistics
- **Attendance History**: 14-day trend analysis with charts
- **Daily Reports**: Detailed daily attendance records
- **Performance Metrics**: Confidence scores and recognition accuracy

### 🔌 API Integration
- **RESTful API**: Complete API for third-party integration
- **Multiple Endpoints**: Registration, recognition, and data retrieval
- **CORS Enabled**: Ready for cross-origin requests
- **JSON Responses**: Structured data format

## Quick Start

### Prerequisites
- Node.js 16+ (for web dashboard)
- Your API is already live on Railway!

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-upashthiti
   ```

2. **Set up Web Dashboard**
   ```bash
   npm install
   npm run dev
   ```
   The dashboard will start on `http://localhost:3000` and connect to your live API

## API Documentation

### Base URL
```
https://web-production-13b09.up.railway.app
```

### Endpoints

#### 1. Register Student
```http
POST /api/register
Content-Type: multipart/form-data

Parameters:
- name (string): Student name
- file (file): Student photo
- student_id (string, optional): Student ID
```

#### 2. Recognize Faces
```http
POST /api/recognize
Content-Type: multipart/form-data

Parameters:
- file (file): Image containing faces to recognize
```

#### 3. Get Students
```http
GET /api/students
```

#### 4. Delete Student
```http
DELETE /api/students/{student_name}
```

#### 5. Get Attendance Stats
```http
GET /api/attendance/stats
```

#### 6. Get Today's Attendance
```http
GET /api/attendance/today
```

#### 7. Get Attendance History
```http
GET /api/attendance/history?days=7
```

## Usage Examples

### JavaScript/React Integration
```javascript
// Register a student
const registerStudent = async (name, imageFile, studentId) => {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('file', imageFile);
  if (studentId) formData.append('student_id', studentId);
  
  const response = await fetch('https://web-production-13b09.up.railway.app/api/register', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Recognize faces
const recognizeFaces = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('https://web-production-13b09.up.railway.app/api/recognize', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};
```

### Python Integration
```python
import requests

# Register student
def register_student(name, image_path, student_id=None):
    url = "https://web-production-13b09.up.railway.app/api/register"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'name': name}
        if student_id:
            data['student_id'] = student_id
            
        response = requests.post(url, files=files, data=data)
    
    return response.json()

# Recognize faces
def recognize_faces(image_path):
    url = "https://web-production-13b09.up.railway.app/api/recognize"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    return response.json()
```

### cURL Examples
```bash
# Register a student
curl -X POST "https://web-production-13b09.up.railway.app/api/register" \
  -F "name=John Doe" \
  -F "file=@photo.jpg"

# Recognize faces
curl -X POST "https://web-production-13b09.up.railway.app/api/recognize" \
  -F "file=@group_photo.jpg"

# Get all students
curl "https://web-production-13b09.up.railway.app/api/students"

# Get attendance stats
curl "https://web-production-13b09.up.railway.app/api/attendance/stats"
```

## Configuration

### Environment Variables
Your project is now configured to use the live API:
```env
VITE_API_URL=https://web-production-13b09.up.railway.app
```

## File Structure
```
ai-upashthiti/
├── src/                   # React frontend (connects to live API)
│   ├── components/        # React components
│   ├── services/         # API service functions
│   └── App.tsx           # Main application
├── api-integration-examples.html  # Live API examples
├── .env                  # Environment configuration
└── package.json          # Node.js dependencies
```

## Technical Details

### Face Recognition
- **Model**: InsightFace Buffalo_L (deployed on Railway)
- **Embedding Size**: 512 dimensions
- **Similarity Threshold**: 0.6 (configurable)
- **Detection**: RetinaFace for face detection

### Database
- **Embeddings**: JSON file storage on Railway
- **Attendance**: CSV format with timestamps
- **Persistent**: Data persists across deployments

### Security
- **CORS**: Enabled for all origins
- **File Validation**: Image format validation
- **Error Handling**: Comprehensive error responses

## 🎉 Your API is Live!

**Test your live API now:**

1. **Open the integration examples:** `api-integration-examples.html`
2. **View API documentation:** https://web-production-13b09.up.railway.app/docs
3. **Test endpoints directly:** Use the examples above

**Your face recognition system is now:**
- ✅ **Live on the internet**
- ✅ **Using Buffalo model for accurate recognition**
- ✅ **Ready for integration by any website**
- ✅ **Scalable and production-ready**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the documentation
2. Test with the live API examples
3. Search existing issues
4. Create a new issue with detailed information

---

**AI Upashthiti** - Making attendance tracking intelligent and effortless! 🚀

**Live API:** https://web-production-13b09.up.railway.app