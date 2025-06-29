// Update your frontend to use the deployed API

// 1. Create .env.production file
const envProduction = `
# Production API URL (replace with your actual deployed URL)
VITE_API_URL=https://your-app.railway.app

# For Railway deployment
# VITE_API_URL=https://your-app.railway.app

# For Render deployment  
# VITE_API_URL=https://your-app.onrender.com

# For Heroku deployment
# VITE_API_URL=https://your-app-name.herokuapp.com
`;

// 2. Example of how other websites will use your API
const exampleUsage = `
// Any website can now integrate your face recognition API

// Register a student
async function registerStudent(name, imageFile, studentId) {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('file', imageFile);
  if (studentId) formData.append('student_id', studentId);
  
  const response = await fetch('https://your-app.railway.app/api/register', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}

// Recognize faces
async function recognizeFaces(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('https://your-app.railway.app/api/analyze', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}

// Get attendance stats
async function getAttendanceStats() {
  const response = await fetch('https://your-app.railway.app/api/attendance/stats');
  return response.json();
}

// Example integration in any HTML page
const htmlExample = \`
<!DOCTYPE html>
<html>
<head>
    <title>Face Recognition Integration</title>
</head>
<body>
    <h1>Face Recognition System</h1>
    
    <div>
        <h2>Register Student</h2>
        <input type="text" id="studentName" placeholder="Student Name">
        <input type="file" id="studentPhoto" accept="image/*">
        <button onclick="registerNewStudent()">Register</button>
    </div>
    
    <div>
        <h2>Recognize Faces</h2>
        <input type="file" id="recognizePhoto" accept="image/*">
        <button onclick="recognizePhoto()">Recognize</button>
        <div id="results"></div>
    </div>
    
    <script>
        const API_URL = 'https://your-app.railway.app';
        
        async function registerNewStudent() {
            const name = document.getElementById('studentName').value;
            const file = document.getElementById('studentPhoto').files[0];
            
            if (!name || !file) {
                alert('Please provide name and photo');
                return;
            }
            
            const formData = new FormData();
            formData.append('name', name);
            formData.append('file', file);
            
            try {
                const response = await fetch(\`\${API_URL}/api/register\`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                alert(\`Student registered: \${result.message}\`);
            } catch (error) {
                alert(\`Error: \${error.message}\`);
            }
        }
        
        async function recognizePhoto() {
            const file = document.getElementById('recognizePhoto').files[0];
            
            if (!file) {
                alert('Please select a photo');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch(\`\${API_URL}/api/analyze\`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = \`
                    <h3>Recognition Results:</h3>
                    <p>Faces detected: \${result.total_faces_detected}</p>
                    <p>Recognized: \${result.recognized_faces.length}</p>
                    <ul>
                        \${result.recognized_faces.map(face => 
                            \`<li>\${face.name} (Confidence: \${(face.confidence * 100).toFixed(1)}%)</li>\`
                        ).join('')}
                    </ul>
                \`;
            } catch (error) {
                alert(\`Error: \${error.message}\`);
            }
        }
    </script>
</body>
</html>
\`;
`;

console.log('Frontend integration examples created!');