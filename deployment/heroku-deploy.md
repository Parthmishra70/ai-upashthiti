# Deploy to Heroku

## Step 1: Create Heroku Files

Create `Procfile`:
```
web: cd api && python main.py
```

Create `runtime.txt`:
```
python-3.9.18
```

## Step 2: Deploy

```bash
# Install Heroku CLI
# Then:
heroku create your-app-name
git push heroku main
```

## Step 3: Get Your URL

Your API will be at: `https://your-app-name.herokuapp.com`