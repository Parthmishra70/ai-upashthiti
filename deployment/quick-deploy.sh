#!/bin/bash

echo "🚀 AI Upashthiti - Quick Cloud Deployment"
echo "========================================="

echo "Choose your deployment platform:"
echo "1. Railway (Recommended - Free & Easy)"
echo "2. Render (Free alternative)"
echo "3. Heroku (Paid but reliable)"
echo "4. DigitalOcean (Advanced)"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚂 Setting up Railway deployment..."
        
        # Create railway.toml
        cat > railway.toml << EOF
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd api && python main.py"

[env]
PORT = "8000"
EOF
        
        # Create Procfile
        echo "web: cd api && python main.py" > Procfile
        
        echo "✅ Railway files created!"
        echo "📝 Next steps:"
        echo "1. Go to https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Create new project from GitHub repo"
        echo "4. Your API will be live at: https://your-app.railway.app"
        ;;
        
    2)
        echo "🎨 Setting up Render deployment..."
        
        # Create render.yaml
        cat > render.yaml << EOF
services:
  - type: web
    name: ai-upashthiti-api
    env: python
    buildCommand: "cd api && pip install -r requirements.txt"
    startCommand: "cd api && python main.py"
    envVars:
      - key: PORT
        value: 8000
EOF
        
        echo "✅ Render files created!"
        echo "📝 Next steps:"
        echo "1. Go to https://render.com"
        echo "2. Sign up with GitHub"
        echo "3. Create new Web Service from GitHub repo"
        echo "4. Your API will be live at: https://your-app.onrender.com"
        ;;
        
    3)
        echo "🟣 Setting up Heroku deployment..."
        
        # Create Procfile
        echo "web: cd api && python main.py" > Procfile
        
        # Create runtime.txt
        echo "python-3.9.18" > runtime.txt
        
        echo "✅ Heroku files created!"
        echo "📝 Next steps:"
        echo "1. Install Heroku CLI"
        echo "2. Run: heroku create your-app-name"
        echo "3. Run: git push heroku main"
        echo "4. Your API will be live at: https://your-app-name.herokuapp.com"
        ;;
        
    4)
        echo "🌊 DigitalOcean App Platform setup..."
        
        # Create .do/app.yaml
        mkdir -p .do
        cat > .do/app.yaml << EOF
name: ai-upashthiti-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: cd api && python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
EOF
        
        echo "✅ DigitalOcean files created!"
        echo "📝 Next steps:"
        echo "1. Go to https://cloud.digitalocean.com/apps"
        echo "2. Create new app from GitHub repo"
        echo "3. Your API will be live with custom domain"
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🔧 Don't forget to update your frontend .env file:"
echo "VITE_API_URL=https://your-deployed-api-url"
echo ""
echo "🌐 Once deployed, any website can use your API!"