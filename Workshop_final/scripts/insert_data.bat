@echo off
echo ========================================
echo   E-commerce AI Product Advisor
echo   Data Insertion Script
echo ========================================
echo.

cd /d "%~dp0.."

echo Checking Python environment...
REM Activate virtual environment at root
call env\Scripts\activate.bat

echo.
echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo.
echo Checking required packages...
python -c "import pinecone, openai, streamlit" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Required packages not installed.
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Checking .env file...
if not exist .env (
    echo ERROR: .env file not found.
    echo Please copy .env.example to .env and configure your API keys.
    pause
    exit /b 1
)

echo.
echo Starting data insertion...
echo ========================================
python scripts\insert_sample_data.py

echo.
echo ========================================
if %errorlevel% equ 0 (
    echo SUCCESS: Data insertion completed!
) else (
    echo ERROR: Data insertion failed!
)

echo.
pause
