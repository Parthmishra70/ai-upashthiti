# Deploy to Render (Alternative Free Option)

## Step 1: Create render.yaml

```yaml
services:
  - type: web
    name: ai-upashthiti-api
    env: python
    buildCommand: "cd api && pip install -r requirements.txt"
    startCommand: "cd api && python main.py"
    envVars:
      - key: PORT
        value: 8000
```

## Step 2: Deploy

1. **Sign up at Render.com**
2. **Connect GitHub repository**
3. **Deploy** - Get URL like: `https://your-app.onrender.com`

## Step 3: Update Frontend

```env
VITE_API_URL=https://your-app.onrender.com
```