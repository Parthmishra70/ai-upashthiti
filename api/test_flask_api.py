#!/usr/bin/env python3
"""
Test script for Flask API functionality
"""

import requests
import json
import os
from pathlib import Path

def test_api(base_url="http://localhost:5174"):
    """Test the Flask API endpoints"""
    
    print(f"🧪 Testing API at {base_url}")
    print("=" * 50)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        print("✅ Health check:", response.json())
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test detailed health
    try:
        response = requests.get(f"{base_url}/api/health")
        health = response.json()
        print("✅ Detailed health:", health)
        
        if not health.get("buffalo_model_loaded"):
            print("⚠️ Buffalo model not loaded - face recognition won't work")
    except Exception as e:
        print(f"❌ Detailed health check failed: {e}")
    
    # Test get students
    try:
        response = requests.get(f"{base_url}/api/students")
        students = response.json()
        print(f"✅ Students endpoint: {students['total']} students registered")
    except Exception as e:
        print(f"❌ Students endpoint failed: {e}")
    
    # Test get attendance
    try:
        response = requests.get(f"{base_url}/api/attendance")
        attendance = response.json()
        print(f"✅ Attendance endpoint: {attendance['total']} records")
    except Exception as e:
        print(f"❌ Attendance endpoint failed: {e}")
    
    print("\n🎉 Basic API tests completed!")
    return True

def test_with_image(base_url="http://localhost:5174"):
    """Test API with actual image if available"""
    
    # Look for test images
    test_image_paths = [
        "../test_images",
        "../registered_faces",
        "test_images",
        "registered_faces"
    ]
    
    test_image = None
    for path in test_image_paths:
        if os.path.exists(path):
            for file in Path(path).rglob("*.png"):
                test_image = file
                break
            for file in Path(path).rglob("*.jpg"):
                test_image = file
                break
            if test_image:
                break
    
    if test_image:
        print(f"\n🖼️ Testing with image: {test_image}")
        try:
            with open(test_image, 'rb') as f:
                files = {'frame': f}
                response = requests.post(f"{base_url}/api/analyze", files=files)
                result = response.json()
                print(f"✅ Image analysis: {result}")
        except Exception as e:
            print(f"❌ Image analysis failed: {e}")
    else:
        print("\nℹ️ No test images found for image analysis test")

if __name__ == "__main__":
    print("🤖 AI Upashthiti Flask API Test")
    print("=" * 40)
    
    # Test local API
    if test_api():
        test_with_image()
    
    print("\n💡 To test your deployed API:")
    print("python test_flask_api.py")
    print("# Or modify base_url to your Railway URL")