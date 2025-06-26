@echo off
echo ================================================
echo    HYPERTRADER 1.5 - WINDOWS INSTALLER
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

:: Create requirements.txt with FIXED versions
echo fastapi==0.110.1> requirements.txt
echo uvicorn==0.25.0>> requirements.txt
echo python-dotenv==1.1.1>> requirements.txt
echo pymongo==4.5.0>> requirements.txt
echo pydantic==2.6.4>> requirements.txt
echo motor==3.3.1>> requirements.txt
echo requests==2.31.0>> requirements.txt
echo python-multipart==0.0.9>> requirements.txt
echo hyperliquid-python-sdk==0.15.0>> requirements.txt
echo websockets==12.0>> requirements.txt

:: Create .env file
echo MONGO_URL=mongodb://localhost:27017/hypertrader> .env
echo HYPERLIQUID_PRIVATE_KEY="">> .env
echo HYPERLIQUID_ENV="mainnet">> .env

:: Create Python virtual environment and install dependencies
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Upgrade pip first to avoid issues
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing Python dependencies...
pip install -r requirements.txt

:: Create minimal working server.py
echo Creating server.py...
(
echo from fastapi import FastAPI
echo from fastapi.middleware.cors import CORSMiddleware
echo import os
echo from dotenv import load_dotenv
echo from datetime import datetime
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
echo # Mock portfolio data
echo MOCK_PORTFOLIO = {
echo     "account_value": 124.84,
echo     "available_balance": 124.84,
echo     "margin_used": 0.0,
echo     "total_pnl": 124.84,
echo     "daily_pnl": 0.0,
echo     "positions": []
echo }
echo.
echo @app.get^("/api/"^)
echo async def root^(^):
echo     return {"message": "Hypertrader 1.5 API is running", "status": "✅ Ready"}
echo.
echo @app.get^("/api/health"^)
echo async def health_check^(^):
echo     return {"status": "healthy", "timestamp": datetime.utcnow^(^).isoformat^(^)}
echo.
echo @app.get^("/api/portfolio"^)
echo async def get_portfolio^(^):
echo     return {"success": True, "message": "Portfolio retrieved", "data": MOCK_PORTFOLIO}
echo.
echo @app.get^("/api/market/{coin}"^)
echo async def get_market_data^(coin: str^):
echo     prices = {"BTC": 45000, "ETH": 3200, "SOL": 100}
echo     price = prices.get^(coin.upper^(^), 100^)
echo     return {
echo         "success": True,
echo         "data": {
echo             "coin": coin.upper^(^),
echo             "price": price,
echo             "change_24h": 2.5
echo         }
echo     }
echo.
echo if __name__ == "__main__":
echo     import uvicorn
echo     print^("🚀 Starting Hypertrader 1.5 Backend..."^)
echo     print^("📡 API available at: http://localhost:8001"^)
echo     uvicorn.run^(app, host="0.0.0.0", port=8001^)
) > server.py

cd ..

:: Create frontend files
echo [8/10] Creating frontend files...
cd frontend

:: Create package.json with stable versions
(
echo {
echo   "name": "hypertrader-frontend",
echo   "version": "1.5.0",
echo   "private": true,
echo   "dependencies": {
echo     "react": "18.2.0",
echo     "react-dom": "18.2.0",
echo     "react-scripts": "5.0.1",
echo     "axios": "1.3.0"
echo   },
echo   "scripts": {
echo     "start": "react-scripts start",
echo     "build": "react-scripts build"
echo   },
echo   "browserslist": {
echo     "production": ["^>0.2%%", "not dead"],
echo     "development": ["last 1 chrome version"]
echo   }
echo }
) > package.json

:: Create .env file
echo REACT_APP_BACKEND_URL=http://localhost:8001> .env

:: Create React structure
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
echo   ^<style^>
echo     body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: white; }
echo     .container { max-width: 800px; margin: 0 auto; }
echo     .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
echo     .connected { background: #2d5a27; border: 1px solid #4caf50; }
echo     .disconnected { background: #5a2727; border: 1px solid #f44336; }
echo     .card { background: #16213e; padding: 20px; margin: 15px 0; border-radius: 8px; border: 1px solid #0f4c75; }
echo     a { color: #4fc3f7; text-decoration: none; }
echo     .btn { background: #3f51b5; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
echo   ^</style^>
echo ^</head^>
echo ^<body^>
echo   ^<div id="root"^>^</div^>
echo ^</body^>
echo ^</html^>
) > public\index.html

:: Create App.js
(
echo import React, { useState, useEffect } from 'react';
echo import axios from 'axios';
echo.
echo function App^(^) {
echo   const [status, setStatus] = useState^('Loading..'^);
echo   const [portfolio, setPortfolio] = useState^(null^);
echo   const [connected, setConnected] = useState^(false^);
echo.
echo   useEffect^(^(^) =^> {
echo     checkConnection^(^);
echo     const interval = setInterval^(checkConnection, 5000^);
echo     return ^(^) =^> clearInterval^(interval^);
echo   }, []^);
echo.
echo   const checkConnection = async ^(^) =^> {
echo     try {
echo       await axios.get^('http://localhost:8001/api/health'^);
echo       setStatus^('✅ Connected to Backend!'^);
echo       setConnected^(true^);
echo       
echo       const portfolioResponse = await axios.get^('http://localhost:8001/api/portfolio'^);
echo       setPortfolio^(portfolioResponse.data.data^);
echo     } catch ^(error^) {
echo       setStatus^('❌ Backend Connection Failed'^);
echo       setConnected^(false^);
echo     }
echo   };
echo.
echo   return ^(
echo     ^<div className="container"^>
echo       ^<h1^>🚀 Hypertrader 1.5 Trading Platform^</h1^>
echo       
echo       ^<div className={`status ${connected ? 'connected' : 'disconnected'}`}^>
echo         ^<strong^>Status: {status}^</strong^>
echo       ^</div^>
echo.
echo       {connected ^&^& portfolio ^&^& ^(
echo         ^<div className="card"^>
echo           ^<h2^>📊 Portfolio Overview^</h2^>
echo           ^<p^>^<strong^>Account Value:^</strong^> ${portfolio.account_value}^</p^>
echo           ^<p^>^<strong^>Available Balance:^</strong^> ${portfolio.available_balance}^</p^>
echo           ^<p^>^<strong^>Total PnL:^</strong^> ${portfolio.total_pnl}^</p^>
echo         ^</div^>
echo       ^)}
echo       
echo       ^<div className="card"^>
echo         ^<h2^>🔗 API Links^</h2^>
echo         ^<p^>^<a href="http://localhost:8001/api/health" target="_blank"^>Health Check^</a^>^</p^>
echo         ^<p^>^<a href="http://localhost:8001/api/portfolio" target="_blank"^>Portfolio API^</a^>^</p^>
echo         ^<button className="btn" onClick={checkConnection}^>🔄 Refresh^</button^>
echo       ^</div^>
echo     ^</div^>
echo   ^);
echo }
echo.
echo export default App;
) > src\App.js

:: Create index.js
(
echo import React from 'react';
echo import ReactDOM from 'react-dom/client';
echo import App from './App';
echo.
echo const root = ReactDOM.createRoot^(document.getElementById^('root'^)^);
echo root.render^(^<App /^>^);
) > src\index.js

:: Install Node.js dependencies
echo Installing Node.js dependencies...
npm install --legacy-peer-deps

cd ..

:: Create startup scripts
echo [9/10] Creating startup scripts...

(
echo @echo off
echo cd /d "C:\Hypertrader\backend"
echo call venv\Scripts\activate
echo python server.py
echo pause
) > start_backend.bat

(
echo @echo off
echo cd /d "C:\Hypertrader\frontend"
echo npm start
echo pause
) > start_frontend.bat

(
echo @echo off
echo echo Starting Hypertrader 1.5...
echo net start MongoDB ^>nul 2^>^&1
echo start "Backend" cmd /k "cd /d C:\Hypertrader\backend && call venv\Scripts\activate && python server.py"
echo timeout /t 8 /nobreak ^>nul
echo start "Frontend" cmd /k "cd /d C:\Hypertrader\frontend && npm start"
echo timeout /t 15 /nobreak ^>nul
echo start http://localhost:3000
echo echo ✅ Hypertrader 1.5 is running!
echo pause
) > start_all.bat

echo [10/10] Setup completed!
echo.
echo ================================================
echo    HYPERTRADER 1.5 INSTALLED SUCCESSFULLY! ✅
echo ================================================
echo.
echo 📁 Location: C:\Hypertrader\
echo 🚀 To start: Double-click start_all.bat
echo 🌐 Frontend: http://localhost:3000
echo 📡 Backend: http://localhost:8001
echo.

set /p choice="🚀 Start Hypertrader now? (y/n): "
if /i "%choice%"=="y" (
    call start_all.bat
) else (
    echo Run start_all.bat when ready!
)

echo.
echo 🎉 Installation complete!
pause