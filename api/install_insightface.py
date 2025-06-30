#!/usr/bin/env python3
"""
Script to properly install InsightFace with Buffalo model
"""

import subprocess
import sys
import os

def install_insightface():
    """Install InsightFace and download Buffalo model"""
    print("🔄 Installing InsightFace...")
    
    try:
        # Install InsightFace
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "insightface==0.7.3", "--no-cache-dir"
        ])
        print("✅ InsightFace installed successfully")
        
        # Set model path
        model_path = os.getenv('INSIGHTFACE_MODEL_PATH', '/root/.insightface/models')
        os.environ['INSIGHTFACE_HOME'] = os.path.dirname(model_path)
        os.makedirs(model_path, exist_ok=True)
        
        print(f"📂 Using model cache directory: {model_path}")
        
        # Test import and model loading
        print("🔄 Testing InsightFace and Buffalo model...")
        import insightface
        
        # Initialize model to download Buffalo weights
        model = insightface.app.FaceAnalysis(
            name='buffalo_l',
            root=model_path,
            providers=['CPUExecutionProvider']
        )
        model.prepare(ctx_id=-1)  # CPU mode
        
        print("✅ Buffalo model loaded successfully!")
        print("🎉 InsightFace setup complete!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install InsightFace: {e}")
        return False
    except ImportError as e:
        print(f"❌ Failed to import InsightFace: {e}")
        return False
    except Exception as e:
        print(f"❌ Error setting up InsightFace: {e}")
        return False

if __name__ == "__main__":
    success = install_insightface()
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you have Python 3.8+")
        print("2. Try: pip install --upgrade pip wheel setuptools")
        print("3. Install build tools: apt-get install build-essential cmake")
        sys.exit(1)
    else:
        print("\n🚀 Ready to run the API server!")