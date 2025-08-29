@echo off
setlocal enabledelayedexpansion

REM ========================================
REM Smart Image Generation - Installer
REM ========================================

echo.
echo ========================================
echo Smart Image Generation Dependencies
echo ========================================

REM Check if Python is available
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if install_dependencies.py exists
echo [2/4] Checking installation script...
if not exist "install_dependencies.py" (
    echo ERROR: install_dependencies.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM Run the installation
echo [3/4] Installing dependencies...
python install_dependencies.py
if errorlevel 1 (
    echo ERROR: Installation failed
    echo Please check the error messages above
    pause
    exit /b 1
)

REM Installation completed
echo [4/4] Installation completed successfully!
echo You can now run the Smart Image Generation system.
pause
