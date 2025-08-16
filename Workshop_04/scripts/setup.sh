#!/bin/bash

echo "🚀 Setting up AI Agent EDINET..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "⚙️ Creating environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Please update with your API keys."
fi


echo "✅ Setup complete!"
echo "📝 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Run: python main.py"