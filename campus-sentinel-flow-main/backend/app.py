from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import json
import sqlite3
import os
import sys
import threading
import time
import csv
from datetime import datetime
import subprocess
import tempfile
import base64
import numpy as np
import csv
from PIL import Image
import io

# Add the modules to Python path
sys.path.append('../../FaceRecognition-GUI-APP-master')
sys.path.append('../../openalpr_64/python')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'campus_sentinel_secret_key'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
camera = None
camera_active = False
detection_active = False

# Paths - Use absolute paths to avoid issues with working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPENALPR_PATH = os.path.join(BASE_DIR, "openalpr_64", "alpr.exe")
FACE_CASCADE_PATH = os.path.join(BASE_DIR, "FaceRecognition-GUI-APP-master", "data", "haarcascade_frontalface_default.xml")
CLASSIFIERS_PATH = os.path.join(BASE_DIR, "FaceRecognition-GUI-APP-master", "data", "classifiers")

# Database setup
def init_db():
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    
    # Students table
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
    
    # License plates table
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
    
    # Access logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detection_type TEXT NOT NULL,  -- 'license_plate', 'face', 'student_id'
            detected_value TEXT,
            student_id TEXT,
            student_name TEXT,
            status TEXT NOT NULL,  -- 'granted', 'denied'
            confidence REAL,
            image_path TEXT
        )
    ''')
    
    # Add sample data
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ('STU-2025-001', 'Rohan Sharma', 'rohan@example.com'),
            ('STU-2025-042', 'Priya Verma', 'priya@example.com'),
            ('STU-2025-103', 'Amit Kumar', 'amit@example.com')
        ]
        cursor.executemany('INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)', sample_students)
        
        sample_plates = [
            ('STU-2025-001', 'MH-12-AB-1234'),
            ('STU-2025-042', 'DL-01-XY-5678'),
            ('STU-2025-103', 'KA-05-CD-9012')
        ]
        cursor.executemany('INSERT INTO license_plates (student_id, plate_number) VALUES (?, ?)', sample_plates)
    
    conn.commit()
    conn.close()

# License plate detection with improved accuracy and logging
def detect_license_plate(frame):
    try:
        print("🔍 Starting license plate detection...")
        
        # Use unique temporary file name to avoid Windows file conflicts
        import uuid
        temp_filename = f"plate_detection_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        # Enhance image for better OCR
        enhanced_frame = enhance_image_for_ocr(frame)
        cv2.imwrite(temp_path, enhanced_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"📸 Enhanced image saved to: {temp_path}")
        
        # Check if OpenALPR executable exists
        if not os.path.exists(OPENALPR_PATH):
            print(f"❌ OpenALPR not found at: {OPENALPR_PATH}")
            return None, 0
        
        print(f"✅ OpenALPR found at: {OPENALPR_PATH}")
        
        # Prepare OpenALPR command
        config_path = os.path.join(os.path.dirname(OPENALPR_PATH), "openalpr.conf")
        cmd = [
            OPENALPR_PATH, 
            "-j",  # JSON output
            "-n", "10",  # Return top 10 results
            "-c", "us",  # US region
            "--config", config_path,
            temp_path
        ]
        
        print(f"🔧 Running OpenALPR command: {' '.join(cmd)}")
            
        # Run OpenALPR with enhanced parameters
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        print(f"📋 OpenALPR return code: {result.returncode}")
        print(f"📋 OpenALPR stdout length: {len(result.stdout) if result.stdout else 0}")
        
        # Clean up temp file immediately
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"🗑️ Cleaned up temp file: {temp_path}")
        except Exception as cleanup_error:
            print(f"⚠️ Temp file cleanup warning: {cleanup_error}")
            
        if result.stdout:
            try:
                results = json.loads(result.stdout)
                print(f"📊 OpenALPR raw results: {results}")
                
                if results and "results" in results:
                    all_detections = []
                    
                    # Process all detected plates, not just the first one
                    for plate_result in results["results"]:
                        if "candidates" in plate_result:
                            for candidate in plate_result["candidates"]:
                                plate_number = candidate.get("plate", "").upper().strip()
                                confidence = float(candidate.get("confidence", 0))
                                
                                # Log ALL detections regardless of confidence
                                if plate_number:
                                    print(f"🎯 Detected plate candidate: '{plate_number}' (confidence: {confidence:.1f}%)")
                                    all_detections.append((plate_number, confidence))
                                    
                                    # Log to database even with low confidence
                                    log_plate_detection(plate_number, confidence)
                    
                    if all_detections:
                        # Return the best detection above minimum threshold
                        best_detection = None
                        best_confidence = 0
                        
                        for plate, conf in all_detections:
                            if conf > best_confidence and conf >= 65:  # Lowered threshold
                                best_detection = plate
                                best_confidence = conf
                        
                        if best_detection:
                            print(f"✅ Best plate detection: '{best_detection}' (confidence: {best_confidence:.1f}%)")
                            return best_detection, best_confidence
                        else:
                            # Return the highest confidence detection even if below threshold
                            best_plate, best_conf = max(all_detections, key=lambda x: x[1])
                            print(f"⚠️ Low confidence detection: '{best_plate}' (confidence: {best_conf:.1f}%)")
                            return best_plate, best_conf
                    else:
                        print("🔍 OpenALPR processed image but found no license plate candidates")
                else:
                    print("🔍 OpenALPR returned empty results")
                        
            except json.JSONDecodeError as e:
                print(f"❌ License plate detection JSON error: {e}")
                print(f"Raw stdout: {result.stdout}")
                
        else:
            print("❌ No stdout from OpenALPR")
                
        # Log stderr for debugging
        if result.stderr:
            print(f"⚠️ OpenALPR stderr: {result.stderr}")
            
        print("🔍 License plate detection completed - no plates found")
                        
    except subprocess.TimeoutExpired:
        print("⏱️ License plate detection timeout")
        # Clean up temp file on timeout
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except:
            pass
    except Exception as e:
        print(f"❌ License plate detection error: {e}")
        import traceback
        traceback.print_exc()
        # Clean up temp file on error
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except:
            pass
    
    return None, 0

# Image enhancement for better OCR
def enhance_image_for_ocr(frame):
    """Enhance image quality for better license plate recognition"""
    try:
        print("🎨 Enhancing image for OCR...")
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        print("✅ Applied CLAHE contrast enhancement")
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        print("✅ Applied Gaussian blur for noise reduction")
        
        # Apply sharpening kernel
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        print("✅ Applied sharpening filter")
        
        # Additional enhancement: Morphological operations to clean up
        kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morphed = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel_morph)
        
        # Convert back to BGR for consistency
        enhanced_bgr = cv2.cvtColor(morphed, cv2.COLOR_GRAY2BGR)
        print("✅ Image enhancement completed")
        
        return enhanced_bgr
        
    except Exception as e:
        print(f"❌ Image enhancement error: {e}")
        return frame  # Return original frame if enhancement fails

# Log all plate detections to database
def log_plate_detection(plate_number, confidence):
    """Log plate detection to database for analysis"""
    try:
        conn = sqlite3.connect('campus_sentinel.db')
        cursor = conn.cursor()
        
        # Create plate_detections table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plate_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plate_number TEXT NOT NULL,
                confidence REAL NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Insert detection
        cursor.execute('''
            INSERT INTO plate_detections (plate_number, confidence)
            VALUES (?, ?)
        ''', (plate_number, confidence))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error logging plate detection: {e}")

# Face recognition with improved error handling
def detect_face(frame):
    try:
        # Check if cascade classifier exists
        if not os.path.exists(FACE_CASCADE_PATH):
            print(f"Face cascade not found at: {FACE_CASCADE_PATH}")
            return None, 0, None
            
        face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
        if face_cascade.empty():
            print("Failed to load face cascade classifier")
            return None, 0, None
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            print(f"Detected {len(faces)} face(s)")
            
            # Check for trained classifiers
            if not os.path.exists(CLASSIFIERS_PATH):
                print(f"Classifiers directory not found: {CLASSIFIERS_PATH}")
                return None, 0, faces[0]  # Return face coords even if no classifiers
                
            classifier_files = [f for f in os.listdir(CLASSIFIERS_PATH) if f.endswith('_classifier.xml')]
            
            if not classifier_files:
                print("No trained face classifiers found")
                return None, 0, faces[0]  # Return face coords even if no classifiers
            
            # Try face recognition with opencv-contrib-python
            try:
                for classifier_file in classifier_files:
                    name = classifier_file.replace('_classifier.xml', '')
                    try:
                        # Use LBPHFaceRecognizer from opencv-contrib
                        if hasattr(cv2, 'face'):
                            recognizer = cv2.face.LBPHFaceRecognizer_create()
                        else:
                            print("OpenCV face module not available - install opencv-contrib-python")
                            return None, 0, faces[0]
                            
                        classifier_path = os.path.join(CLASSIFIERS_PATH, classifier_file)
                        recognizer.read(classifier_path)
                        
                        for (x, y, w, h) in faces:
                            roi_gray = gray[y:y+h, x:x+w]
                            id, confidence = recognizer.predict(roi_gray)
                            recognition_confidence = 100 - int(confidence)
                            
                            if recognition_confidence > 50:
                                print(f"Face recognized: {name} (confidence: {recognition_confidence}%)")
                                return name, recognition_confidence, (x, y, w, h)
                                
                    except Exception as e:
                        print(f"Face recognition error for {name}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Face recognition module error: {e}")
                return None, 0, faces[0]
                
    except Exception as e:
        print(f"Face detection error: {e}")
    
    return None, 0, None

# Simulation mode for student ID scanning only (as requested)
def simulate_detections():
    """Simulate student ID detections for testing - no face or license plate simulation"""
    import random
    
    # Only simulate student ID detection (10% chance per call)
    if random.random() < 0.1:
        # Random student from the database for ID scan simulation
        students = [
            ("23102824", "Ankit Ayaan Patel"),
            ("23107924", "Avni Divya Mehta"),
            ("23104150", "Vivaan Shah"),
            ("23106155", "Sanjay Mishra"),
            ("23103621", "Swati Myra Nair"),
            ("23108433", "Ankit Desai"),
            ("23105889", "Vihaan Kumar"),
            ("23102832", "Komal Shah")
        ]
        student_id, student_name = random.choice(students)
        confidence = 100  # Student ID scans are always 100% confident
        return 'student_id', student_id, confidence
        
    return None, None, None

# CSV Import functionality
def import_students_from_csv(csv_file_path):
    """Import student data from CSV file into database"""
    try:
        conn = sqlite3.connect('campus_sentinel.db')
        cursor = conn.cursor()
        
        imported_count = 0
        updated_count = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Skip header row if present
                if row.get('student_id') == 'student_id':
                    continue
                    
                student_id = str(row.get('student_id', '')).strip()
                name = row.get('name', '').strip()
                license_plate = row.get('license_plate', '').strip()
                
                # Skip empty rows
                if not student_id or not name:
                    continue
                
                # Create email from name and student_id
                email = f"{name.lower().replace(' ', '.')}@college.edu"
                
                # Check if student already exists
                cursor.execute('SELECT student_id FROM students WHERE student_id = ?', (student_id,))
                existing_student = cursor.fetchone()
                
                if existing_student:
                    # Update existing student
                    cursor.execute('''
                        UPDATE students 
                        SET name = ?, email = ?, active = 1
                        WHERE student_id = ?
                    ''', (name, email, student_id))
                    updated_count += 1
                else:
                    # Insert new student
                    cursor.execute('''
                        INSERT INTO students (student_id, name, email, active)
                        VALUES (?, ?, ?, 1)
                    ''', (student_id, name, email))
                    imported_count += 1
                
                # Handle license plate if provided
                if license_plate:
                    # Check if license plate already exists for this student
                    cursor.execute('''
                        SELECT id FROM license_plates 
                        WHERE student_id = ? AND plate_number = ?
                    ''', (student_id, license_plate))
                    
                    if not cursor.fetchone():
                        # Insert new license plate
                        cursor.execute('''
                            INSERT INTO license_plates (student_id, plate_number, active)
                            VALUES (?, ?, 1)
                        ''', (student_id, license_plate))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'imported': imported_count, 'updated': updated_count}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
def get_student_by_plate(plate_number):
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.student_id, s.name 
        FROM students s 
        JOIN license_plates lp ON s.student_id = lp.student_id 
        WHERE lp.plate_number = ? AND s.active = 1 AND lp.active = 1
    ''', (plate_number,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_student_by_name(face_name):
    """Get student information by recognized face name with mapping to existing classifiers"""
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    
    # Map existing trained face classifiers to our target students
    FACE_NAME_MAPPING = {
        'ab': '23102069',      # Map 'ab' classifier to Mihika Patil
        'ngoc': '23101188',    # Map 'ngoc' classifier to Vinayak Kundar  
        'tho': '23102069',     # Alternative mapping for Mihika
        'tho1': '23101188',    # Alternative mapping for Vinayak
        'mihika': '23102069',  # Direct mapping (if trained)
        'vinayak': '23101188'  # Direct mapping (if trained)
    }
    
    # Only allow predefined face names
    if face_name.lower() not in FACE_NAME_MAPPING:
        print(f"⚠️ Unrecognized face name: {face_name} - Access denied")
        conn.close()
        return None
    
    student_id = FACE_NAME_MAPPING[face_name.lower()]
    
    # Get student info and verify they're authorized for face recognition
    cursor.execute('''
        SELECT student_id, name, face_trained, active 
        FROM students 
        WHERE student_id = ? AND active = 1 AND face_trained = 1
    ''', (student_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        student_id, student_name, face_trained, active = result
        print(f"✅ Authorized face recognition: {student_name} ({student_id}) via {face_name} classifier")
        return (student_id, student_name)
    else:
        print(f"❌ Student not authorized for face recognition: {face_name}")
        return None

def log_access(detection_type, detected_value, student_id, student_name, status, confidence=None):
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO access_logs (detection_type, detected_value, student_id, student_name, status, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (detection_type, detected_value, student_id, student_name, status, confidence))
    
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Emit to frontend
    log_data = {
        'id': log_id,
        'timestamp': datetime.now().isoformat(),
        'detection_type': detection_type,
        'detected_value': detected_value,
        'student_id': student_id,
        'student_name': student_name,
        'status': status,
        'confidence': confidence
    }
    socketio.emit('new_access_log', log_data)
    return log_id

# Enhanced camera processing with better frame rate and detection
def process_camera():
    global camera, camera_active, detection_active
    
    frame_count = 0
    detection_interval = 30  # Process detection every 30 frames (~1 second)
    last_plate_detection = None
    last_face_detection = None
    detection_cooldown = 0
    
    print("🎥 Camera processing started - detecting license plates and authorized faces only")
    
    while camera_active:
        if camera is not None:
            ret, frame = camera.read()
            if ret:
                frame_count += 1
                
                # Resize frame for better performance
                height, width = frame.shape[:2]
                if width > 640:
                    scale = 640 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Process detection every few frames
                if detection_active and frame_count % detection_interval == 0 and detection_cooldown <= 0:
                    print(f"🔍 Frame {frame_count}: Starting detection cycle...")
                    
                    # 1. LICENSE PLATE DETECTION
                    print("🚗 Attempting license plate detection...")
                    plate_number, plate_confidence = detect_license_plate(frame)
                    if plate_number and plate_number != last_plate_detection:
                        last_plate_detection = plate_number
                        detection_cooldown = 60  # Cooldown to prevent spam
                        
                        # Check if plate is registered to a student
                        student_data = get_student_by_plate(plate_number)
                        if student_data:
                            student_id, student_name = student_data
                            log_access('license_plate', plate_number, student_id, student_name, 'granted', plate_confidence)
                            socketio.emit('detection_alert', {
                                'type': 'license_plate',
                                'message': f'🚗 Vehicle {plate_number} - Student: {student_name}',
                                'status': 'granted',
                                'timestamp': datetime.now().isoformat(),
                                'confidence': plate_confidence
                            })
                            print(f"✅ License Plate Access Granted: {plate_number} -> {student_name}")
                        else:
                            log_access('license_plate', plate_number, None, 'Unknown Vehicle', 'denied', plate_confidence)
                            socketio.emit('detection_alert', {
                                'type': 'license_plate',
                                'message': f'🚗 Unregistered vehicle: {plate_number}',
                                'status': 'denied',
                                'timestamp': datetime.now().isoformat(),
                                'confidence': plate_confidence
                            })
                            print(f"❌ License Plate Access Denied: {plate_number} (unregistered)")
                    else:
                        if frame_count % detection_interval == 0:  # Only log every detection cycle
                            print("🔍 No license plate detected in this cycle")
                    
                    # 2. FACE RECOGNITION (Mihika & Vinayak only)
                    face_name, face_confidence, face_coords = detect_face(frame)
                    if face_coords:  # Face detected
                        if face_name and face_name != last_face_detection:
                            # Recognized face (Mihika or Vinayak)
                            last_face_detection = face_name
                            detection_cooldown = 60
                            
                            student_data = get_student_by_name(face_name)
                            if student_data:
                                student_id, student_name = student_data
                                log_access('face', face_name, student_id, student_name, 'granted', face_confidence)
                                socketio.emit('detection_alert', {
                                    'type': 'face',
                                    'message': f'👤 Face recognized: {student_name}',
                                    'status': 'granted',
                                    'timestamp': datetime.now().isoformat(),
                                    'confidence': face_confidence
                                })
                                print(f"✅ Face Access Granted: {student_name} (confidence: {face_confidence}%)")
                            else:
                                # This shouldn't happen due to strict mapping, but just in case
                                log_access('face', face_name, None, 'Unrecognized Face', 'denied', face_confidence)
                                socketio.emit('detection_alert', {
                                    'type': 'face',
                                    'message': f'👤 Unrecognized face detected',
                                    'status': 'denied',
                                    'timestamp': datetime.now().isoformat(),
                                    'confidence': face_confidence
                                })
                                print(f"❌ Face Access Denied: Unrecognized ({face_confidence}%)")
                        
                        elif not face_name:
                            # Face detected but not recognized (not Mihika or Vinayak)
                            if frame_count % 120 == 0:  # Only alert every ~4 seconds to avoid spam
                                log_access('face', 'unknown_face', None, 'Unrecognized Face', 'denied', 0)
                                socketio.emit('detection_alert', {
                                    'type': 'face',
                                    'message': f'👤 Unrecognized face detected',
                                    'status': 'denied',
                                    'timestamp': datetime.now().isoformat(),
                                    'confidence': 0
                                })
                                print(f"❌ Face Access Denied: Unrecognized face")
                        
                        # Draw face detection box
                        x, y, w, h = face_coords
                        # Green box for recognized faces, red for unrecognized
                        color = (0, 255, 0) if face_name else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        
                        if face_name:
                            cv2.putText(frame, f"{face_name} ({face_confidence}%)", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        else:
                            cv2.putText(frame, "Unrecognized", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # 3. CONTINUE STUDENT ID SIMULATION (as requested)
                if frame_count % 150 == 0:  # Every ~5 seconds
                    # Simulate random student ID scan
                    import random
                    random_students = [
                        ('23102824', 'Ankit Ayaan Patel'),
                        ('23107924', 'Avni Divya Mehta'), 
                        ('23104150', 'Vivaan Shah'),
                        ('23106155', 'Sanjay Mishra'),
                        ('23103621', 'Swati Myra Nair'),
                        ('23108433', 'Ankit Desai'),
                        ('23105889', 'Vihaan Kumar'),
                        ('23102832', 'Komal Shah')
                    ]
                    
                    student_id, student_name = random.choice(random_students)
                    log_access('student_id', student_id, student_id, student_name, 'granted', 100)
                    socketio.emit('detection_alert', {
                        'type': 'student_id',
                        'message': f'📱 Student ID scanned: {student_name}',
                        'status': 'granted',
                        'timestamp': datetime.now().isoformat(),
                        'confidence': 100
                    })
                    print(f"📱 Student ID Simulation: {student_name} ({student_id})")
                
                # Reduce cooldown
                if detection_cooldown > 0:
                    detection_cooldown -= 1
                
                # Reset detection memory periodically
                if frame_count % 300 == 0:  # Every ~10 seconds
                    last_plate_detection = None
                    last_face_detection = None
                
                # Encode frame for streaming
                try:
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    frame_data = base64.b64encode(buffer).decode('utf-8')
                    socketio.emit('camera_frame', {'image': frame_data})
                except Exception as e:
                    print(f"Frame encoding error: {e}")
                
        time.sleep(0.033)  # Approximately 30 FPS
    
    print("🎥 Camera processing stopped")

@app.route('/api/import_csv', methods=['POST'])
def import_csv_data():
    """Import student data from CSV file"""
    try:
        # Check if file is uploaded
        if 'file' not in request.files:
            # Try to import from default CSV location
            csv_path = "../../Untitled - Sheet1.csv"
            if os.path.exists(csv_path):
                result = import_students_from_csv(csv_path)
                if result['success']:
                    return jsonify({
                        'status': 'success',
                        'message': f"Imported {result['imported']} new students, updated {result['updated']} existing"
                    })
                else:
                    return jsonify({'status': 'error', 'message': result['error']}), 500
            else:
                return jsonify({'status': 'error', 'message': 'No CSV file found'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = tempfile.mktemp(suffix='.csv')
        file.save(temp_path)
        
        # Import data
        result = import_students_from_csv(temp_path)
        os.unlink(temp_path)  # Clean up temp file
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': f"Imported {result['imported']} new students, updated {result['updated']} existing"
            })
        else:
            return jsonify({'status': 'error', 'message': result['error']}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/camera_status', methods=['GET'])
def get_camera_status():
    """Get current camera and detection status"""
    return jsonify({
        'camera_active': camera_active,
        'detection_active': detection_active,
        'camera_available': camera is not None
    })

@app.route('/api/detection_stats', methods=['GET'])
def get_detection_stats():
    """Get detection statistics for dashboard"""
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    
    # Get today's stats using a more flexible date comparison
    cursor.execute('''
        SELECT 
            COUNT(*) as total_detections,
            COUNT(CASE WHEN status = 'granted' THEN 1 END) as granted,
            COUNT(CASE WHEN status = 'denied' THEN 1 END) as denied,
            COUNT(CASE WHEN detection_type = 'license_plate' THEN 1 END) as license_plates,
            COUNT(CASE WHEN detection_type = 'face' THEN 1 END) as faces,
            COUNT(CASE WHEN detection_type = 'student_id' THEN 1 END) as student_ids
        FROM access_logs 
        WHERE DATE(timestamp) = DATE('now')
    ''')
    
    stats = cursor.fetchone()
    
    # Get hourly distribution for today
    cursor.execute('''
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as count
        FROM access_logs 
        WHERE DATE(timestamp) = DATE('now')
        GROUP BY strftime('%H', timestamp)
        ORDER BY hour
    ''')
    
    hourly_data = cursor.fetchall()
    
    # If no data for today, get recent data for demo purposes
    if not stats[0]:  # If no detections today
        cursor.execute('''
            SELECT 
                COUNT(*) as total_detections,
                COUNT(CASE WHEN status = 'granted' THEN 1 END) as granted,
                COUNT(CASE WHEN status = 'denied' THEN 1 END) as denied,
                COUNT(CASE WHEN detection_type = 'license_plate' THEN 1 END) as license_plates,
                COUNT(CASE WHEN detection_type = 'face' THEN 1 END) as faces,
                COUNT(CASE WHEN detection_type = 'student_id' THEN 1 END) as student_ids
            FROM access_logs 
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
        ''')
        stats = cursor.fetchone()
        
        # Get recent hourly distribution
        cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as count
            FROM access_logs 
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        ''')
        hourly_data = cursor.fetchall()
    
    conn.close()
    
    # Convert hourly data to proper format
    hourly_distribution = {}
    for hour, count in hourly_data:
        hourly_distribution[f"{hour}:00"] = count
    
    return jsonify({
        'total_detections': stats[0] or 0,
        'granted': stats[1] or 0,
        'denied': stats[2] or 0,
        'license_plates': stats[3] or 0,
        'faces': stats[4] or 0,
        'student_ids': stats[5] or 0,
        'hourly_distribution': hourly_distribution
    })

@app.route('/api/recent_detections', methods=['GET'])
def get_recent_detections():
    """Get recent detection alerts"""
    limit = request.args.get('limit', 10)
    
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, detection_type, detected_value, student_name, status, confidence
        FROM access_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    detections = cursor.fetchall()
    conn.close()
    
    formatted_detections = []
    for detection in detections:
        formatted_detections.append({
            'timestamp': detection[0],
            'type': detection[1],
            'value': detection[2],
            'student_name': detection[3],
            'status': detection[4],
            'confidence': detection[5]
        })
    
    return jsonify(formatted_detections)
@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    global camera, camera_active
    try:
        # Check if camera is already active
        if camera_active:
            return jsonify({'status': 'info', 'message': 'Camera is already running'})
        
        # Release any existing camera instance
        if camera is not None:
            camera.release()
            camera = None
            time.sleep(0.5)  # Give time for camera to be released
        
        # Try different camera indices with enhanced initialization
        camera_indices = [0, 1, 2, -1]  # Include DirectShow backend
        camera_found = False
        
        for idx in camera_indices:
            print(f"Trying camera index {idx}...")
            try:
                # Try different backends for better Windows compatibility
                if idx == -1:
                    test_camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow backend
                else:
                    test_camera = cv2.VideoCapture(idx)
                
                # Set properties before checking
                test_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                test_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                test_camera.set(cv2.CAP_PROP_FPS, 30)
                test_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                if test_camera.isOpened():
                    ret, test_frame = test_camera.read()
                    if ret and test_frame is not None:
                        camera = test_camera
                        camera_found = True
                        print(f"✅ Camera found at index {idx}")
                        break
                    else:
                        print(f"❌ Camera at index {idx} failed to read frame")
                        test_camera.release()
                else:
                    print(f"❌ Camera at index {idx} failed to open")
                    test_camera.release()
            except Exception as idx_error:
                print(f"❌ Error with camera index {idx}: {idx_error}")
                if 'test_camera' in locals():
                    test_camera.release()
        
        if not camera_found:
            error_msg = 'No camera found. Possible issues: camera in use by another app, no camera connected, or permission denied'
            print(f"❌ {error_msg}")
            return jsonify({'status': 'error', 'message': error_msg}), 500
        
        camera_active = True
        
        # Start camera processing thread
        threading.Thread(target=process_camera, daemon=True).start()
        
        print("✅ Camera started successfully")
        return jsonify({'status': 'success', 'message': 'Camera started successfully'})
    except Exception as e:
        error_msg = f'Failed to start camera: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'status': 'error', 'message': error_msg}), 500

@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    global camera, camera_active
    camera_active = False
    if camera:
        camera.release()
        camera = None
    return jsonify({'status': 'success', 'message': 'Camera stopped'})

@app.route('/api/toggle_detection', methods=['POST'])
def toggle_detection():
    global detection_active
    detection_active = not detection_active
    status = 'started' if detection_active else 'stopped'
    return jsonify({'status': 'success', 'message': f'Detection {status}', 'active': detection_active})

@app.route('/api/student_scan', methods=['POST'])
def student_scan():
    """API endpoint for external student ID scanning"""
    data = request.get_json()
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'status': 'error', 'message': 'Student ID required'}), 400
    
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT student_id, name FROM students WHERE student_id = ? AND active = 1', (student_id,))
    student = cursor.fetchone()
    conn.close()
    
    if student:
        student_id, student_name = student
        log_access('student_id', student_id, student_id, student_name, 'granted')
        return jsonify({
            'status': 'success', 
            'message': f'Access granted for {student_name}',
            'student_name': student_name
        })
    else:
        log_access('student_id', student_id, None, None, 'denied')
        return jsonify({
            'status': 'denied', 
            'message': 'Student ID not found or inactive'
        }), 404

@app.route('/api/access_logs', methods=['GET'])
def get_access_logs():
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, detection_type, detected_value, student_id, student_name, status, confidence
        FROM access_logs 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    logs = cursor.fetchall()
    conn.close()
    
    formatted_logs = []
    for log in logs:
        formatted_logs.append({
            'timestamp': log[0],
            'detection_type': log[1],
            'detected_value': log[2],
            'student_id': log[3],
            'student_name': log[4],
            'status': log[5],
            'confidence': log[6]
        })
    
    return jsonify(formatted_logs)

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect('campus_sentinel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.student_id, s.name, s.email, s.active,
               GROUP_CONCAT(lp.plate_number) as plates
        FROM students s
        LEFT JOIN license_plates lp ON s.student_id = lp.student_id AND lp.active = 1
        WHERE s.active = 1
        GROUP BY s.student_id, s.name, s.email, s.active
    ''')
    students = cursor.fetchall()
    conn.close()
    
    formatted_students = []
    for student in students:
        plates = student[4].split(',') if student[4] else []
        formatted_students.append({
            'student_id': student[0],
            'name': student[1],
            'email': student[2],
            'active': student[3],
            'plates': plates
        })
    
    return jsonify(formatted_students)

# Socket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'status': 'Connected to Campus Sentinel'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    init_db()
    print("Campus Sentinel Backend starting...")
    print("Initializing database...")
    print("Starting Flask-SocketIO server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)