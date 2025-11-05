# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.7+ installed
- Git installed

## Step-by-Step Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd mgis13-national-park-scraper

# Run setup script
./setup.sh
```

### 2. Get NPS API Key (5 minutes)

1. Visit: https://www.nps.gov/subjects/developer/get-started.htm
2. Fill out the form with:
   - First/Last name
   - Email address
3. Check your email for the API key (arrives within an hour)

### 3. Configure Environment

```bash
# Edit .env file
nano .env  # or use your preferred editor

# Add your API key:
NPS_API_KEY=your_actual_api_key_here
```

### 4. Run the Scraper

```bash
# Activate virtual environment
source venv/bin/activate

# Run the scraper
./run_scraper.sh
```

That's it! The script will:
- Fetch all National Parks from the NPS API
- Find brochure pages on npshistory.com
- Save data to `parks_data.json`

## Google Sheets Setup (Optional)

If you want to upload to Google Sheets:

### Quick Steps:

1. **Google Cloud Console**: https://console.cloud.google.com
   - Create new project
   - Enable "Google Sheets API"

2. **Create Service Account**:
   - Go to: APIs & Services > Credentials
   - Create Credentials > Service Account
   - Download JSON key file

3. **Share Google Sheet**:
   - Open: https://docs.google.com/spreadsheets/d/1y9hv2TgbaoAsUqZVpd6TlnPGHKQ7r5JS6Zo-IjSatMw/edit
   - Click "Share"
   - Add the service account email (from JSON file)
   - Give "Editor" access

4. **Update .env**:
   ```bash
   GOOGLE_SHEETS_CREDENTIALS=/path/to/downloaded/credentials.json
   ```

5. **Run Upload**:
   ```bash
   python upload_to_sheets.py
   ```

## Troubleshooting

### "NPS_API_KEY not set"
- Make sure you edited `.env` file
- Remove any quotes around the API key
- Run: `source venv/bin/activate` before running scripts

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

### "403 Forbidden" on npshistory.com
- This is expected for some parks
- The scraper will continue with other parks
- Primary data comes from NPS API (which works fine)

## What You Get

A `parks_data.json` file and/or Google Sheet with:
- Park names
- States
- Established years
- Sizes (in acres)
- Descriptions
- Official URLs
- Brochure page links (where available)

## Expected Runtime

- Scraping: ~10-15 minutes (respects 5-second rate limits)
- Upload: ~5-10 seconds

## Need Help?

See the full [README.md](README.md) for detailed documentation.

## Common Commands

```bash
# Setup
./setup.sh

# Activate environment
source venv/bin/activate

# Run scraper only
python national_park_scraper.py

# Upload to sheets only
python upload_to_sheets.py

# Run everything
./run_scraper.sh

# Deactivate environment
deactivate
```

## Pro Tips

1. **Test First**: The scraper respects rate limits, so it takes time. Be patient!
2. **Check JSON**: Review `parks_data.json` before uploading to sheets
3. **API Limits**: The NPS API is generous, but avoid running the scraper repeatedly
4. **Brochures**: Not all parks have brochure pages - this is normal

Happy scraping!
