# Campus Sentinel - AI-Powered Security System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

An intelligent campus security system that integrates **facial recognition**, **license plate detection**, and **student ID verification** into a unified real-time monitoring dashboard.

## 🎯 Features

### 🔐 Multi-Modal Security Detection
- **👤 Facial Recognition**: Real-time face detection and student identification
- **🚗 License Plate Recognition**: Automatic vehicle identification using OpenALPR
- **🆔 Student ID Scanner**: Barcode/QR code simulation for access control
- **📊 Cross-Reference Verification**: All detections verified against student database

### 📱 Real-Time Admin Dashboard
- **🎥 Live Camera Feed**: 30 FPS video streaming with detection overlays
- **📈 Live Statistics**: Real-time KPI updates every 5 seconds
- **🚨 Instant Alerts**: Socket.IO powered detection notifications
- **📊 Traffic Analytics**: Interactive hourly distribution charts
- **🔍 Access Logs**: Comprehensive search and filtering

### 🛠️ Advanced Features
- **🔄 Auto-Import**: CSV student database integration
- **🎮 Auto Scanner**: Continuous student ID generation for testing
- **⚡ Real-Time Sync**: Socket.IO for instant dashboard updates
- **🎯 Smart Simulation**: Fallback detection when hardware unavailable
- **📱 Responsive UI**: Modern React/TypeScript interface

## 🏗️ System Architecture

```
📹 Camera Feed ──┐
🆔 Student Scanner ──┼──► 🧠 AI Detection Engine ──► 💾 Database ──► 📊 Admin Dashboard
🚗 License Plates ──┘     (Face + LPR + ID)         (SQLite)      (React + Socket.IO)
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **OpenCV** with contrib modules
- **OpenALPR** (optional - simulation fallback available)

### 1. Clone Repository
```bash
git clone https://github.com/Em001hub/campus-sentinel.git
cd campus-sentinel
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup
```bash
# In new terminal
npm install
npm run dev
```

### 4. Import Student Data
```bash
python import_csv_now.py
```

### 5. Start Detection Testing
```bash
python auto_scanner.py
```

## 📖 Usage Guide

### 🎮 Admin Dashboard
1. **Access**: Open http://localhost:8081
2. **Start Camera**: Click "Start Camera" for live video feed
3. **Enable Detection**: Click "Start Detection" for AI processing
4. **Import Data**: Use "Import CSV Data" for student database
5. **Monitor**: Watch real-time statistics and access logs

### 🆔 Student ID Testing
```bash
# Automated continuous scanning
python auto_scanner.py

# Single student scan test
python test_scan.py

# Generate test detection activity
python quick_test_scans.py
```

### 📊 System Verification
```bash
# Complete system demo
python demo_system.py

# Verify dashboard statistics
python verify_dashboard_stats.py
```

## 📁 Project Structure

```
campus-sentinel/
├── 📂 backend/                 # Python Flask API
│   ├── app.py                 # Main backend server
│   ├── requirements.txt       # Python dependencies
│   └── campus_sentinel.db     # SQLite database
├── 📂 src/                    # React frontend
│   ├── 📂 components/         # Reusable UI components
│   ├── 📂 pages/             # Main application pages
│   │   └── AdminDashboard.tsx # Main dashboard component
│   └── 📂 lib/               # Utility functions
├── 📂 data/                   # AI models and classifiers
├── 🔧 auto_scanner.py         # Student ID simulator
├── 📊 demo_system.py          # Complete system demo
├── 📈 import_csv_now.py       # Database import utility
└── 📋 Untitled - Sheet1.csv   # Sample student data
```

## 🔧 Configuration

### Environment Variables
Create `.env` file in root directory:
```env
# Backend Configuration
FLASK_ENV=development
DATABASE_URL=sqlite:///campus_sentinel.db

# OpenALPR Configuration (optional)
OPENALPR_PATH=../openalpr_64/alpr.exe

# Camera Configuration
DEFAULT_CAMERA_INDEX=0
```

### Student Database Format
CSV file structure for student import:
```csv
student_id,name,year,division,roll_number,license_plate
23102824,Ankit Ayaan Patel,First,C,70,KAF 9279
23107924,Avni Divya Mehta,First,A,49,MH71HQ6925
```

## 📊 Dashboard Statistics

The admin dashboard displays real-time statistics:

- **📈 Total Entries Today**: Combined count from all detection types
- **🚗 Unique Vehicles**: Count of unique license plates detected
- **❌ Denied Access**: Count of denied access attempts
- **⏰ Peak Traffic Hour**: Hour with highest activity
- **📊 Traffic Analytics**: Interactive hourly distribution chart

## 🔌 API Endpoints

### Core Endpoints
- `GET /api/students` - List all students
- `GET /api/access_logs` - Retrieve access logs
- `GET /api/detection_stats` - Real-time statistics
- `POST /api/student_scan` - Process student ID scan
- `POST /api/start_camera` - Start camera feed
- `POST /api/toggle_detection` - Enable/disable detection

### WebSocket Events
- `new_access_log` - Real-time access log updates
- `detection_alert` - Instant detection notifications
- `camera_frame` - Live video stream

## 🧪 Testing

### Automated Testing
```bash
# Complete system test
python demo_system.py

# Dashboard statistics verification
python verify_dashboard_stats.py

# Camera detection test
python trigger_camera_detections.py
```

### Manual Testing
1. **Student ID Scanner**: Use `auto_scanner.py` for continuous testing
2. **Camera System**: Start camera through admin dashboard
3. **Database**: Import student data via CSV
4. **Real-time Updates**: Monitor dashboard for live statistics

## 🚀 Deployment

### Development
```bash
# Backend (Terminal 1)
cd backend && python app.py

# Frontend (Terminal 2)
npm run dev

# Testing (Terminal 3)
python auto_scanner.py
```

### Production
```bash
# Build frontend
npm run build

# Start production server
python -m gunicorn backend.app:app
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenCV** for computer vision capabilities
- **OpenALPR** for license plate recognition
- **React** and **TypeScript** for the frontend
- **Flask** and **Socket.IO** for real-time backend
- **ShadCN/UI** for beautiful UI components

## 📞 Support

For support and questions:
- 📧 **Email**: [Your Email]
- 🐛 **Issues**: [GitHub Issues](https://github.com/Em001hub/campus-sentinel/issues)
- 📖 **Documentation**: [Wiki](https://github.com/Em001hub/campus-sentinel/wiki)

---

**🎯 Campus Sentinel**: Making campus security intelligent, real-time, and comprehensive.