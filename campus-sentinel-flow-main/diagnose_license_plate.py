#!/usr/bin/env python3
"""
Quick License Plate Detection Diagnostic
"""

import sys
import os
import subprocess
import json

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_paths():
    """Test all relevant paths"""
    print("🔍 Path Diagnostics")
    print("=" * 40)
    
    # Get the base directory (hacknova)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Base directory: {base_dir}")
    
    # Test OpenALPR path
    openalpr_path = os.path.join(base_dir, "openalpr_64", "alpr.exe")
    print(f"OpenALPR path: {openalpr_path}")
    print(f"OpenALPR exists: {os.path.exists(openalpr_path)}")
    
    # Test config path
    config_path = os.path.join(base_dir, "openalpr_64", "openalpr.conf")
    print(f"Config path: {config_path}")
    print(f"Config exists: {os.path.exists(config_path)}")
    
    return openalpr_path, config_path

def test_openalpr_direct(openalpr_path, config_path):
    """Test OpenALPR directly"""
    print("\n🔧 OpenALPR Direct Test")
    print("=" * 40)
    
    # Create a simple test image
    import cv2
    import numpy as np
    import tempfile
    
    test_img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    cv2.rectangle(test_img, (50, 50), (350, 150), (0, 0, 0), 2)
    cv2.putText(test_img, 'ABC-1234', (80, 110), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Save test image
    temp_path = os.path.join(tempfile.gettempdir(), "test_plate_img.jpg")
    cv2.imwrite(temp_path, test_img)
    print(f"Test image saved: {temp_path}")
    
    try:
        # Run OpenALPR
        cmd = [
            openalpr_path,
            "-j",  # JSON output
            "-n", "10",  # Top 10 results
            "-c", "us",  # US region
            "--config", config_path,
            temp_path
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
            
        # Try to parse JSON
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                print(f"Parsed JSON: {data}")
                
                if "results" in data and len(data["results"]) > 0:
                    print("✅ License plate detection working!")
                    for result_item in data["results"]:
                        if "candidates" in result_item:
                            for candidate in result_item["candidates"]:
                                plate = candidate.get("plate", "")
                                conf = candidate.get("confidence", 0)
                                print(f"   Found: '{plate}' (confidence: {conf:.1f}%)")
                else:
                    print("⚠️ OpenALPR working but no plates detected in test image")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
        else:
            print("❌ No output from OpenALPR")
            
    except subprocess.TimeoutExpired:
        print("❌ OpenALPR timeout")
    except Exception as e:
        print(f"❌ Error running OpenALPR: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_backend_integration():
    """Test backend integration"""
    print("\n🔗 Backend Integration Test")
    print("=" * 40)
    
    try:
        from app import detect_license_plate, OPENALPR_PATH
        import cv2
        import numpy as np
        
        print(f"Backend OpenALPR path: {OPENALPR_PATH}")
        print(f"Backend path exists: {os.path.exists(OPENALPR_PATH)}")
        
        # Create test image
        test_img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        cv2.rectangle(test_img, (50, 50), (350, 150), (0, 0, 0), 2)
        cv2.putText(test_img, 'ABC-1234', (80, 110), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        print("Testing backend license plate detection...")
        result = detect_license_plate(test_img)
        print(f"Backend result: {result}")
        
        if result[0] is not None:
            print("✅ Backend license plate detection working!")
        else:
            print("❌ Backend license plate detection not working")
            
    except Exception as e:
        print(f"❌ Backend integration error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main diagnostic function"""
    print("🏫 Campus Sentinel - License Plate Diagnostic")
    print("=" * 60)
    
    # Test paths
    openalpr_path, config_path = test_paths()
    
    if os.path.exists(openalpr_path) and os.path.exists(config_path):
        # Test OpenALPR directly
        test_openalpr_direct(openalpr_path, config_path)
        
        # Test backend integration
        test_backend_integration()
    else:
        print("❌ OpenALPR or config files not found - cannot continue")
    
    print("\n🎯 Diagnostic completed!")

if __name__ == "__main__":
    main()