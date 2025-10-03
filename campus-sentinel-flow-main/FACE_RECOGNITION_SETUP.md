# 👤 Facial Recognition Setup Guide

## 🎯 **Authorized Students Only**

This system is configured to **ONLY** grant facial recognition access to:
- **👩 Mihika Patil** (ID: 23102069) - `mihika.jpg`
- **👨 Vinayak Kundar** (ID: 23101188) - `vinayak.jpeg`

**All other faces will be DENIED access** - ensuring maximum security!

---

## 🚀 **Quick Setup (3 Steps)**

### **Step 1: Install Dependencies**
```bash
pip install --user opencv-contrib-python
```

### **Step 2: Place Photos & Import Data**
```bash
# Place mihika.jpg and vinayak.jpeg in campus-sentinel-flow-main folder
cd campus-sentinel-flow-main

# Import student data
python import_students.py

# Setup face recognition training
python setup_face_recognition.py
```

### **Step 3: Test & Run**
```bash
# Test the setup
python test_face_recognition.py

# Start the system
cd backend
python app.py
```

---

## 📋 **Detailed Setup Instructions**

### **Prerequisites**
- ✅ Python 3.8+
- ✅ OpenCV with contrib module
- ✅ Photos: `mihika.jpg` and `vinayak.jpeg`
- ✅ Backend database initialized

### **1. Photo Preparation**

**Required Files:**
- `mihika.jpg` - Clear photo of Mihika Patil's face
- `vinayak.jpeg` - Clear photo of Vinayak Kundar's face

**Photo Requirements:**
- 📸 **Clear face visibility** - no sunglasses, hats, or obstructions
- 💡 **Good lighting** - avoid shadows on face
- 📐 **Face centered** - person looking at camera
- 🎯 **High resolution** - at least 200x200 pixels
- 👤 **Single person** - only target person in photo

**Where to Place:**
```
campus-sentinel-flow-main/
├── mihika.jpg          ← Place here
├── vinayak.jpeg        ← Place here
├── setup_face_recognition.py
└── ...
```

### **2. Install Dependencies**

Based on the memory about OpenCV face recognition setup:

```bash
# Install OpenCV with face recognition module
pip install --user opencv-contrib-python

# Verify installation
python -c "import cv2; print('OpenCV:', cv2.__version__); print('Face module:', hasattr(cv2, 'face'))"
```

### **3. Import Student Database**

```bash
cd campus-sentinel-flow-main
python import_students.py
```

This will:
- ✅ Import all students from CSV
- ✅ Mark only Mihika and Vinayak as authorized for face recognition
- ✅ Create proper database structure

**Expected Output:**
```
📊 Import Summary:
   Total students imported: 102
   Authorized for face recognition: 2
   Face recognition enabled for:
     - Mihika Patil (23102069)
     - Vinayak Kundar (23101188)
```

### **4. Train Face Recognition**

```bash
python setup_face_recognition.py
```

This will:
- 🔍 **Extract faces** from photos using Haar cascades
- 🎯 **Create training variations** (brightness, contrast, blur adjustments)
- 🧠 **Train LBPH recognizers** for each person
- 💾 **Save classifiers** as `mihika_classifier.xml` and `vinayak_classifier.xml`
- 🗑️ **Remove old classifiers** to prevent unauthorized access

**Expected Output:**
```
✅ Found 1 face(s) in mihika.jpg
✅ Saved 30 training images for Mihika Patil
✅ Face recognizer trained and saved: mihika_classifier.xml

✅ Found 1 face(s) in vinayak.jpeg  
✅ Saved 30 training images for Vinayak Kundar
✅ Face recognizer trained and saved: vinayak_classifier.xml
```

### **5. Test the System**

```bash
python test_face_recognition.py
```

This comprehensive test will verify:
- ✅ OpenCV installation
- ✅ Trained classifiers
- ✅ Database setup
- ✅ Camera access
- ✅ Face detection
- ✅ Security (unauthorized access denied)

**Expected Test Results:**
```
✅ OpenCV version: 4.x.x
✅ OpenCV face module is available
✅ Classifier loaded successfully: mihika
✅ Classifier loaded successfully: vinayak
✅ Mihika Patil (23102069) - Authorized for face recognition
✅ Vinayak Kundar (23101188) - Authorized for face recognition
✅ Camera accessed successfully
✅ Face cascade loaded successfully
✅ Face detection working
✅ Access granted: Mihika Patil (23102069)
✅ Access granted: Vinayak Kundar (23101188)
✅ Security working: Unauthorized access properly denied
```

---

## 🔒 **Security Features**

### **Strict Authorization**
- ❌ **No wildcards** - only exact trained faces recognized
- ❌ **No partial matches** - prevents false positives
- ❌ **No fallback recognition** - unknown faces always denied
- ✅ **Database verification** - double-checks student authorization

### **Face Name Mapping**
```python
FACE_NAME_MAPPING = {
    'mihika': '23102069',   # Mihika Patil
    'vinayak': '23101188'   # Vinayak Kundar
}
```

### **Access Control Logic**
1. 🔍 **Face detected** by Haar cascade
2. 🧠 **Face recognized** by trained LBPH model
3. 🔐 **Name mapped** to authorized student ID
4. 💾 **Database verified** for active status
5. ✅ **Access granted** only if all checks pass

---

## 🎮 **Running the System**

### **Start Backend**
```bash
cd backend
venv\Scripts\activate  # If using virtual environment
python app.py
```

### **Open Frontend**
```bash
# In browser, go to:
http://localhost:5173/monitoring
```

### **Test Face Recognition**
1. 📹 Click "Start Camera"
2. 🔍 Click "Start Detection"  
3. 👤 Show face to camera
4. 📝 Check logs for recognition results

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"OpenCV face module not available"**
```bash
pip uninstall opencv-python
pip install --user opencv-contrib-python
```

#### **"No faces detected in photo"**
- ✅ Ensure face is clearly visible
- ✅ Good lighting conditions
- ✅ Face looking at camera
- ✅ No sunglasses/hats/obstructions

#### **"Classifier not found"**
- ✅ Run `python setup_face_recognition.py` again
- ✅ Check photos are in correct location
- ✅ Verify photo file names match exactly

#### **"Database error"**
- ✅ Run `python import_students.py` first
- ✅ Check CSV file exists
- ✅ Ensure backend folder exists

### **Debug Commands**

```bash
# Test OpenCV installation
python -c "import cv2; print('Face module:', hasattr(cv2, 'face'))"

# Check trained classifiers
ls "C:\Users\rites\Project\hacknova\FaceRecognition-GUI-APP-master\data\classifiers\"

# Test database
python -c "import sqlite3; c=sqlite3.connect('backend/campus_sentinel.db'); print(c.execute('SELECT name FROM students WHERE face_trained=1').fetchall())"

# Test camera
python -c "import cv2; c=cv2.VideoCapture(0); print('Camera OK:', c.read()[0]); c.release()"
```

---

## 📊 **Expected System Behavior**

### **Authorized Access (Mihika/Vinayak)**
```
🔍 Face detected
🧠 Recognized as: mihika
✅ Access granted: Mihika Patil (23102069)
📝 Logged to database
🔔 Real-time alert sent to dashboard
```

### **Unauthorized Access (Anyone Else)**
```
🔍 Face detected  
❌ Unknown face or unrecognized
❌ Access denied
📝 Security alert logged
🚨 Admin notification sent
```

### **No Face Detected**
```
📷 Camera active
🔍 No face in frame
⏳ Waiting for detection...
```

---

## 🎯 **Success Indicators**

Your system is ready when you see:

✅ **Two classifier files created:**
- `mihika_classifier.xml`
- `vinayak_classifier.xml`

✅ **Database shows 2 authorized students:**
- Mihika Patil (23102069) 
- Vinayak Kundar (23101188)

✅ **Test script passes all checks:**
- OpenCV working
- Classifiers loaded
- Camera accessible
- Security verified

✅ **Live system shows:**
- Camera feed active
- Face detection working
- Recognition alerts appearing
- Database logging entries

---

## 🚀 **Next Steps After Setup**

1. **Monitor Live System**
   - Watch real-time detection alerts
   - Check access logs in admin dashboard
   - Verify only authorized faces get access

2. **Fine-tune if Needed**
   - Adjust lighting for better recognition
   - Retrain with additional photos if needed
   - Monitor confidence scores

3. **Security Validation**
   - Test with different people
   - Verify unauthorized access is blocked
   - Check all logs are properly recorded

**Remember: Only Mihika Patil and Vinayak Kundar will be granted access through facial recognition!**