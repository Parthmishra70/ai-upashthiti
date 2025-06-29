# 🚀 Deploy Your AI Upashthiti API to Railway

## Step 1: Create Railway Account (2 minutes)

1. **Go to [Railway.app](https://railway.app)**
2. **Click "Login with GitHub"** (free account)
3. **Authorize Railway** to access your repositories

## Step 2: Deploy Your API (3 minutes)

1. **In Railway Dashboard:**
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose your **AI Upashthiti repository**

2. **Railway will automatically:**
   - ✅ Detect Python project
   - ✅ Install dependencies from `api/requirements.txt`
   - ✅ Start your API server
   - ✅ Give you a public URL

3. **Your API will be live at:**
   ```
   https://your-app-name.railway.app
   ```

## Step 3: Update Your Frontend

1. **Copy your Railway URL** (from Railway dashboard)

2. **Update your .env file:**
   ```bash
   # Replace with your actual Railway URL
   echo "VITE_API_URL=https://your-actual-app.railway.app" > .env
   ```

3. **Rebuild your frontend:**
   ```bash
   npm run build
   ```

## Step 4: Test Your Live API

Your API is now online! Test it:

```bash
# Test if API is live
curl https://your-app.railway.app/

# View interactive docs
# Visit: https://your-app.railway.app/docs
```

## 🎉 Success! Your API is Now Online

**Any website worldwide can now use your face recognition API:**

```javascript
// Example: Any website can integrate your API
const API_URL = 'https://your-app.railway.app';

// Register a student
const formData = new FormData();
formData.append('name', 'John Doe');
formData.append('file', imageFile);

const response = await fetch(`${API_URL}/api/register`, {
  method: 'POST',
  body: formData
});

// Recognize faces
const recognizeData = new FormData();
recognizeData.append('file', photoFile);

const result = await fetch(`${API_URL}/api/recognize`, {
  method: 'POST',
  body: recognizeData
});
```

## 🔗 Your Live API Endpoints

- **Main API:** `https://your-app.railway.app`
- **Interactive Docs:** `https://your-app.railway.app/docs`
- **Register Student:** `POST https://your-app.railway.app/api/register`
- **Recognize Faces:** `POST https://your-app.railway.app/api/recognize`
- **Get Students:** `GET https://your-app.railway.app/api/students`
- **Attendance Stats:** `GET https://your-app.railway.app/api/attendance/stats`

## 💡 Next Steps

1. **Share your API URL** with other developers
2. **Add your API to documentation** or marketplace
3. **Monitor usage** in Railway dashboard
4. **Scale up** if you get high traffic (Railway auto-scales)

Your face recognition system is now a **cloud service** that anyone can integrate! 🚀