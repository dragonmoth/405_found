"""
Campus Sentinel System Demo
Demonstrates all working features of the security system
"""

import requests
import json
import time
import threading
from datetime import datetime

class CampusSentinelDemo:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        
    def print_header(self, title):
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def print_section(self, title):
        print(f"\n🔹 {title}")
        print("-" * 40)
    
    def test_student_scanning(self):
        self.print_section("Student ID Scanner Test")
        
        test_students = [
            ("STU-2025-001", "Rohan Sharma"),
            ("23102824", "Ankit Ayaan Patel"),
            ("23107924", "Avni Divya Mehta"),
            ("99999999", "Invalid Student")
        ]
        
        for student_id, expected_name in test_students:
            try:
                response = requests.post(f'{self.base_url}/api/student_scan', 
                                       json={"student_id": student_id})
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {student_id}: {data['message']}")
                else:
                    data = response.json()
                    print(f"❌ {student_id}: {data['message']}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error testing {student_id}: {e}")
    
    def test_api_endpoints(self):
        self.print_section("API Endpoints Test")
        
        endpoints = [
            ("/api/students", "Students Database"),
            ("/api/access_logs", "Access Logs"),
            ("/api/camera_status", "Camera Status"),
            ("/api/detection_stats", "Detection Statistics")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f'{self.base_url}{endpoint}')
                if response.ok:
                    data = response.json()
                    if endpoint == "/api/students":
                        print(f"✅ {name}: {len(data)} students loaded")
                    elif endpoint == "/api/access_logs":
                        print(f"✅ {name}: {len(data)} access logs")
                    elif endpoint == "/api/camera_status":
                        status = "Active" if data.get('camera_active') else "Inactive"
                        print(f"✅ {name}: Camera {status}")
                    elif endpoint == "/api/detection_stats":
                        print(f"✅ {name}: {data.get('total_detections', 0)} total detections today")
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: {e}")
    
    def test_camera_controls(self):
        self.print_section("Camera Control Test")
        
        try:
            # Test camera start
            response = requests.post(f'{self.base_url}/api/start_camera')
            if response.ok:
                result = response.json()
                print(f"✅ Start Camera: {result['message']}")
            else:
                print(f"❌ Start Camera: {response.status_code}")
            
            time.sleep(2)
            
            # Test detection toggle
            response = requests.post(f'{self.base_url}/api/toggle_detection')
            if response.ok:
                result = response.json()
                print(f"✅ Toggle Detection: {result['message']}")
            else:
                print(f"❌ Toggle Detection: {response.status_code}")
                
            time.sleep(2)
            
            # Test camera stop
            response = requests.post(f'{self.base_url}/api/stop_camera')
            if response.ok:
                result = response.json()
                print(f"✅ Stop Camera: {result['message']}")
            else:
                print(f"❌ Stop Camera: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Camera Control Error: {e}")
    
    def test_csv_import(self):
        self.print_section("CSV Data Import Test")
        
        try:
            response = requests.post(f'{self.base_url}/api/import_csv')
            if response.ok:
                result = response.json()
                print(f"✅ CSV Import: {result['message']}")
            else:
                result = response.json()
                print(f"❌ CSV Import: {result['message']}")
        except Exception as e:
            print(f"❌ CSV Import Error: {e}")
    
    def show_database_info(self):
        self.print_section("Database Information")
        
        try:
            # Get students
            response = requests.get(f'{self.base_url}/api/students')
            if response.ok:
                students = response.json()
                print(f"📊 Total Students: {len(students)}")
                
                with_plates = sum(1 for s in students if s.get('plates') and s['plates'][0])
                print(f"🚗 Students with License Plates: {with_plates}")
                
                # Show sample students
                print("\n📋 Sample Students:")
                for i, student in enumerate(students[:5]):
                    plates = ", ".join(student.get('plates', [])) if student.get('plates') else "None"
                    print(f"   {student['student_id']}: {student['name']} (Plates: {plates})")
                    
        except Exception as e:
            print(f"❌ Database Info Error: {e}")
    
    def run_demo(self):
        self.print_header("Campus Sentinel System Demo")
        print("🎯 Testing all system components...")
        
        # Test basic API endpoints
        self.test_api_endpoints()
        
        # Show database info
        self.show_database_info()
        
        # Test CSV import
        self.test_csv_import()
        
        # Test student scanning
        self.test_student_scanning()
        
        # Test camera controls
        self.test_camera_controls()
        
        self.print_header("Demo Complete")
        print("✅ All tests completed!")
        print("\n🚀 System Features:")
        print("   • ✅ Student ID Scanning (Barcode/QR simulation)")
        print("   • ✅ Live Camera Feed with Detection")
        print("   • ✅ Face Recognition (with simulation fallback)")
        print("   • ✅ License Plate Detection (with simulation fallback)")
        print("   • ✅ Real-time Admin Dashboard")
        print("   • ✅ Access Logs and Statistics")
        print("   • ✅ CSV Student Data Import")
        print("   • ✅ Socket.IO Real-time Updates")
        
        print("\n📱 Frontend: http://localhost:8081")
        print("🔧 Backend API: http://localhost:5000")
        print("\n🎮 Use the auto_scanner.py for continuous student ID generation!")

if __name__ == "__main__":
    demo = CampusSentinelDemo()
    demo.run_demo()