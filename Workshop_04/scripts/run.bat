@echo off

REM Check if virtual environment exists at root
if not exist env (
    echo Virtual environment not found at root. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call env\Scripts\activate.bat

REM Check if .env file exists
if not exist .env (
    echo .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Run the application
echo Launching Streamlit application...
streamlit run main.py

pause