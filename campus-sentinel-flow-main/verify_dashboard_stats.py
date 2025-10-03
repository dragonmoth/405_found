import requests
import json
from datetime import datetime

def verify_dashboard_statistics():
    """Verify that all dashboard statistics are working and updating"""
    
    print("🔍 Verifying Dashboard Statistics...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Check Detection Stats API
        print("\n📊 Backend Detection Statistics:")
        response = requests.get(f'{base_url}/api/detection_stats')
        if response.ok:
            stats = response.json()
            print(f"   Total Detections Today: {stats.get('total_detections', 0)}")
            print(f"   Granted Access: {stats.get('granted', 0)}")
            print(f"   Denied Access: {stats.get('denied', 0)}")
            print(f"   License Plates: {stats.get('license_plates', 0)}")
            print(f"   Faces: {stats.get('faces', 0)}")
            print(f"   Student IDs: {stats.get('student_ids', 0)}")
            
            hourly = stats.get('hourly_distribution', {})
            if hourly:
                print(f"   Hourly Distribution: {len(hourly)} hours with data")
                # Show peak hours
                peak_hour = max(hourly.items(), key=lambda x: x[1]) if hourly else None
                if peak_hour:
                    print(f"   Peak Hour: {peak_hour[0]} ({peak_hour[1]} entries)")
        else:
            print(f"   ❌ Failed to get detection stats: {response.status_code}")
        
        # 2. Check Access Logs
        print("\n📝 Access Logs:")
        response = requests.get(f'{base_url}/api/access_logs')
        if response.ok:
            logs = response.json()
            print(f"   Total Access Logs: {len(logs)}")
            
            # Count today's logs
            today = datetime.now().date()
            today_logs = []
            for log in logs:
                try:
                    log_date = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')).date()
                    if log_date == today:
                        today_logs.append(log)
                except:
                    pass
            
            print(f"   Today's Logs: {len(today_logs)}")
            
            # Count by status
            granted = sum(1 for log in today_logs if log.get('status') == 'granted')
            denied = sum(1 for log in today_logs if log.get('status') == 'denied')
            print(f"   Today - Granted: {granted}, Denied: {denied}")
            
            # Count by detection type
            license_plates = sum(1 for log in today_logs if log.get('detection_type') == 'license_plate')
            faces = sum(1 for log in today_logs if log.get('detection_type') == 'face')
            student_ids = sum(1 for log in today_logs if log.get('detection_type') == 'student_id')
            
            print(f"   Today - License Plates: {license_plates}, Faces: {faces}, Student IDs: {student_ids}")
            
            # Show recent logs
            print("\n   Recent Access Logs (last 5):")
            for i, log in enumerate(logs[:5]):
                status_icon = "✅" if log.get('status') == 'granted' else "❌"
                print(f"   {i+1}. {status_icon} {log.get('detection_type', 'unknown')} - {log.get('detected_value', 'N/A')} ({log.get('status', 'unknown')})")
        else:
            print(f"   ❌ Failed to get access logs: {response.status_code}")
        
        # 3. Check Students Database
        print("\n👥 Students Database:")
        response = requests.get(f'{base_url}/api/students')
        if response.ok:
            students = response.json()
            print(f"   Total Students: {len(students)}")
            
            with_plates = sum(1 for s in students if s.get('plates') and any(s['plates']))
            print(f"   Students with License Plates: {with_plates}")
        else:
            print(f"   ❌ Failed to get students: {response.status_code}")
        
        # 4. Check Camera Status
        print("\n📹 Camera Status:")
        response = requests.get(f'{base_url}/api/camera_status')
        if response.ok:
            status = response.json()
            camera_status = "🟢 Active" if status.get('camera_active') else "🔴 Inactive"
            detection_status = "🟢 Active" if status.get('detection_active') else "🔴 Inactive"
            print(f"   Camera: {camera_status}")
            print(f"   Detection: {detection_status}")
        else:
            print(f"   ❌ Failed to get camera status: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("✅ Dashboard Statistics Verification Complete!")
        print("\n🎯 Expected Dashboard Updates:")
        print("   • Total Entries Today: Should show combined count from all detection types")
        print("   • Unique Vehicles: Should show count of unique license plates detected today")
        print("   • Denied Access: Should show count of denied attempts today")
        print("   • Peak Traffic Hour: Should show hour with most activity")
        print("   • Traffic Analytics Chart: Should use hourly distribution data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    verify_dashboard_statistics()