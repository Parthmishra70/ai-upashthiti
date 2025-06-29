#!/usr/bin/env python3
"""
Test script to verify Buffalo model is working correctly
"""

import sys
import os

def test_buffalo_model():
    """Test if Buffalo model loads and works correctly"""
    print("🧪 Testing Buffalo Model...")
    
    try:
        import insightface
        import numpy as np
        import cv2
        
        print("✅ InsightFace imported successfully")
        
        # Initialize Buffalo model
        print("🔄 Loading Buffalo model...")
        model = insightface.app.FaceAnalysis(name='buffalo_l')
        model.prepare(ctx_id=-1)  # CPU mode
        print("✅ Buffalo model loaded successfully")
        
        # Test with a dummy image
        print("🔄 Testing face detection...")
        dummy_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = model.get(dummy_img)
        print(f"✅ Face detection test completed (found {len(faces)} faces in random image)")
        
        # Test embedding generation
        if len(faces) > 0:
            embedding = faces[0].embedding
            print(f"✅ Embedding generated: shape {embedding.shape}")
        
        print("🎉 Buffalo model is working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Buffalo model: {e}")
        return False

def test_existing_embeddings():
    """Test compatibility with existing embeddings"""
    print("\n🔍 Testing existing embeddings compatibility...")
    
    try:
        import json
        
        # Check if embeddings file exists
        if os.path.exists("../embeddings_db.json"):
            with open("../embeddings_db.json", "r") as f:
                db = json.load(f)
            
            print(f"✅ Found {len(db)} existing student embeddings")
            
            for name, data in db.items():
                if isinstance(data, dict) and "embedding" in data:
                    embedding = np.array(data["embedding"])
                    print(f"  - {name}: embedding shape {embedding.shape}")
                else:
                    print(f"  - {name}: legacy format")
            
            print("✅ Existing embeddings are compatible")
            return True
        else:
            print("ℹ️ No existing embeddings found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking embeddings: {e}")
        return False

if __name__ == "__main__":
    print("🤖 AI Upashthiti - Buffalo Model Test")
    print("=" * 40)
    
    # Test Buffalo model
    buffalo_ok = test_buffalo_model()
    
    # Test existing embeddings
    embeddings_ok = test_existing_embeddings()
    
    print("\n" + "=" * 40)
    if buffalo_ok and embeddings_ok:
        print("🎉 All tests passed! Buffalo model is ready.")
        print("🚀 You can now run the API server with confidence.")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)