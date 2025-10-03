"""
Automated Student ID Scanner Simulator
Continuously generates random student ID scans to test the system
"""

import requests
import json
import time
import random
import threading
from datetime import datetime

# Backend API endpoint
API_URL = "http://localhost:5000/api/student_scan"

# List of actual student IDs from the CSV data
STUDENT_IDS = [
    "23102824", "23107924", "23104150", "23108573", "23101916", 
    "23106155", "23103621", "23101188", "23108433", "23105889",
    "23102832", "23102290", "23103705", "23107537", "23108953",
    "23104119", "23101887", "23104872", "23109883", "23109565",
    "23102127", "23105325", "23101722", "23108007", "23101685",
    "23106794", "23106000", "23105573", "23105279", "23104228",
    "23105920", "23108238", "23106491", "23101090", "23102988",
    "23109976", "23105543", "23107883", "23105892", "23108022",
    "23101659", "23102874", "23103683", "23106590", "23108532",
    "23105397", "23107209", "23108800", "23106016", "23105636",
    "23103073", "23109042", "23105066", "23108253", "23102625",
    "23103564", "23103330", "23105982", "23106280", "23103870",
    "23109056", "23106403", "23108242", "23103522", "23104993",
    "23107798", "23109022", "23106272", "23107246", "23106439",
    "23103529", "23102480", "23107267", "23101153", "23105901",
    "23109138", "23103153", "23106994", "23108451", "23101609",
    "23104868", "23104362", "23101046", "23101422", "23109543",
    "23102768", "23104522", "23102557", "23102099", "23102697",
    "23102882", "23109691", "23102391", "23108957", "23105742",
    "23104770", "23106129", "23106562", "23106724", "23106179"
]

# Some invalid IDs for testing denied access
INVALID_IDS = [
    "99999999", "12345678", "00000000", "11111111", "23199999"
]

class StudentIDScanner:
    def __init__(self):
        self.running = False
        self.scan_interval = 3  # seconds between scans
        self.success_count = 0
        self.denied_count = 0
        self.error_count = 0
        
    def scan_student_id(self, student_id):
        """Simulate scanning a student ID and sending to backend"""
        try:
            payload = {"student_id": student_id}
            headers = {"Content-Type": "application/json"}
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📱 Scanning Student ID: {student_id}")
            
            response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[{timestamp}] ✅ {data['message']}")
                if 'student_name' in data:
                    print(f"[{timestamp}]    Student: {data['student_name']}")
                self.success_count += 1
            elif response.status_code == 404:
                data = response.json()
                print(f"[{timestamp}] ❌ {data['message']}")
                self.denied_count += 1
            else:
                print(f"[{timestamp}] ⚠️  Server error: {response.status_code}")
                self.error_count += 1
                
        except requests.exceptions.ConnectionError:
            print(f"[{timestamp}] ❌ Cannot connect to backend server")
            self.error_count += 1
        except requests.exceptions.Timeout:
            print(f"[{timestamp}] ⏱️  Request timeout")
            self.error_count += 1
        except Exception as e:
            print(f"[{timestamp}] ❌ Error: {str(e)}")
            self.error_count += 1
    
    def generate_random_scan(self):
        """Generate a random student ID scan (mix of valid and invalid)"""
        # 80% chance of valid ID, 20% chance of invalid ID
        if random.random() < 0.8:
            return random.choice(STUDENT_IDS)
        else:
            return random.choice(INVALID_IDS)
    
    def continuous_scanning(self):
        """Continuously scan random student IDs"""
        print("🔄 Starting continuous scanning mode...")
        print(f"   Scan interval: {self.scan_interval} seconds")
        print("   Press Ctrl+C to stop\n")
        
        while self.running:
            try:
                student_id = self.generate_random_scan()
                self.scan_student_id(student_id)
                
                # Print statistics every 10 scans
                total_scans = self.success_count + self.denied_count + self.error_count
                if total_scans > 0 and total_scans % 10 == 0:
                    print(f"\n📊 Statistics: {self.success_count} granted, {self.denied_count} denied, {self.error_count} errors\n")
                
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                break
        
        print(f"\n🛑 Scanning stopped")
        print(f"📊 Final Statistics:")
        print(f"   ✅ Granted: {self.success_count}")
        print(f"   ❌ Denied: {self.denied_count}")
        print(f"   ⚠️  Errors: {self.error_count}")
    
    def start(self):
        """Start the scanner"""
        self.running = True
        self.continuous_scanning()
    
    def stop(self):
        """Stop the scanner"""
        self.running = False

def main():
    print("=" * 60)
    print("  Campus Sentinel - Automated Student ID Scanner")
    print("=" * 60)
    print()
    print("This simulator automatically generates random student ID scans")
    print("to test the campus security system with real and fake IDs.")
    print()
    
    scanner = StudentIDScanner()
    
    while True:
        print("Options:")
        print("1. Start continuous scanning (auto-mode)")
        print("2. Single random scan")
        print("3. Set scan interval")
        print("4. Test specific student ID")
        print("5. Show statistics")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            try:
                scanner.start()
            except KeyboardInterrupt:
                scanner.stop()
                
        elif choice == "2":
            student_id = scanner.generate_random_scan()
            scanner.scan_student_id(student_id)
            
        elif choice == "3":
            try:
                interval = float(input("Enter scan interval in seconds (current: {}): ".format(scanner.scan_interval)))
                if 0.5 <= interval <= 60:
                    scanner.scan_interval = interval
                    print(f"✅ Scan interval set to {interval} seconds")
                else:
                    print("❌ Interval must be between 0.5 and 60 seconds")
            except ValueError:
                print("❌ Invalid number")
                
        elif choice == "4":
            student_id = input("Enter Student ID to test: ").strip()
            if student_id:
                scanner.scan_student_id(student_id)
            else:
                print("❌ Invalid student ID")
                
        elif choice == "5":
            total = scanner.success_count + scanner.denied_count + scanner.error_count
            print(f"\n📊 Current Statistics:")
            print(f"   Total scans: {total}")
            print(f"   ✅ Granted: {scanner.success_count}")
            print(f"   ❌ Denied: {scanner.denied_count}")
            print(f"   ⚠️  Errors: {scanner.error_count}")
            if total > 0:
                print(f"   Success rate: {(scanner.success_count/total)*100:.1f}%")
            print()
                
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-6")

if __name__ == "__main__":
    main()