@echo off
echo ================================================
echo    HYPERTRADER 1.5 - ONE-CLICK SETUP
echo ================================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
) else (
    echo Please run this batch file as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit
)

:: Create main directory
echo [1/10] Creating Hypertrader directory...
if not exist "C:\Hypertrader" mkdir "C:\Hypertrader"
cd /d "C:\Hypertrader"

:: Download and install Python if not exists
echo [2/10] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python already installed
) else (
    echo Downloading Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe'"
    echo Installing Python...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python installed - Please restart this batch file
    pause
    exit
)

:: Download and install Node.js if not exists
echo [3/10] Checking Node.js installation...
node --version >nul 2>&1
if %errorLevel% == 0 (
    echo Node.js already installed
) else (
    echo Downloading Node.js...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.19.0/node-v18.19.0-x64.msi' -OutFile 'node-installer.msi'"
    echo Installing Node.js...
    msiexec /i node-installer.msi /quiet
    del node-installer.msi
    echo Node.js installed - Please restart this batch file
    pause
    exit
)

:: Download and install MongoDB if not exists
echo [4/10] Checking MongoDB installation...
if exist "C:\Program Files\MongoDB" (
    echo MongoDB already installed
) else (
    echo Downloading MongoDB...
    powershell -Command "Invoke-WebRequest -Uri 'https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.4-signed.msi' -OutFile 'mongodb-installer.msi'"
    echo Installing MongoDB...
    msiexec /i mongodb-installer.msi /quiet
    del mongodb-installer.msi
)

:: Start MongoDB service
echo [5/10] Starting MongoDB service...
net start MongoDB >nul 2>&1

:: Create project structure
echo [6/10] Setting up project structure...
if not exist "backend" mkdir "backend"
if not exist "frontend" mkdir "frontend"

:: Create backend files
echo [7/10] Creating backend files...
cd backend

:: Create requirements.txt
echo fastapi==0.110.1> requirements.txt
echo uvicorn==0.25.0>> requirements.txt
echo boto3^>=1.34.129>> requirements.txt
echo requests-oauthlib^>=2.0.0>> requirements.txt
echo cryptography^>=42.0.8>> requirements.txt
echo python-dotenv^>=1.0.1>> requirements.txt
echo pymongo==4.5.0>> requirements.txt
echo pydantic^>=2.6.4>> requirements.txt
echo email-validator^>=2.2.0>> requirements.txt
echo pyjwt^>=2.10.1>> requirements.txt
echo passlib^>=1.7.4>> requirements.txt
echo tzdata^>=2024.2>> requirements.txt
echo motor==3.3.1>> requirements.txt
echo pytest^>=8.0.0>> requirements.txt
echo black^>=24.1.1>> requirements.txt
echo isort^>=5.13.2>> requirements.txt
echo flake8^>=7.0.0>> requirements.txt
echo mypy^>=1.8.0>> requirements.txt
echo python-jose^>=3.3.0>> requirements.txt
echo requests^>=2.31.0>> requirements.txt
echo pandas^>=2.2.0>> requirements.txt
echo numpy^>=1.26.0>> requirements.txt
echo python-multipart^>=0.0.9>> requirements.txt
echo jq^>=1.6.0>> requirements.txt
echo typer^>=0.9.0>> requirements.txt
echo hyperliquid-python-sdk^>=1.0.0>> requirements.txt
echo websockets^>=12.0>> requirements.txt

:: Create .env file
echo MONGO_URL=mongodb://localhost:27017/hypertrader> .env
echo HYPERLIQUID_PRIVATE_KEY="">> .env
echo HYPERLIQUID_ENV="mainnet">> .env
echo HYPERLIQUID_TESTNET_URL="https://api.hyperliquid-testnet.xyz">> .env
echo HYPERLIQUID_MAINNET_URL="https://api.hyperliquid.xyz">> .env
echo HYPERLIQUID_WS_TESTNET="wss://api.hyperliquid-testnet.xyz/ws">> .env
echo HYPERLIQUID_WS_MAINNET="wss://api.hyperliquid.xyz/ws">> .env

:: Create Python virtual environment and install dependencies
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt

:: Create basic server.py
echo Creating server.py...
(
echo from fastapi import FastAPI
echo from fastapi.middleware.cors import CORSMiddleware
echo import motor.motor_asyncio
echo import os
echo from dotenv import load_dotenv
echo.
echo load_dotenv^(^)
echo.
echo app = FastAPI^(title="Hypertrader 1.5 API", version="1.5.0"^)
echo.
echo app.add_middleware^(
echo     CORSMiddleware,
echo     allow_origins=["*"],
echo     allow_credentials=True,
echo     allow_methods=["*"],
echo     allow_headers=["*"],
echo ^)
echo.
echo MONGO_URL = os.getenv^("MONGO_URL"^)
echo client = motor.motor_asyncio.AsyncIOMotorClient^(MONGO_URL^)
echo db = client.hypertrader
echo.
echo @app.get^("/api/"^)
echo async def root^(^):
echo     return {"message": "Hypertrader 1.5 API is running"}
echo.
echo @app.get^("/api/health"^)
echo async def health_check^(^):
echo     return {"status": "healthy"}
echo.
echo if __name__ == "__main__":
echo     import uvicorn
echo     uvicorn.run^(app, host="0.0.0.0", port=8001^)
) > server.py

cd ..

:: Create frontend files
echo [8/10] Creating frontend files...
cd frontend

:: Create package.json
(
echo {
echo   "name": "hypertrader-frontend",
echo   "version": "1.5.0",
echo   "private": true,
echo   "dependencies": {
echo     "react": "^18.2.0",
echo     "react-dom": "^18.2.0",
echo     "react-scripts": "5.0.1",
echo     "react-router-dom": "^6.8.0",
echo     "axios": "^1.3.0",
echo     "tailwindcss": "^3.2.0",
echo     "autoprefixer": "^10.4.0",
echo     "postcss": "^8.4.0"
echo   },
echo   "scripts": {
echo     "start": "react-scripts start",
echo     "build": "react-scripts build",
echo     "test": "react-scripts test",
echo     "eject": "react-scripts eject"
echo   },
echo   "eslintConfig": {
echo     "extends": [
echo       "react-app",
echo       "react-app/jest"
echo     ]
echo   },
echo   "browserslist": {
echo     "production": [
echo       "^>0.2%%",
echo       "not dead",
echo       "not op_mini all"
echo     ],
echo     "development": [
echo       "last 1 chrome version",
echo       "last 1 firefox version",
echo       "last 1 safari version"
echo     ]
echo   }
echo }
) > package.json

:: Create .env file
echo REACT_APP_BACKEND_URL=http://localhost:8001> .env

:: Create basic React structure
if not exist "src" mkdir "src"
if not exist "public" mkdir "public"

:: Create index.html
(
echo ^<!DOCTYPE html^>
echo ^<html lang="en"^>
echo ^<head^>
echo   ^<meta charset="utf-8" /^>
echo   ^<meta name="viewport" content="width=device-width, initial-scale=1" /^>
echo   ^<title^>Hypertrader 1.5^</title^>
echo ^</head^>
echo ^<body^>
echo   ^<div id="root"^>^</div^>
echo ^</body^>
echo ^</html^>
) > public\index.html

:: Create index.js
(
echo import React from 'react';
echo import ReactDOM from 'react-dom/client';
echo import App from './App';
echo.
echo const root = ReactDOM.createRoot^(document.getElementById^('root'^)^);
echo root.render^(^<App /^>^);
) > src\index.js

:: Create App.js
(
echo import React, { useState, useEffect } from 'react';
echo import axios from 'axios';
echo.
echo function App^(^) {
echo   const [status, setStatus] = useState^('Loading..'^);
echo.
echo   useEffect^(^(^) =^> {
echo     axios.get^('http://localhost:8001/api/health'^)
echo       .then^(response =^> setStatus^('✅ Connected to Backend!'^)^)
echo       .catch^(error =^> setStatus^('❌ Backend Connection Failed'^)^);
echo   }, []^);
echo.
echo   return ^(
echo     ^<div style={{padding: '20px', fontFamily: 'Arial'}^}^>
echo       ^<h1^>🚀 Hypertrader 1.5^</h1^>
echo       ^<p^>Status: {status}^</p^>
echo       ^<p^>Backend API: ^<a href="http://localhost:8001/api/health" target="_blank"^>http://localhost:8001/api/health^</a^>^</p^>
echo       ^<p^>Frontend: ^<a href="http://localhost:3000" target="_blank"^>http://localhost:3000^</a^>^</p^>
echo     ^</div^>
echo   ^);
echo }
echo.
echo export default App;
) > src\App.js

:: Install Node.js dependencies
echo Installing Node.js dependencies...
call npm install

cd ..

:: Create startup scripts
echo [9/10] Creating startup scripts...

:: Create start_backend.bat
(
echo @echo off
echo echo Starting Hypertrader Backend...
echo cd /d "C:\Hypertrader\backend"
echo call venv\Scripts\activate
echo python server.py
) > start_backend.bat

:: Create start_frontend.bat
(
echo @echo off
echo echo Starting Hypertrader Frontend...
echo cd /d "C:\Hypertrader\frontend"
echo call npm start
) > start_frontend.bat

:: Create start_all.bat
(
echo @echo off
echo echo ================================================
echo echo    STARTING HYPERTRADER 1.5
echo echo ================================================
echo.
echo Starting MongoDB...
echo net start MongoDB ^>nul 2^>^&1
echo.
echo Starting Backend...
echo start "Hypertrader Backend" cmd /k "cd /d C:\Hypertrader\backend && call venv\Scripts\activate && python server.py"
echo.
echo Waiting for backend to start...
echo timeout /t 5 /nobreak ^>nul
echo.
echo Starting Frontend...
echo start "Hypertrader Frontend" cmd /k "cd /d C:\Hypertrader\frontend && npm start"
echo.
echo Waiting for frontend to start...
echo timeout /t 10 /nobreak ^>nul
echo.
echo Opening Browser...
echo start http://localhost:3000
echo start http://localhost:8001/api/health
echo.
echo ================================================
echo    HYPERTRADER 1.5 IS READY!
echo ================================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8001/api/health
echo.
echo Keep this window open to see the status
echo Close this window to stop all services
echo ================================================
pause
) > start_all.bat

:: Final step - Launch everything
echo [10/10] Launching Hypertrader 1.5...
echo.
echo ================================================
echo    SETUP COMPLETE!
echo ================================================
echo.
echo Created files in: C:\Hypertrader\
echo.
echo TO START HYPERTRADER:
echo   Double-click: start_all.bat
echo.
echo OR manually:
echo   1. Double-click: start_backend.bat
echo   2. Double-click: start_frontend.bat
echo   3. Open browser to: http://localhost:3000
echo.
echo ================================================

:: Ask if user wants to start now
echo.
set /p choice="Start Hypertrader now? (y/n): "
if /i "%choice%"=="y" (
    echo Starting Hypertrader...
    call start_all.bat
) else (
    echo.
    echo You can start Hypertrader later by running: start_all.bat
    echo.
)

echo.
echo Setup completed successfully!
pause