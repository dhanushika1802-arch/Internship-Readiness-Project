@echo off
echo ====================================================================
echo   AI-Powered Internship Readiness System Startup
echo ====================================================================
echo.

echo Starting Flask Backend Server...
start cmd /k "title ReadyUp AI Backend && cd backend && .\venv\Scripts\python.exe app.py"

echo Starting React Frontend Server...
start cmd /k "title ReadyUp AI Frontend && cd frontend && npm.cmd run dev"

echo.
echo ====================================================================
echo   Servers launched!
echo   - Backend API is running on: http://127.0.0.1:5000
echo   - Frontend Client is running on: http://localhost:5173
echo ====================================================================
pause
