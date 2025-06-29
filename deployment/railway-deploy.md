# Deploy to Railway (Recommended - Free & Easy)

Railway is perfect for your Python API - it's free, easy, and handles everything automatically.

## Step 1: Prepare Your Code

1. Create a `railway.toml` file:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd api && python main.py"

[env]
PORT = "8000"
```

2. Create a `Procfile`:
```
web: cd api && python main.py
```

## Step 2: Deploy to Railway

1. **Sign up at Railway.app** (free account)
2. **Connect your GitHub repository**
3. **Deploy automatically** - Railway will:
   - Install Python dependencies
   - Start your API server
   - Give you a public URL like: `https://your-app.railway.app`

## Step 3: Update Your Frontend

Update your `.env` file:
```env
VITE_API_URL=https://your-app.railway.app
```

## That's it! Your API is now online! 🚀

**Your API will be accessible at:**
- Main API: `https://your-app.railway.app`
- Docs: `https://your-app.railway.app/docs`

**Other websites can now use:**
```javascript
// Any website can now call your API
fetch('https://your-app.railway.app/api/analyze', {
  method: 'POST',
  body: formData
});
```