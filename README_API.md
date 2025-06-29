# AI Upashthiti API - Setup and Deployment Guide

## Quick Start Options

### Option 1: Simple Python Run (Recommended for Development)

1. **Install Python 3.8+** (if not already installed)
2. **Run the setup script:**
   ```bash
   python run_api.py
   ```

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```

### Option 3: Using Shell Script (Linux/Mac)

```bash
chmod +x api/start_server.sh
./api/start_server.sh
```

### Option 4: Using Batch File (Windows)

Double-click `start_api.bat` or run:
```cmd
start_api.bat
```

### Option 5: Docker (Production Ready)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual containers
docker build -f Dockerfile.api -t ai-upashthiti-api .
docker run -p 8000:8000 ai-upashthiti-api
```

## API Endpoints

Once running, your API will be available at `http://localhost:8000`

### Core Endpoints:

- **POST /api/register** - Register a new student
- **POST /api/analyze** - Recognize faces in an image
- **GET /api/students** - Get all registered students
- **DELETE /api/students/{name}** - Delete a student
- **GET /api/attendance/stats** - Get attendance statistics
- **GET /api/attendance/today** - Get today's attendance
- **GET /api/attendance/history** - Get attendance history

### Interactive Documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Integration Examples

### JavaScript/Fetch
```javascript
// Register a student
const formData = new FormData();
formData.append('name', 'John Doe');
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/api/register', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

### Python/Requests
```python
import requests

# Recognize faces
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files={'file': f}
    )
    
result = response.json()
```

### cURL
```bash
# Register student
curl -X POST "http://localhost:8000/api/register" \
  -F "name=John Doe" \
  -F "file=@photo.jpg"

# Recognize faces
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@group_photo.jpg"
```

## Deployment Options

### 1. Local Development
- Use `python run_api.py` for quick setup
- API runs on http://localhost:8000

### 2. Cloud Deployment

#### Heroku
```bash
# Create Procfile
echo "web: cd api && python main.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### Railway
```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd api && python main.py"
  }
}
```

#### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: ai-upashthiti-api
services:
- name: api
  source_dir: /api
  github:
    repo: your-username/your-repo
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
```

### 3. Docker Production
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

Create a `.env` file in the API directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Face Recognition Settings
CONFIDENCE_THRESHOLD=0.6
MAX_FILE_SIZE=10485760  # 10MB

# Database (if using external DB)
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## Troubleshooting

### Common Issues:

1. **Import Error: No module named 'insightface'**
   ```bash
   pip install insightface
   ```

2. **OpenCV Error**
   ```bash
   pip install opencv-python-headless
   ```

3. **Permission Denied**
   ```bash
   chmod +x api/start_server.sh
   ```

4. **Port Already in Use**
   - Change port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`

### Performance Tips:

1. **Use GPU acceleration** (if available):
   ```python
   # In main.py, change ctx_id
   model.prepare(ctx_id=0)  # GPU
   model.prepare(ctx_id=-1) # CPU
   ```

2. **Optimize for production**:
   - Use gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
   - Enable caching for embeddings
   - Use a proper database (PostgreSQL/MongoDB)

## API Security

For production deployment, consider:

1. **Add authentication**:
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **Rate limiting**:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

3. **HTTPS only**:
   ```python
   app.add_middleware(HTTPSRedirectMiddleware)
   ```

## Monitoring

Add health checks and monitoring:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

Your API is now ready to be integrated into any application! 🚀