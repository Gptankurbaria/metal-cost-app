@echo off
TITLE Shanghai Metals Cost Analysis App
echo Starting Manufacturing Cost App...
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python to run this application.
    pause
    exit
)

:: Install Dependencies
echo Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Could not install dependencies. App might fail if libraries are missing.
    echo.
)

:: Run App
echo.
echo Launching Dashboard...
echo You can also access this from other computers on your network using your IP address.
echo.
streamlit run app.py
pause
