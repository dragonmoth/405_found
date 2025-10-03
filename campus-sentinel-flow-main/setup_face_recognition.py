"""
Facial Recognition Setup for Campus Sentinel
Set up face recognition for specific students: Mihika Patil and Vinayak Kundar
"""

import cv2
import os
import numpy as np
from PIL import Image
import shutil
import sqlite3

# Configuration
FACE_DATA_DIR = r"..\..\FaceRecognition-GUI-APP-master\data"
CLASSIFIERS_DIR = os.path.join(FACE_DATA_DIR, "classifiers")
HAARCASCADE_PATH = os.path.join(FACE_DATA_DIR, "haarcascade_frontalface_default.xml")

# Student information
STUDENTS = {
    "mihika": {
        "student_id": "23102069",
        "name": "Mihika Patil",
        "photo": "mihika.jpg"
    },
    "vinayak": {
        "student_id": "23101188", 
        "name": "Vinayak Kundar",
        "photo": "vinayak.jpeg"
    }
}

def setup_directories():
    """Create necessary directories for face training"""
    for student_key, student_info in STUDENTS.items():
        student_dir = os.path.join(FACE_DATA_DIR, student_key)
        os.makedirs(student_dir, exist_ok=True)
        print(f"✅ Created directory for {student_info['name']}: {student_dir}")

def extract_faces_from_photo(photo_path, student_key, student_name):
    """Extract faces from a single photo and create training dataset"""
    print(f"\n🔍 Processing photo for {student_name}...")
    
    if not os.path.exists(photo_path):
        print(f"❌ Photo not found: {photo_path}")
        return False
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)
    if face_cascade.empty():
        print(f"❌ Could not load face cascade from {HAARCASCADE_PATH}")
        return False
    
    # Read the image
    img = cv2.imread(photo_path)
    if img is None:
        print(f"❌ Could not read image: {photo_path}")
        return False
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        print(f"⚠️ No faces detected in {photo_path}")
        return False
    
    print(f"✅ Found {len(faces)} face(s) in {photo_path}")
    
    # Create training dataset directory
    student_dir = os.path.join(FACE_DATA_DIR, student_key)
    
    # Clear existing training data
    if os.path.exists(student_dir):
        shutil.rmtree(student_dir)
    os.makedirs(student_dir)
    
    # Extract and save faces with variations
    face_id = 1
    saved_faces = 0
    
    for (x, y, w, h) in faces:
        # Extract face region
        face = gray[y:y+h, x:x+w]
        
        # Resize to standard size
        face = cv2.resize(face, (200, 200))
        
        # Save original face
        face_path = os.path.join(student_dir, f"{face_id}_{student_key}.jpg")
        cv2.imwrite(face_path, face)
        saved_faces += 1
        face_id += 1
        
        # Create variations for better training
        variations = [
            ("bright", cv2.convertScaleAbs(face, alpha=1.2, beta=30)),
            ("dark", cv2.convertScaleAbs(face, alpha=0.8, beta=-30)),
            ("contrast", cv2.convertScaleAbs(face, alpha=1.5, beta=0)),
            ("blur", cv2.GaussianBlur(face, (3, 3), 0)),
            ("sharp", cv2.filter2D(face, -1, np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]))),
        ]
        
        for var_name, var_face in variations:
            if face_id <= 50:  # Limit to 50 total images
                var_path = os.path.join(student_dir, f"{face_id}_{student_key}_{var_name}.jpg")
                cv2.imwrite(var_path, var_face)
                saved_faces += 1
                face_id += 1
    
    print(f"✅ Saved {saved_faces} training images for {student_name}")
    return True

def train_face_recognizer(student_key, student_name):
    """Train LBPH face recognizer for a specific student"""
    print(f"\n🎯 Training face recognizer for {student_name}...")
    
    student_dir = os.path.join(FACE_DATA_DIR, student_key)
    
    # Check if training data exists
    if not os.path.exists(student_dir):
        print(f"❌ No training data found for {student_name}")
        return False
    
    # Get all image files
    image_files = [f for f in os.listdir(student_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(image_files) == 0:
        print(f"❌ No training images found for {student_name}")
        return False
    
    print(f"📚 Found {len(image_files)} training images")
    
    # Prepare training data
    faces = []
    labels = []
    
    for image_file in image_files:
        image_path = os.path.join(student_dir, image_file)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if img is not None:
            faces.append(img)
            labels.append(1)  # Use label 1 for all faces of this person
    
    if len(faces) == 0:
        print(f"❌ Could not load training images for {student_name}")
        return False
    
    # Create and train the recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    
    # Save the trained model
    classifier_path = os.path.join(CLASSIFIERS_DIR, f"{student_key}_classifier.xml")
    recognizer.save(classifier_path)
    
    print(f"✅ Face recognizer trained and saved: {classifier_path}")
    return True

def clear_old_classifiers():
    """Remove old classifiers except for our target students"""
    print("\n🧹 Cleaning old classifiers...")
    
    if not os.path.exists(CLASSIFIERS_DIR):
        os.makedirs(CLASSIFIERS_DIR)
        return
    
    target_classifiers = [f"{key}_classifier.xml" for key in STUDENTS.keys()]
    
    for file in os.listdir(CLASSIFIERS_DIR):
        if file.endswith("_classifier.xml") and file not in target_classifiers:
            file_path = os.path.join(CLASSIFIERS_DIR, file)
            os.remove(file_path)
            print(f"🗑️ Removed old classifier: {file}")

def update_database():
    """Update database with student information"""
    print("\n💾 Updating database...")
    
    try:
        # Connect to campus sentinel database
        db_path = os.path.join("backend", "campus_sentinel.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing students (optional - comment out if you want to keep others)
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM license_plates")
        
        # Add our target students
        for student_key, student_info in STUDENTS.items():
            student_id = student_info["student_id"]
            name = student_info["name"]
            email = f"{student_key}@college.edu"
            
            # Insert student
            cursor.execute('''
                INSERT OR REPLACE INTO students (student_id, name, email, face_trained, active)
                VALUES (?, ?, ?, 1, 1)
            ''', (student_id, name, email))
            
            print(f"✅ Added student to database: {name} ({student_id})")
        
        conn.commit()
        conn.close()
        print("✅ Database updated successfully")
        
    except Exception as e:
        print(f"❌ Database update error: {e}")

def test_face_recognition():
    """Test the trained face recognition system"""
    print("\n🧪 Testing face recognition system...")
    
    # Check if opencv-contrib-python is available
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        print("✅ OpenCV face module is available")
    except Exception as e:
        print(f"❌ OpenCV face module not available: {e}")
        print("💡 Install with: pip install --user opencv-contrib-python")
        return False
    
    # Check classifiers
    for student_key, student_info in STUDENTS.items():
        classifier_path = os.path.join(CLASSIFIERS_DIR, f"{student_key}_classifier.xml")
        if os.path.exists(classifier_path):
            print(f"✅ Classifier found for {student_info['name']}")
        else:
            print(f"❌ Classifier missing for {student_info['name']}")
    
    # Check face cascade
    if os.path.exists(HAARCASCADE_PATH):
        face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)
        if not face_cascade.empty():
            print("✅ Face cascade classifier loaded successfully")
        else:
            print("❌ Face cascade classifier failed to load")
    else:
        print(f"❌ Face cascade not found: {HAARCASCADE_PATH}")
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("  Campus Sentinel - Facial Recognition Setup")
    print("=" * 60)
    print(f"Setting up face recognition for:")
    for student_key, student_info in STUDENTS.items():
        print(f"  👤 {student_info['name']} (ID: {student_info['student_id']})")
    print()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Check for face module
        if hasattr(cv2, 'face'):
            print("✅ OpenCV face module available")
        else:
            print("❌ OpenCV face module not available")
            print("💡 Install with: pip install --user opencv-contrib-python")
            return
            
    except ImportError:
        print("❌ OpenCV not installed")
        print("💡 Install with: pip install opencv-python opencv-contrib-python")
        return
    
    # Setup directories
    setup_directories()
    
    # Clear old classifiers
    clear_old_classifiers()
    
    # Process each student
    for student_key, student_info in STUDENTS.items():
        photo_path = student_info["photo"]
        
        # Look for photo in current directory or common locations
        search_paths = [
            photo_path,
            os.path.join(".", photo_path),
            os.path.join("..", photo_path),
            os.path.join("campus-sentinel-flow-main", photo_path)
        ]
        
        photo_found = None
        for search_path in search_paths:
            if os.path.exists(search_path):
                photo_found = search_path
                break
        
        if photo_found:
            print(f"📸 Found photo: {photo_found}")
            if extract_faces_from_photo(photo_found, student_key, student_info["name"]):
                train_face_recognizer(student_key, student_info["name"])
            else:
                print(f"⚠️ Failed to process photo for {student_info['name']}")
        else:
            print(f"❌ Photo not found for {student_info['name']}: {photo_path}")
            print(f"   Searched in: {search_paths}")
            print(f"   Please place {photo_path} in the current directory")
    
    # Update database
    update_database()
    
    # Test the system
    test_face_recognition()
    
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Start the backend: cd backend && python app.py")
    print("2. Open frontend: http://localhost:5173/monitoring")
    print("3. Test face recognition with camera")
    print()
    print("Only Mihika Patil and Vinayak Kundar will be granted access!")

if __name__ == "__main__":
    main()