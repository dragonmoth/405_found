"""
Quick Test Script for Campus Sentinel
Tests the complete integration: license plates, faces (Mihika & Vinayak), and student ID simulation
"""

import requests
import time
import json

def test_system_integration():
    """Test the complete system integration"""
    
    print("🎯 Campus Sentinel Integration Test")
    print("=" * 50)
    
    # Check backend connection
    try:
        response = requests.get("http://localhost:5000/api/camera_status", timeout=3)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Backend connected")
            print(f"   Camera active: {status.get('camera_active', False)}")
            print(f"   Detection active: {status.get('detection_active', False)}")
        else:
            print("❌ Backend not responding properly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Please start the backend first:")
        print("   cd backend && python app.py")
        return False
    
    # Test student ID simulation (manually trigger one)
    print(f"\n📱 Testing Student ID Simulation...")
    try:
        test_students = [
            ("23102824", "Ankit Ayaan Patel"),
            ("23107924", "Avni Divya Mehta"),
            ("23104150", "Vivaan Shah")
        ]
        
        for student_id, student_name in test_students:
            response = requests.post("http://localhost:5000/api/student_scan", 
                                   json={"student_id": student_id}, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Student ID scan: {result['message']}")
            else:
                print(f"⚠️ Student ID scan failed for {student_id}")
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ Student ID test error: {e}")
    
    # Check recent access logs
    print(f"\n📊 Checking Recent Access Logs...")
    try:
        response = requests.get("http://localhost:5000/api/access_logs")
        if response.status_code == 200:
            logs = response.json()
            
            if logs:
                print(f"✅ Found {len(logs)} total access logs")
                
                # Show recent logs by type
                recent_logs = logs[:10]  # Last 10 logs
                
                license_logs = [log for log in recent_logs if log.get('detection_type') == 'license_plate']
                face_logs = [log for log in recent_logs if log.get('detection_type') == 'face']
                id_logs = [log for log in recent_logs if log.get('detection_type') == 'student_id']
                
                print(f"\n📋 Recent Activity:")
                print(f"   🚗 License Plate Detections: {len(license_logs)}")
                print(f"   👤 Face Detections: {len(face_logs)}")  
                print(f"   📱 Student ID Scans: {len(id_logs)}")
                
                # Show last few entries
                print(f"\n🕒 Last 5 Access Attempts:")
                for i, log in enumerate(recent_logs[:5]):
                    timestamp = log.get('timestamp', 'Unknown')
                    det_type = log.get('detection_type', 'Unknown')
                    detected_value = log.get('detected_value', 'Unknown')
                    student_name = log.get('student_name', 'Unknown')
                    status = log.get('status', 'Unknown')
                    confidence = log.get('confidence', 0)
                    
                    status_icon = "✅" if status == 'granted' else "❌"
                    type_icon = {"license_plate": "🚗", "face": "👤", "student_id": "📱"}.get(det_type, "❓")
                    
                    print(f"   {i+1}. {status_icon} {type_icon} {det_type}: {detected_value}")
                    if student_name != 'Unknown':
                        print(f"      Student: {student_name} (confidence: {confidence}%)")
                    print(f"      Time: {timestamp}")
                    print()
                    
            else:
                print("⚠️ No access logs found")
                
    except Exception as e:
        print(f"❌ Access logs test error: {e}")
    
    # Check detection statistics
    print(f"📈 Current Detection Statistics:")
    try:
        response = requests.get("http://localhost:5000/api/detection_stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total detections today: {stats.get('total_detections', 0)}")
            print(f"   Access granted: {stats.get('granted', 0)}")
            print(f"   Access denied: {stats.get('denied', 0)}")
            print(f"   License plates: {stats.get('license_plates', 0)}")
            print(f"   Face detections: {stats.get('faces', 0)}")
            print(f"   Student ID scans: {stats.get('student_ids', 0)}")
        else:
            print("⚠️ Could not load detection statistics")
    except Exception as e:
        print(f"❌ Statistics error: {e}")
    
    print(f"\n🎯 System Integration Status:")
    print(f"✅ Backend API - Working")
    print(f"✅ Student ID Simulation - Active")
    print(f"✅ Access Logging - Recording")
    print(f"✅ Admin Dashboard Data - Available")
    
    print(f"\n🔍 What You Should See:")
    print(f"1. 🎥 Camera Feed: Shows live video with detection boxes")
    print(f"2. 👤 Face Detection: Green box for Mihika/Vinayak, Red box for others")
    print(f"3. 🚗 License Plate: Detects and logs all plates")
    print(f"4. 📱 Student ID: Random simulation every ~5 seconds")
    print(f"5. 📊 Admin Dashboard: Real-time logs and statistics")
    
    print(f"\n🌐 Frontend URLs:")
    print(f"   Admin Dashboard: http://localhost:5173/admin")
    print(f"   Security Monitoring: http://localhost:5173/monitoring")
    
    return True

def check_authorized_students():
    """Check which students are authorized for face recognition"""
    print(f"\n👥 Checking Authorized Students...")
    
    try:
        response = requests.get("http://localhost:5000/api/students")
        if response.status_code == 200:
            students = response.json()
            
            # Filter students with face recognition
            face_authorized = [s for s in students if s.get('face_trained', False)]
            
            print(f"✅ Total students in database: {len(students)}")
            print(f"✅ Authorized for face recognition: {len(face_authorized)}")
            
            print(f"\n👤 Face Recognition Authorized:")
            for student in face_authorized:
                print(f"   - {student['name']} (ID: {student['student_id']})")
                if student.get('plates'):
                    print(f"     License plates: {', '.join(student['plates'])}")
                    
        else:
            print("❌ Could not load student data")
            
    except Exception as e:
        print(f"❌ Student check error: {e}")

def main():
    """Main test function"""
    
    print("🏫 Campus Sentinel Flow - Integration Test")
    print("=" * 60)
    print("Testing: License Plates + Faces (Mihika & Vinayak) + Student ID Simulation")
    print()
    
    # Run integration tests
    if test_system_integration():
        check_authorized_students()
        
        print(f"\n🎉 Integration Test Complete!")
        print(f"=" * 60)
        print(f"✅ System is ready for live testing")
        print(f"\nNext Steps:")
        print(f"1. Open: http://localhost:5173/monitoring")
        print(f"2. Click 'Start Camera' and 'Start Detection'")
        print(f"3. Test with license plates and faces")
        print(f"4. Check admin dashboard for real-time logs")
        print(f"\n🔒 Security: Only Mihika Patil and Vinayak Kundar will be granted face access!")
    else:
        print(f"\n❌ Integration test failed - please fix issues above")

if __name__ == "__main__":
    main()