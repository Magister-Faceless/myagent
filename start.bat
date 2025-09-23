@echo off
REM Start both backend and frontend servers for MyAgents application
REM This batch file starts both servers in separate command prompt windows

echo.
echo 🚀 Starting MyAgents Development Environment...
echo.

REM Get the directory where this batch file is located
set "PROJECT_ROOT=%~dp0"
set "BACKEND_PATH=%PROJECT_ROOT%backend"
set "FRONTEND_PATH=%PROJECT_ROOT%frontend"

REM Check if directories exist
if not exist "%BACKEND_PATH%" (
    echo ❌ Backend directory not found: %BACKEND_PATH%
    pause
    exit /b 1
)

if not exist "%FRONTEND_PATH%" (
    echo ❌ Frontend directory not found: %FRONTEND_PATH%
    pause
    exit /b 1
)

REM Start backend server
echo 🔧 Starting Backend Server...
start "MyAgents Backend" cmd /k "cd /d "%BACKEND_PATH%" && .\.venv\Scripts\activate && echo 🚀 Backend Server Starting... && echo API: http://127.0.0.1:2024 && langgraph dev"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🎨 Starting Frontend Server...
start "MyAgents Frontend" cmd /k "cd /d "%FRONTEND_PATH%" && echo 🎨 Frontend Server Starting... && echo Local: http://localhost:3000 && npm run dev"

REM Wait for servers to start
timeout /t 5 /nobreak >nul

echo.
echo 🎉 MyAgents Development Environment Started!
echo.
echo 📍 Server URLs:
echo    Backend API: http://127.0.0.1:2024
echo    Frontend UI: http://localhost:3000
echo    LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
echo.
echo 💡 Tips:
echo    - Both servers are running in separate command prompt windows
echo    - Close the windows or press Ctrl+C to stop the servers
echo    - Check the individual windows for logs and errors
echo.
echo Press any key to exit this script (servers will continue running)...
pause >nul
