<#
.SYNOPSIS
    Start both backend and frontend servers for MyAgents application
.DESCRIPTION
    This script starts the LangGraph backend server and Next.js frontend server
    in separate PowerShell windows for easy development.
.EXAMPLE
    .\start.ps1
#>

# Set error action preference
$ErrorActionPreference = "Stop"

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPath = Join-Path $ProjectRoot "backend"
$FrontendPath = Join-Path $ProjectRoot "frontend"

Write-Host "Starting MyAgents Development Environment..." -ForegroundColor Green
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Cyan

# Check if directories exist
if (-not (Test-Path $BackendPath)) {
    Write-Error "Backend directory not found: $BackendPath"
    exit 1
}

if (-not (Test-Path $FrontendPath)) {
    Write-Error "Frontend directory not found: $FrontendPath"
    exit 1
}

# Function to start backend
function Start-Backend {
    Write-Host "Starting Backend Server..." -ForegroundColor Yellow
    
    # Check if virtual environment exists
    $VenvPath = Join-Path $BackendPath ".venv"
    if (-not (Test-Path $VenvPath)) {
        Write-Error "Virtual environment not found at $VenvPath. Please run 'python -m venv .venv' in the backend directory first."
        return $false
    }
    
    # Create backend command
    $BackendCommand = "cd '$BackendPath'; .\.venv\Scripts\Activate.ps1; Write-Host 'Backend Server Starting...' -ForegroundColor Green; Write-Host 'API: http://127.0.0.1:2024' -ForegroundColor Cyan; langgraph dev"
    
    # Start backend in a new PowerShell window
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $BackendCommand)
    return $true
}

# Function to start frontend
function Start-Frontend {
    Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
    
    # Check if node_modules exists
    $NodeModulesPath = Join-Path $FrontendPath "node_modules"
    if (-not (Test-Path $NodeModulesPath)) {
        Write-Host "Node modules not found. Installing dependencies..." -ForegroundColor Yellow
        Set-Location $FrontendPath
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install frontend dependencies"
            return $false
        }
    }
    
    # Create frontend command
    $FrontendCommand = "cd '$FrontendPath'; Write-Host 'Frontend Server Starting...' -ForegroundColor Green; Write-Host 'Local: http://localhost:3000' -ForegroundColor Cyan; npm run dev"
    
    # Start frontend in a new PowerShell window
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $FrontendCommand)
    return $true
}

# Function to check if servers are running
function Test-ServerHealth {
    param(
        [int]$MaxAttempts = 15,
        [int]$DelaySeconds = 2
    )
    
    Write-Host "Checking server health..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            # Check backend (simplified check)
            $BackendHealthy = $false
            try {
                $BackendResponse = Invoke-WebRequest -Uri "http://127.0.0.1:2024" -TimeoutSec 3 -ErrorAction SilentlyContinue
                $BackendHealthy = $true
            } catch {
                # Backend might not have health endpoint, so any response is good
            }
            
            # Check frontend
            $FrontendHealthy = $false
            try {
                $FrontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -ErrorAction SilentlyContinue
                $FrontendHealthy = $true
            } catch {
                # Frontend not ready yet
            }
            
            if ($BackendHealthy -and $FrontendHealthy) {
                Write-Host "Both servers are healthy!" -ForegroundColor Green
                return $true
            }
            elseif ($BackendHealthy) {
                Write-Host "Backend healthy, waiting for frontend..." -ForegroundColor Yellow
            }
            elseif ($FrontendHealthy) {
                Write-Host "Frontend healthy, waiting for backend..." -ForegroundColor Yellow
            }
            else {
                Write-Host "Waiting for servers to start... ($i/$MaxAttempts)" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "Waiting for servers to start... ($i/$MaxAttempts)" -ForegroundColor Gray
        }
        
        Start-Sleep -Seconds $DelaySeconds
    }
    
    Write-Host "Servers may still be starting. Check the individual windows for status." -ForegroundColor Yellow
    return $false
}

# Main execution
try {
    # Start backend
    if (-not (Start-Backend)) {
        Write-Error "Failed to start backend server"
        exit 1
    }
    
    # Wait a moment for backend to initialize
    Start-Sleep -Seconds 3
    
    # Start frontend
    if (-not (Start-Frontend)) {
        Write-Error "Failed to start frontend server"
        exit 1
    }
    
    # Wait for servers to be ready
    Start-Sleep -Seconds 5
    
    # Check server health (optional)
    Test-ServerHealth | Out-Null
    
    Write-Host ""
    Write-Host "MyAgents Development Environment Started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Server URLs:" -ForegroundColor Cyan
    Write-Host "   Backend API: http://127.0.0.1:2024" -ForegroundColor White
    Write-Host "   Frontend UI: http://localhost:3000" -ForegroundColor White
    Write-Host "   LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024" -ForegroundColor White
    Write-Host ""
    Write-Host "Tips:" -ForegroundColor Yellow
    Write-Host "   - Both servers are running in separate windows" -ForegroundColor White
    Write-Host "   - Close the windows or press Ctrl+C to stop the servers" -ForegroundColor White
    Write-Host "   - Check the individual windows for logs and errors" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit this script (servers will continue running)..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
