# National Park Brochure Scraper

A Python scraper that catalogs information about U.S. National Parks by combining data from the official National Park Service (NPS) API and historical brochure pages from npshistory.com. The scraped data is automatically uploaded to Google Sheets for easy viewing and analysis.

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
- Error handling and retry logic
- Progress tracking during scraping

## Prerequisites

1. **Python 3.7+** installed on your system
2. **NPS API Key** - Free API key from the National Park Service
3. **Google Cloud Service Account** - For Google Sheets integration

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mgis13-national-park-scraper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get an NPS API Key

1. Visit the [NPS Developer Portal](https://www.nps.gov/subjects/developer/get-started.htm)
2. Fill out the form to request an API key
3. You'll receive your API key via email (usually within an hour)
4. Set the environment variable:

```bash
export NPS_API_KEY='your_api_key_here'
```

### 4. Set Up Google Sheets Access

#### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the **Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

#### Step 2: Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

#### Step 3: Download Credentials

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Download the JSON file and save it securely

#### Step 4: Share Your Google Sheet

1. Open your [Google Sheet](https://docs.google.com/spreadsheets/d/1y9hv2TgbaoAsUqZVpd6TlnPGHKQ7r5JS6Zo-IjSatMw/edit?usp=sharing)
2. Click the "Share" button
3. Add the service account email (found in the JSON file as `client_email`)
4. Give it "Editor" permissions

#### Step 5: Set Environment Variable

```bash
export GOOGLE_SHEETS_CREDENTIALS='/path/to/your/credentials.json'
```

## Usage

### Step 1: Scrape National Park Data

Run the scraper to fetch data from the NPS API and npshistory.com:

```bash
python national_park_scraper.py
```

This will:
- Fetch all National Parks from the NPS API
- Try to find brochure pages on npshistory.com for each park
- Respect rate limiting with 5-second delays
- Save the data to `parks_data.json`

Expected runtime: ~10-15 minutes (depending on the number of parks)

### Step 2: Upload to Google Sheets

Upload the scraped data to your Google Sheet:

```bash
python upload_to_sheets.py
```

This will:
- Read the `parks_data.json` file
- Authenticate with Google Sheets API
- Upload all data to the specified Google Sheet
- Format the sheet with headers and auto-sized columns

### View Results

Open your Google Sheet to view the results:
https://docs.google.com/spreadsheets/d/1y9hv2TgbaoAsUqZVpd6TlnPGHKQ7r5JS6Zo-IjSatMw/edit?usp=sharing

## Output Format

The Google Sheet will contain the following columns:

| Column | Description |
|--------|-------------|
| Park Name | Full official name of the park |
| State | State(s) where the park is located |
| Established Year | Year the park was established |
| Size | Size in acres |
| Description | Official park description |
| NPS URL | Link to official NPS website |
| Brochure Page URL | Link to historical brochures (if found) |
| Has Brochures | Yes/No indicator |
| Park Code | Official NPS park code |

## Troubleshooting

### API Key Issues

If you get API key errors:
- Verify your API key is set: `echo $NPS_API_KEY`
- Make sure there are no extra spaces or quotes
- Try requesting a new API key if it's expired

### Google Sheets Authentication Errors

If you get authentication errors:
- Verify the credentials file path is correct
- Make sure you've shared the sheet with the service account email
- Check that the Google Sheets API is enabled in your project

### Rate Limiting

The scraper includes built-in 5-second delays between requests to respect the data sources. Do not reduce this delay as it may result in being blocked.

### Missing Brochure Pages

Not all parks have brochure pages on npshistory.com. This is expected - the scraper will mark these as "No" in the "Has Brochures" column.

## Data Sources

- **Primary Data**: [National Park Service API](https://www.nps.gov/subjects/developer/api-documentation.htm)
- **Brochure Links**: [NPS History - Electronic Library](https://npshistory.com/brochures/)

## Rate Limiting & Ethics

This scraper:
- Uses the official NPS API (no scraping needed for primary data)
- Respects rate limits with 5-second delays between requests
- Uses appropriate User-Agent headers
- Only accesses publicly available data
- Follows best practices for ethical web scraping

## License

This project is for educational purposes as part of MGIS13 coursework.

## Notes

- The scraper focuses on "National Parks" designation only (not National Monuments, Historic Sites, etc.)
- Brochure availability varies by park
- Some data fields may be "Unknown" if not available from the NPS API
- The NPS API is the authoritative source for park information
