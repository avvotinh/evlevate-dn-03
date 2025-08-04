@echo off
echo 🚀 Setting up AI Agent EDINET...

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file
echo ⚙️ Creating environment file...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file. Please update with your API keys.
) else (
    echo ⚠️ .env file already exists.
)

echo.
echo ✅ Setup complete!
echo 📝 Next steps:
echo 1. Update .env file with your API keys
echo 2. Run: run.bat
echo.
pause