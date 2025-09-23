# MyAgents - Quick Start Guide

This guide explains how to quickly start both the backend and frontend servers for the MyAgents application.

## 🚀 Quick Start Options

### Option 1: PowerShell Script (Recommended)
```powershell
.\start.ps1
```

### Option 2: Batch File
```cmd
start.bat
```

### Option 3: Manual Start (if scripts don't work)
```powershell
# Terminal 1 - Backend
cd backend
.\.venv\Scripts\Activate.ps1
langgraph dev

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 📍 Server URLs

Once started, you can access:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://127.0.0.1:2024
- **LangGraph Studio**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## 🔧 Prerequisites

Before running the scripts, ensure you have:

1. **Backend Setup**:
   - Python virtual environment created: `python -m venv backend\.venv`
   - Dependencies installed: `pip install -e .` (from backend directory)
   - Environment variables set (OPENROUTER_API_KEY, etc.)

2. **Frontend Setup**:
   - Node.js installed
   - Dependencies installed: `npm install` (from frontend directory)

## 💡 Features of the Start Scripts

- **Automatic Health Checks**: Verifies both servers are running
- **Dependency Checks**: Ensures virtual environment and node_modules exist
- **Separate Windows**: Each server runs in its own window for easy monitoring
- **Error Handling**: Clear error messages if something goes wrong
- **Cross-Platform**: PowerShell script works on Windows, macOS, and Linux

## 🛠️ Troubleshooting

### If the PowerShell script doesn't run:
```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If servers don't start:
1. Check that all prerequisites are met
2. Verify environment variables are set
3. Check the individual server windows for error messages
4. Try the manual start method

### Common Issues:
- **Backend fails**: Check OPENROUTER_API_KEY environment variable
- **Frontend fails**: Run `npm install` in the frontend directory
- **Port conflicts**: Make sure ports 3000 and 2024 are available

## 🔄 Stopping the Servers

To stop the servers:
1. Close the individual command prompt/PowerShell windows, or
2. Press `Ctrl+C` in each server window

## 📝 Notes

- The scripts will continue running the servers even after you close the main script window
- Both servers support hot reloading - changes to your code will be reflected automatically
- Check the individual server windows for logs and error messages
