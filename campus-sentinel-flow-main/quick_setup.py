"""
Quick setup script to get the system running
"""

import sqlite3
import os

def setup_basic_system():
    """Setup basic system with authorized students"""
    print("🔧 Quick Setup - Campus Sentinel")
    print("=" * 40)
    
    db_path = "backend/campus_sentinel.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                face_trained BOOLEAN DEFAULT FALSE,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license_plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                plate_number TEXT NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detection_type TEXT NOT NULL,
                detected_value TEXT,
                student_id TEXT,
                student_name TEXT,
                status TEXT NOT NULL,
                confidence REAL,
                image_path TEXT
            )
        ''')
        
        # Clear existing data
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM license_plates")
        
        # Add authorized students for face recognition
        authorized_students = [
            ('23102069', 'Mihika Patil', 'mihika@college.edu', 1),  # face_trained = 1
            ('23101188', 'Vinayak Kundar', 'vinayak@college.edu', 1),  # face_trained = 1
        ]
        
        cursor.executemany('''
            INSERT INTO students (student_id, name, email, face_trained, active)
            VALUES (?, ?, ?, ?, 1)
        ''', authorized_students)
        
        # Add some sample students for regular access
        sample_students = [
            ('23102824', 'Ankit Ayaan Patel', 'ankit@college.edu', 0),
            ('23107924', 'Avni Divya Mehta', 'avni@college.edu', 0),
            ('23104150', 'Vivaan Shah', 'vivaan@college.edu', 0),
            ('23106155', 'Sanjay Mishra', 'sanjay@college.edu', 0),
            ('23103621', 'Swati Myra Nair', 'swati@college.edu', 0),
        ]
        
        cursor.executemany('''
            INSERT INTO students (student_id, name, email, face_trained, active)
            VALUES (?, ?, ?, ?, 1)
        ''', sample_students)
        
        # Add some sample license plates
        sample_plates = [
            ('23102069', 'MH-12-AB-1234'),  # Mihika's plate
            ('23101188', 'DL-01-XY-5678'),  # Vinayak's plate
            ('23102824', 'KA-05-CD-9012'),  # Ankit's plate
        ]
        
        cursor.executemany('''
            INSERT INTO license_plates (student_id, plate_number, active)
            VALUES (?, ?, 1)
        ''', sample_plates)
        
        conn.commit()
        conn.close()
        
        print("✅ Database setup complete!")
        print(f"✅ Added 2 authorized students for face recognition:")
        print(f"   - Mihika Patil (23102069)")
        print(f"   - Vinayak Kundar (23101188)")
        print(f"✅ Added 5 regular students")
        print(f"✅ Added 3 license plates")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def check_opencv():
    """Check if OpenCV is properly installed"""
    print(f"\n🔍 Checking OpenCV installation...")
    
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        if hasattr(cv2, 'face'):
            print(f"✅ OpenCV face module available")
            return True
        else:
            print(f"❌ OpenCV face module not available")
            print(f"💡 Install with: pip install --user opencv-contrib-python")
            return False
            
    except ImportError:
        print(f"❌ OpenCV not installed")
        print(f"💡 Install with: pip install opencv-python opencv-contrib-python")
        return False

def check_camera():
    """Check if camera is accessible"""
    print(f"\n📷 Testing camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"✅ Camera is working")
            return True
        else:
            print(f"❌ Camera not accessible")
            print(f"💡 Make sure no other app is using the camera")
            return False
            
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def start_backend():
    """Instructions to start backend"""
    print(f"\n🚀 Starting Backend...")
    print(f"   cd backend")
    print(f"   python app.py")

def main():
    """Main setup function"""
    print("🏫 Campus Sentinel - Quick Setup")
    print("=" * 50)
    
    # Setup database
    if setup_basic_system():
        
        # Check dependencies
        opencv_ok = check_opencv()
        camera_ok = check_camera()
        
        print(f"\n📋 Setup Summary:")
        print(f"✅ Database: Ready")
        print(f"{'✅' if opencv_ok else '❌'} OpenCV: {'Ready' if opencv_ok else 'Needs Installation'}")
        print(f"{'✅' if camera_ok else '❌'} Camera: {'Ready' if camera_ok else 'Check Connection'}")
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Start Backend:")
        print(f"   cd backend")
        print(f"   python app.py")
        print(f"")
        print(f"2. Open Frontend:")
        print(f"   http://localhost:5173/monitoring")
        print(f"")
        print(f"3. Start Camera & Detection:")
        print(f"   Click 'Start Camera' then 'Start Detection'")
        print(f"")
        print(f"4. Test the System:")
        print(f"   - License plates will be detected and logged")
        print(f"   - Faces will show as 'Unrecognized' (since no training photos)")
        print(f"   - Student ID simulation runs automatically")
        print(f"   - Check Admin Dashboard for real-time logs")
        
        if not opencv_ok:
            print(f"\n⚠️  Face recognition won't work until OpenCV face module is installed!")
            
    else:
        print(f"\n❌ Setup failed - please check database permissions")

if __name__ == "__main__":
    main()