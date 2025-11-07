# National Park Brochure Scraper

A Python scraper that catalogs information about U.S. National Parks and uploads the data to Google Sheets. Designed to run in Google Colab with minimal setup.

## Features

- Fetches comprehensive data for all U.S. National Parks from the official NPS API
- Extracts park information including:
  - Park name
  - State(s)
  - Established year
  - Size (acreage)
  - Description
  - Official NPS URL
  - Historical brochure page URL (from npshistory.com)
- Respects rate limiting with 5-second delays between scrapes
- Automatically uploads data to Google Sheets
- Single file - no configuration files needed
- Runs entirely in Google Colab

## Quick Start (5 minutes)

### 1. Get an NPS API Key (Free)

1. Visit [NPS Developer Portal](https://www.nps.gov/subjects/developer/get-started.htm)
2. Fill out the form with your name and email
3. Check your email for the API key (arrives within an hour)

### 2. Open in Google Colab

1. Download `national_park_scraper_colab.py`
2. Go to [Google Colab](https://colab.research.google.com/)
3. Upload the file: `File > Upload notebook` or drag-and-drop

### 3. Configure

Edit the configuration section at the top of the file:

```python
# CONFIGURATION - CUSTOMIZE THESE TWO VARIABLES
NPS_API_KEY = "your_actual_api_key_here"
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

### 4. Run

Click `Runtime > Run all` or press `Ctrl+F9`

The script will:
- Install required packages automatically
- Authenticate with your Google account (you'll need to grant permissions)
- Scrape all National Parks from the NPS API
- Find brochure pages on npshistory.com
- Upload everything to your Google Sheet

Expected runtime: 10-15 minutes

## What You Get

A Google Sheet with the following columns:

| Column | Description |
|--------|-------------|
| **Park Name** | Full official name of the park |
| **State** | State(s) where the park is located |
| **Established Year** | Year the park was established (if available) |
| **Size** | Size in acres |
| **Description** | Official park description |
| **NPS URL** | Link to official NPS website |
| **Brochure Page URL** | Link to historical brochures (if found) |
| **Has Brochures** | Yes/No indicator |
| **Park Code** | Official NPS park code |

## Google Sheets Setup

### Option 1: Use the Provided Sheet (Easiest)

The script is pre-configured to use:
```
https://docs.google.com/spreadsheets/d/1y9hv2TgbaoAsUqZVpd6TlnPGHKQ7r5JS6Zo-IjSatMw/edit?usp=sharing
```

Just make sure you have edit access to this sheet.

### Option 2: Use Your Own Sheet

1. Create a new Google Sheet
2. Copy the sheet URL
3. Update `SHEET_URL` in the configuration section
4. Make sure you're logged into the Google account that owns the sheet

When you run the script, you'll be prompted to authenticate with Google. This allows the script to access your Google Sheets.

## How It Works

The scraper uses a two-source approach:

1. **Primary Data** - Official NPS API
   - Authoritative information about all National Parks
   - Includes names, locations, descriptions, sizes, URLs
   - Reliable and structured

2. **Supplementary Data** - npshistory.com
   - Historical brochure pages for each park
   - Not all parks have brochure pages (this is normal)
   - Respects rate limits with 5-second delays

## Output Example

```
[1/63] Yellowstone National Park (yell)
  ✓ Found brochure page
  State: ID, MT, WY
  Established: 1872
  Size: 2,219,791 acres

[2/63] Yosemite National Park (yose)
  ✓ Found brochure page
  State: CA
  Established: 1890
  Size: 761,747 acres
...
```

## Troubleshooting

### "Please set your NPS_API_KEY"

Make sure you:
1. Replaced `YOUR_NPS_API_KEY_HERE` with your actual API key
2. Kept the quotes around the API key
3. Saved the file before running

### "Authentication failed"

When prompted by Google Colab:
1. Click the authentication link
2. Choose your Google account
3. Click "Allow" to grant permissions
4. Wait for "Successfully authenticated" message

### "Error opening spreadsheet"

Make sure:
1. The SHEET_URL is correct
2. You have edit access to the sheet
3. You authenticated with the correct Google account

### "403 Forbidden" on brochure pages

This is expected for some parks. The script will:
- Continue processing other parks
- Mark these as "No brochures found"
- Still save all the NPS API data

### "No parks found from NPS API"

Check:
1. Your API key is correct
2. You have internet connection
3. Try requesting a new API key

## Data Sources

- **Primary Data**: [National Park Service API](https://www.nps.gov/subjects/developer/api-documentation.htm)
- **Brochure Links**: [NPS History - Electronic Library](https://npshistory.com/brochures/)

## Rate Limiting & Ethics

This scraper:
- Uses the official NPS API (authorized access)
- Respects rate limits with 5-second delays between requests
- Uses appropriate User-Agent headers
- Only accesses publicly available data
- Follows best practices for ethical web scraping

## Notes

- Focuses on "National Parks" designation only (not National Monuments, Historic Sites, etc.)
- Expected to find ~63 National Parks
- Some data fields may be "Unknown" if not available from the NPS API
- Brochure availability varies by park
- The script automatically installs required packages in Colab

## Requirements

The script automatically installs:
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `gspread` - Google Sheets API

Built-in to Colab:
- `google.colab.auth` - Authentication
- `google.auth` - Google credentials

## License

This project is for educational purposes as part of MGIS13 coursework.

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify your API key is valid
3. Make sure you have edit access to the Google Sheet
4. Try creating a new Google Sheet and updating the URL

## Credits

Data provided by:
- National Park Service (nps.gov)
- NPS History (npshistory.com)
