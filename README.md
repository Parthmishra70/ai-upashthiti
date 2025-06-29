# AI Upashthiti - Face Recognition Attendance System

A comprehensive face recognition attendance system with web API and dashboard interface.

## Features

### 🎯 Core Functionality
- **Face Registration**: Register students with their photos
- **Real-time Recognition**: Recognize faces from uploaded images
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
- Python 3.8+
- Node.js 16+
- Webcam or image files for testing

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-upashthiti
   ```

2. **Set up Python API**
   ```bash
   cd api
   pip install -r requirements.txt
   python main.py
   ```
   The API will start on `http://localhost:8000`

3. **Set up Web Dashboard**
   ```bash
   npm install
   npm run dev
   ```
   The dashboard will start on `http://localhost:3000`

## API Documentation

### Base URL
```
http://localhost:8000
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
  
  const response = await fetch('http://localhost:8000/api/register', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Recognize faces
const recognizeFaces = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('http://localhost:8000/api/recognize', {
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
    url = "http://localhost:8000/api/register"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'name': name}
        if student_id:
            data['student_id'] = student_id
            
        response = requests.post(url, files=files, data=data)
    
    return response.json()

# Recognize faces
def recognize_faces(image_path):
    url = "http://localhost:8000/api/recognize"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    return response.json()
```

## Deployment

### API Deployment (Python)
1. **Using Docker**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY api/requirements.txt .
   RUN pip install -r requirements.txt
   COPY api/ .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Using Cloud Platforms**
   - Deploy to Heroku, Railway, or DigitalOcean
   - Set environment variables as needed
   - Ensure sufficient memory for face recognition models

### Web Dashboard Deployment
1. **Build for production**
   ```bash
   npm run build
   ```

2. **Deploy to Netlify/Vercel**
   - Connect your repository
   - Set build command: `npm run build`
   - Set publish directory: `dist`
   - Add environment variable: `VITE_API_URL=your-api-url`

## Configuration

### Environment Variables
Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

For production:
```env
VITE_API_URL=https://your-api-domain.com
```

## File Structure
```
ai-upashthiti/
├── api/                    # Python FastAPI backend
│   ├── main.py            # Main API application
│   └── requirements.txt   # Python dependencies
├── src/                   # React frontend
│   ├── components/        # React components
│   ├── services/         # API service functions
│   └── App.tsx           # Main application
├── registered_faces/      # Student photos storage
├── test_images/          # Test images
├── embeddings_db.json    # Face embeddings database
├── attendance.csv        # Attendance records
└── package.json          # Node.js dependencies
```

## Technical Details

### Face Recognition
- **Model**: InsightFace Buffalo_L
- **Embedding Size**: 512 dimensions
- **Similarity Threshold**: 0.6 (configurable)
- **Detection**: RetinaFace for face detection

### Database
- **Embeddings**: JSON file storage (easily replaceable with SQL/NoSQL)
- **Attendance**: CSV format with timestamps
- **Scalable**: Can be migrated to PostgreSQL/MongoDB

### Security
- **CORS**: Configurable origins
- **File Validation**: Image format validation
- **Error Handling**: Comprehensive error responses

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
2. Search existing issues
3. Create a new issue with detailed information

---

**AI Upashthiti** - Making attendance tracking intelligent and effortless! 🚀