#!/bin/bash

echo "=========================================="
echo "National Park Scraper - Run Script"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Please copy .env.example to .env and fill in your credentials."
    exit 1
fi

# Load environment variables from .env
echo "Loading environment variables from .env..."
export $(cat .env | grep -v '^#' | xargs)

# Check if NPS_API_KEY is set
if [ -z "$NPS_API_KEY" ] || [ "$NPS_API_KEY" = "your_nps_api_key_here" ]; then
    echo "ERROR: NPS_API_KEY is not set in .env file."
    echo "Please edit .env and add your NPS API key."
    exit 1
fi

echo "✓ NPS_API_KEY is set"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Activating..."
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
        echo "✓ Virtual environment activated"
    else
        echo "ERROR: Virtual environment not found."
        echo "Please run ./setup.sh first."
        exit 1
    fi
else
    echo "✓ Virtual environment is active"
fi

echo ""
echo "=========================================="
echo "Step 1: Scraping National Park Data"
echo "=========================================="
echo ""

python national_park_scraper.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Scraper failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Uploading to Google Sheets"
echo "=========================================="
echo ""

# Check if parks_data.json exists
if [ ! -f parks_data.json ]; then
    echo "ERROR: parks_data.json not found."
    echo "The scraper may have failed. Please check the output above."
    exit 1
fi

# Check if Google Sheets credentials are set
if [ -z "$GOOGLE_SHEETS_CREDENTIALS" ] || [ "$GOOGLE_SHEETS_CREDENTIALS" = "/path/to/your/credentials.json" ]; then
    echo "WARNING: GOOGLE_SHEETS_CREDENTIALS is not properly set in .env file."
    echo "Skipping Google Sheets upload."
    echo ""
    echo "To upload to Google Sheets:"
    echo "1. Set up Google Cloud credentials (see README.md)"
    echo "2. Update GOOGLE_SHEETS_CREDENTIALS in .env"
    echo "3. Run: python upload_to_sheets.py"
    exit 0
fi

if [ ! -f "$GOOGLE_SHEETS_CREDENTIALS" ]; then
    echo "WARNING: Google Sheets credentials file not found at: $GOOGLE_SHEETS_CREDENTIALS"
    echo "Skipping Google Sheets upload."
    echo ""
    echo "To upload to Google Sheets:"
    echo "1. Download credentials from Google Cloud Console"
    echo "2. Update path in .env file"
    echo "3. Run: python upload_to_sheets.py"
    exit 0
fi

echo "✓ Google Sheets credentials found"
echo ""

python upload_to_sheets.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Upload to Google Sheets failed."
    echo "Please check the error messages above."
    exit 1
fi

echo ""
echo "=========================================="
echo "SUCCESS! Process Complete"
echo "=========================================="
echo ""
echo "Data has been scraped and uploaded to Google Sheets."
echo "View at: https://docs.google.com/spreadsheets/d/1y9hv2TgbaoAsUqZVpd6TlnPGHKQ7r5JS6Zo-IjSatMw/edit?usp=sharing"
echo ""
