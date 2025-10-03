"""
License Plate Detection Test & Trigger Script
Helps test and debug license plate detection issues
"""

import cv2
import requests
import numpy as np
from datetime import datetime
import time
import os

def test_camera_and_trigger_detections():
    """Test camera feed and manually trigger detections for debugging"""
    
    print("=" * 60)
    print("  License Plate Detection Test Script")
    print("=" * 60)
    print()
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:5000/api/access_logs", timeout=3)
        print("✅ Backend server is running")
    except:
        print("❌ Backend server not running. Please start the backend first:")
        print("   cd backend")
        print("   venv\\Scripts\\activate")
        print("   python app.py")
        return

    # Start camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("✅ Camera opened successfully")
    print("\nInstructions:")
    print("- Hold a license plate or image with text in front of the camera")
    print("- Press 'c' to capture and test detection")
    print("- Press 's' to save current frame for analysis")
    print("- Press 'r' to start/stop recording for later analysis")
    print("- Press 'q' to quit")
    print("\nTips for better detection:")
    print("- Ensure good lighting")
    print("- Hold plate steady and parallel to camera")
    print("- Try different distances (2-6 feet)")
    print("- Avoid reflections and shadows")
    
    recording = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Display frame with instructions
        display_frame = frame.copy()
        cv2.putText(display_frame, "License Plate Detection Test", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_frame, "Press 'c' to capture, 'q' to quit", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if recording:
            cv2.putText(display_frame, "RECORDING", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            out.write(frame)
        
        cv2.imshow('License Plate Detection Test', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            # Capture and test detection
            print(f"\n📸 Capturing frame #{frame_count} for detection...")
            test_single_frame_detection(frame)
            
        elif key == ord('s'):
            # Save frame for analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_frame_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Frame saved as: {filename}")
            
        elif key == ord('r'):
            # Toggle recording
            if not recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_recording_{timestamp}.avi"
                out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
                recording = True
                print(f"🎬 Started recording: {filename}")
            else:
                out.release()
                recording = False
                print("⏹️ Stopped recording")
                
        elif key == ord('q'):
            break
    
    # Cleanup
    cap.release()
    if recording and out:
        out.release()
    cv2.destroyAllWindows()
    print("\n👋 Camera test completed")

def test_single_frame_detection(frame):
    """Test detection on a single frame and show detailed results"""
    try:
        # Save test frame
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_filename = f"detection_test_{timestamp}.jpg"
        cv2.imwrite(test_filename, frame)
        
        print(f"   📁 Test frame saved: {test_filename}")
        print("   🔍 Running OpenALPR detection...")
        
        # Test with OpenALPR directly
        openalpr_path = r"..\..\openalpr_64\alpr.exe"
        
        if not os.path.exists(openalpr_path):
            print(f"   ❌ OpenALPR not found at: {openalpr_path}")
            return
            
        import subprocess
        import json
        
        # Run OpenALPR with verbose output
        result = subprocess.run([
            openalpr_path, 
            "-j",  # JSON output
            "-n", "10",  # Return top 10 results
            "-c", "us",  # US region
            "--config", os.path.join(os.path.dirname(openalpr_path), "openalpr.conf"),
            test_filename
        ], capture_output=True, text=True, timeout=30)
        
        print(f"   📊 OpenALPR return code: {result.returncode}")
        
        if result.stdout:
            try:
                results = json.loads(result.stdout)
                print(f"   📋 Raw results: {results}")
                
                if results and "results" in results:
                    if len(results["results"]) > 0:
                        print(f"   ✅ Found {len(results['results'])} plate regions")
                        
                        for i, plate_result in enumerate(results["results"]):
                            print(f"   \n   🚗 Plate Region #{i+1}:")
                            if "candidates" in plate_result:
                                for j, candidate in enumerate(plate_result["candidates"]):
                                    plate = candidate.get("plate", "")
                                    confidence = candidate.get("confidence", 0)
                                    print(f"      Candidate #{j+1}: '{plate}' (confidence: {confidence:.1f}%)")
                            
                            if "coordinates" in plate_result:
                                coords = plate_result["coordinates"]
                                print(f"      Location: {coords}")
                    else:
                        print("   ⚠️ No license plates detected in this frame")
                else:
                    print("   ⚠️ No detection results returned")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                print(f"   Raw stdout: {result.stdout}")
        else:
            print("   ⚠️ No stdout from OpenALPR")
            
        if result.stderr:
            print(f"   ⚠️ OpenALPR stderr: {result.stderr}")
            
        # Test image enhancement
        print("\n   🎨 Testing image enhancement...")
        enhanced = enhance_image_for_detection(frame)
        enhanced_filename = f"enhanced_{timestamp}.jpg"
        cv2.imwrite(enhanced_filename, enhanced)
        print(f"   💾 Enhanced image saved: {enhanced_filename}")
        
        # Show recommendations
        print("\n   💡 Tips to improve detection:")
        print("   - Ensure the license plate is clearly visible")
        print("   - Good lighting without shadows or reflections")
        print("   - Hold the plate parallel to the camera")
        print("   - Try different distances (2-6 feet from camera)")
        print("   - Make sure text is not blurry or at an angle")
        
    except Exception as e:
        print(f"   ❌ Detection test error: {e}")

def enhance_image_for_detection(frame):
    """Apply image enhancement to improve OCR results"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Sharpening kernel
        kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        
        # Convert back to BGR
        enhanced_bgr = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        
        return enhanced_bgr
        
    except Exception as e:
        print(f"Image enhancement error: {e}")
        return frame

def check_detection_logs():
    """Check recent detection logs from the database"""
    print("\n📊 Checking recent detection logs...")
    
    try:
        response = requests.get("http://localhost:5000/api/access_logs")
        if response.status_code == 200:
            logs = response.json()
            
            # Filter for recent license plate detections
            plate_logs = [log for log in logs if log.get('detection_type') == 'license_plate']
            
            if plate_logs:
                print(f"   ✅ Found {len(plate_logs)} recent license plate detections:")
                for log in plate_logs[:5]:  # Show last 5
                    timestamp = log.get('timestamp', 'Unknown')
                    plate = log.get('detected_value', 'Unknown')
                    confidence = log.get('confidence', 0)
                    status = log.get('status', 'Unknown')
                    print(f"   🚗 {timestamp}: {plate} ({confidence:.1f}%) - {status}")
            else:
                print("   ⚠️ No recent license plate detections found")
                
        else:
            print(f"   ❌ Failed to fetch logs: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking logs: {e}")

def main():
    """Main menu for license plate testing"""
    while True:
        print("\n" + "="*50)
        print("  License Plate Detection Troubleshooting")
        print("="*50)
        print("1. Live camera test with manual capture")
        print("2. Check recent detection logs")
        print("3. Test OpenALPR installation")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            test_camera_and_trigger_detections()
        elif choice == "2":
            check_detection_logs()
        elif choice == "3":
            test_openalpr_installation()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

def test_openalpr_installation():
    """Test if OpenALPR is properly installed"""
    print("\n🔧 Testing OpenALPR installation...")
    
    openalpr_path = r"..\..\openalpr_64\alpr.exe"
    config_path = r"..\..\openalpr_64\openalpr.conf"
    
    print(f"   📍 Checking executable: {openalpr_path}")
    if os.path.exists(openalpr_path):
        print("   ✅ OpenALPR executable found")
    else:
        print("   ❌ OpenALPR executable not found")
        return
        
    print(f"   📍 Checking config: {config_path}")
    if os.path.exists(config_path):
        print("   ✅ OpenALPR config found")
    else:
        print("   ⚠️ OpenALPR config not found (may use defaults)")
    
    # Test with help command
    try:
        import subprocess
        result = subprocess.run([openalpr_path, "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or "OpenALPR" in result.stdout:
            print("   ✅ OpenALPR is functional")
        else:
            print("   ⚠️ OpenALPR may have issues")
            print(f"   Return code: {result.returncode}")
            
    except Exception as e:
        print(f"   ❌ Error testing OpenALPR: {e}")

if __name__ == "__main__":
    main()