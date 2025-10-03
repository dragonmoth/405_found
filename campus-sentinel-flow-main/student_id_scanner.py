"""
Student ID Scanner Simulator
Simulates external barcode/QR code scanner sending student IDs to the system
"""

import requests
import time
import json

# Backend API endpoint
API_URL = "http://localhost:5000/api/student_scan"

# Sample student IDs for testing
STUDENT_IDS = [
    "STU-2025-001",  # Rohan Sharma
    "STU-2025-042",  # Priya Verma  
    "STU-2025-103",  # Amit Kumar
    "STU-2025-999",  # Unknown student (for testing denied access)
]

def scan_student_id(student_id):
    """Simulate scanning a student ID and sending to backend"""
    try:
        payload = {"student_id": student_id}
        headers = {"Content-Type": "application/json"}
        
        print(f"📱 Scanning Student ID: {student_id}")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            if 'student_name' in data:
                print(f"   Student: {data['student_name']}")
        elif response.status_code == 404:
            data = response.json()
            print(f"❌ {data['message']}")
        else:
            print(f"⚠️  Server error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server")
        print("   Make sure the Flask backend is running on http://localhost:5000")
    except requests.exceptions.Timeout:
        print("⏱️  Error: Request timeout")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("=" * 50)
    print("  Campus Sentinel - Student ID Scanner Simulator")
    print("=" * 50)
    print()
    print("This simulator sends student ID scans to the backend system")
    print("Make sure the backend server is running before using this tool")
    print()
    
    while True:
        print("\nOptions:")
        print("1. Scan predefined student IDs (auto)")
        print("2. Manual student ID entry")
        print("3. Continuous scanning (demo mode)")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print("\n--- Scanning predefined student IDs ---")
            for student_id in STUDENT_IDS:
                scan_student_id(student_id)
                time.sleep(2)  # Wait 2 seconds between scans
                
        elif choice == "2":
            student_id = input("\nEnter Student ID: ").strip()
            if student_id:
                scan_student_id(student_id)
            else:
                print("❌ Invalid student ID")
                
        elif choice == "3":
            print("\n--- Demo Mode: Continuous Scanning ---")
            print("Press Ctrl+C to stop")
            try:
                while True:
                    for student_id in STUDENT_IDS:
                        scan_student_id(student_id)
                        time.sleep(5)  # Wait 5 seconds between scans
            except KeyboardInterrupt:
                print("\n🛑 Demo mode stopped")
                
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-4")

if __name__ == "__main__":
    main()