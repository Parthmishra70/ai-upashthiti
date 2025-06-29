# 🧪 API Testing Commands

## ❌ **WRONG - Local API (Not Running)**
```bash
# This will fail because no local server is running
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@photo.jpg"
```

## ✅ **CORRECT - Live Railway API**

### 1. Test Face Recognition
```bash
curl -X POST "https://web-production-13b09.up.railway.app/api/analyze" \
  -F "file=@photo.jpg"
```

### 2. Get Registered Students
```bash
curl "https://web-production-13b09.up.railway.app/api/students"
```

### 3. Health Check
```bash
curl "https://web-production-13b09.up.railway.app/api/health"
```

### 4. Get Attendance Stats
```bash
curl "https://web-production-13b09.up.railway.app/api/attendance/stats"
```

## 🌐 **JavaScript/Fetch Examples**

### Face Recognition
```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('https://web-production-13b09.up.railway.app/api/analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

### Get Students
```javascript
const response = await fetch('https://web-production-13b09.up.railway.app/api/students');
const students = await response.json();
console.log(students);
```

## 🐍 **Python Examples**

### Face Recognition
```python
import requests

url = "https://web-production-13b09.up.railway.app/api/analyze"

with open('photo.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    result = response.json()
    print(result)
```

### Get Students
```python
import requests

url = "https://web-production-13b09.up.railway.app/api/students"
response = requests.get(url)
students = response.json()
print(students)
```

## 📖 **Interactive API Documentation**
Visit: https://web-production-13b09.up.railway.app/docs

## 🎯 **Key Points**

1. **Your API is LIVE** at: `https://web-production-13b09.up.railway.app`
2. **No local server** is running on `localhost:8000`
3. **Use the Railway URL** for all API calls
4. **Buffalo model** is loaded and ready for face recognition
5. **2 students registered**: Pathak and Parth Mishra

## 🔧 **If You Want to Run Locally**

To run the API locally for development:

```bash
cd api
python main.py
```

Then you can use `http://localhost:8000` for testing.