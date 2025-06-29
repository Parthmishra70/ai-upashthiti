#!/usr/bin/env python3
"""
Create train folder structure for face registration
"""

import os
import shutil
from pathlib import Path

def create_train_structure():
    """Create train folder with sample structure"""
    
    # Create train directory
    train_dir = Path("train")
    train_dir.mkdir(exist_ok=True)
    
    print("📁 Created 'train' directory structure:")
    print("train/")
    print("├── person1/")
    print("│   ├── photo1.jpg")
    print("│   └── photo2.jpg")
    print("├── person2/")
    print("│   └── photo1.jpg")
    print("└── ...")
    
    # Create sample person directories
    sample_persons = ["Pathak", "Parth Mishra"]
    
    for person in sample_persons:
        person_dir = train_dir / person
        person_dir.mkdir(exist_ok=True)
        
        # Create a README file in each person's directory
        readme_file = person_dir / "README.txt"
        with open(readme_file, "w") as f:
            f.write(f"Place photos of {person} in this folder.\n")
            f.write("Supported formats: .jpg, .jpeg, .png\n")
            f.write("Multiple photos will be averaged for better accuracy.\n")
    
    # Copy existing registered faces if they exist
    registered_faces_dir = Path("../registered_faces")
    if registered_faces_dir.exists():
        print("\n🔄 Copying existing registered faces...")
        for person_dir in registered_faces_dir.iterdir():
            if person_dir.is_dir():
                dest_dir = train_dir / person_dir.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(person_dir, dest_dir)
                print(f"  ✅ Copied {person_dir.name}")
    
    print(f"\n✅ Train folder structure created!")
    print(f"📍 Location: {train_dir.absolute()}")
    print("\n📝 Next steps:")
    print("1. Add photos to each person's folder")
    print("2. Call POST /api/register to process all photos")
    print("3. Use POST /api/analyze to recognize faces")

if __name__ == "__main__":
    create_train_structure()