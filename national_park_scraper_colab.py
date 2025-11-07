#!/usr/bin/env python3
"""
National Park Brochure Scraper - Google Colab Version

A single-file scraper that catalogs U.S. National Parks and uploads to Google Sheets.
Designed to run in Google Colab with minimal setup.

SETUP:
1. Open this file in Google Colab
2. Set your NPS_API_KEY below
3. Set your SHEET_URL below
4. Run all cells

Get your free NPS API key at: https://www.nps.gov/subjects/developer/get-started.htm
"""

# ============================================================================
# CONFIGURATION - CUSTOMIZE THESE TWO VARIABLES
# ============================================================================

NPS_API_KEY = "YOUR_NPS_API_KEY_HERE"  # Get from: https://www.nps.gov/subjects/developer/get-started.htm
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y9hv2TgbaoAsUqZVpd6TlnPGHKQ7r5JS6Zo-IjSatMw/edit?usp=sharing"

# ============================================================================
# IMPORTS
# ============================================================================

import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import sys

# Check if running in Colab
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    # Install required packages in Colab
    print("Installing required packages...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'gspread', 'beautifulsoup4'], check=True)
    print("✓ Packages installed\n")

import gspread
from google.auth import default
from google.colab import auth


# ============================================================================
# SCRAPER CLASS
# ============================================================================

class NationalParkScraper:
    """Scraper for National Park data and brochures."""

    def __init__(self, nps_api_key: str, rate_limit_delay: float = 5.0):
        """
        Initialize the scraper.

        Args:
            nps_api_key: NPS API key
            rate_limit_delay: Delay between requests in seconds (default 5.0)
        """
        self.nps_api_key = nps_api_key
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.parks_data = []

    def get_nps_parks(self) -> List[Dict]:
        """
        Fetch all national parks from the NPS API.

        Returns:
            List of park dictionaries with official NPS data
        """
        print("Fetching parks from NPS API...")
        url = "https://developer.nps.gov/api/v1/parks"
        params = {
            'api_key': self.nps_api_key,
            'limit': 500,  # Max limit per request
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Filter for National Parks only (designation contains "National Park")
            all_parks = []
            for park in data.get('data', []):
                designation = park.get('designation', '')
                if 'National Park' in designation:
                    all_parks.append(park)

            print(f"✓ Found {len(all_parks)} National Parks from NPS API\n")
            return all_parks

        except requests.RequestException as e:
            print(f"ERROR fetching from NPS API: {e}")
            return []

    def find_brochure_url(self, park_code: str) -> Optional[str]:
        """
        Try to find the brochure page URL for a park on npshistory.com.

        Args:
            park_code: NPS park code (e.g., 'noca')

        Returns:
            URL to the park's brochure page if found, None otherwise
        """
        park_code_lower = park_code.lower()
        brochure_url = f"https://npshistory.com/publications/{park_code_lower}/brochures/index.htm"

        try:
            response = self.session.get(brochure_url, timeout=10)
            if response.status_code == 200:
                return brochure_url
        except requests.RequestException:
            pass

        return None

    def scrape_brochure_page(self, url: str) -> Dict:
        """
        Scrape additional information from a park's brochure page.

        Args:
            url: URL to the brochure page

        Returns:
            Dictionary with brochure information
        """
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            brochure_info = {
                'brochure_url': url,
                'has_brochures': False,
                'latest_brochure_year': None
            }

            # Look for brochure links
            brochure_links = soup.find_all('a', href=re.compile(r'.*\.pdf'))
            if brochure_links:
                brochure_info['has_brochures'] = True

                # Try to extract years
                years = []
                for link in brochure_links:
                    text = link.get_text()
                    year_match = re.search(r'(19|20)\d{2}', text)
                    if year_match:
                        years.append(int(year_match.group()))

                if years:
                    brochure_info['latest_brochure_year'] = max(years)

            return brochure_info

        except requests.RequestException:
            return {'brochure_url': url, 'has_brochures': False}

    def extract_park_data(self, park: Dict, brochure_info: Optional[Dict] = None) -> Dict:
        """
        Extract and format park data.

        Args:
            park: Park data from NPS API
            brochure_info: Brochure information from npshistory.com

        Returns:
            Dictionary with formatted park data
        """
        # Extract states
        states = park.get('states', '')
        if isinstance(states, list):
            states = ', '.join(states)

        # Extract established year
        established_year = None

        # Try description for establishment date
        description = park.get('description', '')
        year_patterns = [
            r'established in (\d{4})',
            r'established (\d{4})',
            r'created in (\d{4})',
            r'founded in (\d{4})',
        ]
        for pattern in year_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                established_year = match.group(1)
                break

        # Extract size (acreage)
        size = None
        try:
            acres = park.get('acres', '')
            if not acres:
                # Try alternative field name
                for contact in park.get('contacts', {}).get('phoneNumbers', []):
                    pass  # Some APIs use different structures

                # Check if there's acreage in latLongDescription or other fields
                lat_long_desc = park.get('latLongDescription', '')

            if acres:
                size = f"{float(acres):,.0f} acres"
        except (ValueError, TypeError):
            size = None

        # Build result
        result = {
            'park_name': park.get('fullName', park.get('name', 'Unknown')),
            'state': states or 'Unknown',
            'established_year': established_year or 'Unknown',
            'size': size or 'Unknown',
            'description': description,
            'park_code': park.get('parkCode', ''),
            'url': park.get('url', ''),
        }

        # Add brochure information
        if brochure_info:
            result['brochure_page_url'] = brochure_info.get('brochure_url', '')
            result['has_brochures'] = brochure_info.get('has_brochures', False)
        else:
            result['brochure_page_url'] = ''
            result['has_brochures'] = False

        return result

    def scrape_all_parks(self) -> List[Dict]:
        """
        Scrape data for all national parks.

        Returns:
            List of park data dictionaries
        """
        # Get parks from NPS API
        nps_parks = self.get_nps_parks()

        if not nps_parks:
            print("ERROR: No parks found from NPS API.")
            return []

        results = []
        total = len(nps_parks)

        print(f"Processing {total} National Parks...")
        print("=" * 80)

        for i, park in enumerate(nps_parks, 1):
            park_name = park.get('fullName', park.get('name', 'Unknown'))
            park_code = park.get('parkCode', '')

            print(f"\n[{i}/{total}] {park_name} ({park_code})")

            # Try to find brochure page
            brochure_info = None
            if park_code:
                brochure_url = self.find_brochure_url(park_code)
                if brochure_url:
                    print(f"  ✓ Found brochure page")
                    brochure_info = self.scrape_brochure_page(brochure_url)
                else:
                    print(f"  ○ No brochure page found")

            # Extract and format park data
            park_data = self.extract_park_data(park, brochure_info)
            results.append(park_data)

            print(f"  State: {park_data['state']}")
            print(f"  Established: {park_data['established_year']}")
            print(f"  Size: {park_data['size']}")

        print("\n" + "=" * 80)
        print(f"✓ Completed scraping {len(results)} parks\n")

        return results


# ============================================================================
# GOOGLE SHEETS UPLOADER CLASS
# ============================================================================

class GoogleSheetsUploader:
    """Uploader for National Park data to Google Sheets (Colab version)."""

    def __init__(self):
        """Initialize the uploader."""
        self.client = None

    def authenticate_colab(self):
        """Authenticate with Google Sheets API using Colab auth."""
        try:
            print("Authenticating with Google...")
            auth.authenticate_user()
            creds, _ = default()
            self.client = gspread.authorize(creds)
            print("✓ Successfully authenticated with Google Sheets API\n")
            return True
        except Exception as e:
            print(f"ERROR: Authentication failed: {e}")
            return False

    def upload_data(self, spreadsheet_url: str, data: List[Dict], sheet_name: str = "National Parks"):
        """
        Upload park data to Google Sheet.

        Args:
            spreadsheet_url: URL of the Google Sheet
            data: List of park data dictionaries
            sheet_name: Name of the worksheet to create/update
        """
        try:
            print(f"Opening spreadsheet...")
            spreadsheet = self.client.open_by_url(spreadsheet_url)

            # Try to get the worksheet, create if it doesn't exist
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"✓ Found existing worksheet: {sheet_name}")
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=len(data) + 1,
                    cols=10
                )
                print(f"✓ Created new worksheet: {sheet_name}")

            # Prepare data
            headers = [
                'Park Name',
                'State',
                'Established Year',
                'Size',
                'Description',
                'NPS URL',
                'Brochure Page URL',
                'Has Brochures',
                'Park Code'
            ]

            rows = [headers]

            for park in data:
                row = [
                    park.get('park_name', ''),
                    park.get('state', ''),
                    park.get('established_year', ''),
                    park.get('size', ''),
                    park.get('description', ''),
                    park.get('url', ''),
                    park.get('brochure_page_url', ''),
                    'Yes' if park.get('has_brochures', False) else 'No',
                    park.get('park_code', '')
                ]
                rows.append(row)

            # Upload all data
            print(f"Uploading {len(data)} parks to Google Sheet...")
            worksheet.update(rows, 'A1')

            # Format header row
            worksheet.format('A1:I1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.2}
            })

            # Auto-resize columns
            for i in range(9):
                worksheet.columns_auto_resize(i, i)

            print(f"\n{'=' * 80}")
            print(f"SUCCESS! Uploaded {len(data)} parks to Google Sheet!")
            print(f"{'=' * 80}")
            print(f"\nView at: {spreadsheet_url}\n")

            return True

        except Exception as e:
            print(f"ERROR uploading to Google Sheet: {e}")
            return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""

    print("=" * 80)
    print("NATIONAL PARK BROCHURE SCRAPER")
    print("=" * 80)
    print()

    # Validate configuration
    if NPS_API_KEY == "YOUR_NPS_API_KEY_HERE":
        print("ERROR: Please set your NPS_API_KEY at the top of this file.")
        print("\nGet your free API key at:")
        print("https://www.nps.gov/subjects/developer/get-started.htm")
        return

    if not IN_COLAB:
        print("WARNING: This script is designed to run in Google Colab.")
        print("Some features may not work outside of Colab.")
        print()

    # Create scraper
    scraper = NationalParkScraper(nps_api_key=NPS_API_KEY, rate_limit_delay=5.0)

    # Scrape all parks
    print("STEP 1: Scraping National Park Data")
    print("=" * 80)
    print()

    parks_data = scraper.scrape_all_parks()

    if not parks_data:
        print("\nERROR: No data was scraped.")
        return

    # Upload to Google Sheets
    print("\nSTEP 2: Uploading to Google Sheets")
    print("=" * 80)
    print()

    uploader = GoogleSheetsUploader()

    if not uploader.authenticate_colab():
        print("\nERROR: Authentication failed.")
        return

    success = uploader.upload_data(SHEET_URL, parks_data)

    if success:
        print("✓ Process complete!")
    else:
        print("\nERROR: Upload failed.")


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    main()
