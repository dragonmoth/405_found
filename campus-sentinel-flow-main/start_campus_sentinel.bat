@echo off
echo ===============================================
echo      Campus Sentinel Flow - Startup Script
echo ===============================================
echo.

:: Check if virtual environment exists
if not exist "backend\venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

:: Start backend in new window
echo Starting Flask Backend Server...
start "Campus Sentinel Backend" cmd /k "cd backend && venv\Scripts\activate && pip install -r requirements.txt && python app.py"

:: Wait a moment for backend to start
timeout /t 3 /nobreak > nul

:: Install frontend dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    call npm install socket.io-client
)

:: Start frontend in new window
echo Starting React Frontend...
start "Campus Sentinel Frontend" cmd /k "npm run dev"

echo.
echo ===============================================
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo ===============================================
echo.
echo Press any key to exit this window...
pause > nul