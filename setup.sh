#!/bin/bash

echo "=========================================="
echo "National Park Scraper - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

echo "✓ Python 3 is installed: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment."
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Install requirements
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements."
    exit 1
fi

echo "✓ Requirements installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "IMPORTANT: Edit the .env file and add your credentials:"
    echo "  - NPS_API_KEY (get from: https://www.nps.gov/subjects/developer/get-started.htm)"
    echo "  - GOOGLE_SHEETS_CREDENTIALS (path to your credentials JSON)"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys and credentials"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the scraper: python national_park_scraper.py"
echo "4. Upload to Google Sheets: python upload_to_sheets.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""
