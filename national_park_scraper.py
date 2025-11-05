#!/usr/bin/env python3
"""
National Park Brochure Scraper

This script scrapes national park information from the NPS API and brochure links
from npshistory.com, then outputs the data to a Google Sheet.

Required environment variables:
    NPS_API_KEY: Your NPS API key from https://www.nps.gov/subjects/developer/get-started.htm
    GOOGLE_SHEETS_CREDENTIALS: Path to Google Sheets service account credentials JSON
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re


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
            'parkCode': '',
        }

        all_parks = []
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Filter for National Parks only (designation contains "National Park")
            for park in data.get('data', []):
                designation = park.get('designation', '')
                if 'National Park' in designation:
                    all_parks.append(park)

            print(f"Found {len(all_parks)} National Parks from NPS API")
            return all_parks

        except requests.RequestException as e:
            print(f"Error fetching from NPS API: {e}")
            return []

    def find_brochure_url(self, park_code: str, park_name: str) -> Optional[str]:
        """
        Try to find the brochure page URL for a park on npshistory.com.

        Args:
            park_code: NPS park code (e.g., 'noca')
            park_name: Full park name

        Returns:
            URL to the park's brochure page if found, None otherwise
        """
        # Try direct URL pattern
        park_code_lower = park_code.lower()
        brochure_url = f"https://npshistory.com/publications/{park_code_lower}/brochures/index.htm"

        try:
            response = self.session.get(brochure_url, timeout=10)
            if response.status_code == 200:
                return brochure_url
        except requests.RequestException:
            pass

        # If direct URL doesn't work, return None
        # We could implement more sophisticated searching here
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

            # Extract brochure information
            brochure_info = {
                'brochure_url': url,
                'has_brochures': False,
                'latest_brochure_year': None
            }

            # Look for brochure links and years
            # The structure varies, but typically brochures are listed with years
            brochure_links = soup.find_all('a', href=re.compile(r'.*\.pdf'))
            if brochure_links:
                brochure_info['has_brochures'] = True

                # Try to extract years from text
                years = []
                for link in brochure_links:
                    text = link.get_text()
                    year_match = re.search(r'(19|20)\d{2}', text)
                    if year_match:
                        years.append(int(year_match.group()))

                if years:
                    brochure_info['latest_brochure_year'] = max(years)

            return brochure_info

        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
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
        states = ', '.join([state.get('stateCode', '') for state in park.get('states', [])])
        if not states:
            states = park.get('states', 'Unknown')

        # Extract established year - try multiple fields
        established_year = None

        # Check designation field for year patterns
        designation = park.get('designation', '')
        year_match = re.search(r'established.*?(\d{4})', designation, re.IGNORECASE)
        if year_match:
            established_year = year_match.group(1)

        # Try description for establishment date
        if not established_year:
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
            acres = park.get('acreage', '')
            if acres:
                # Format with commas for readability
                size = f"{float(acres):,.0f} acres"
        except (ValueError, TypeError):
            size = None

        # Get description
        description = park.get('description', '')

        # Build result
        result = {
            'park_name': park.get('fullName', park.get('name', 'Unknown')),
            'state': states,
            'established_year': established_year or 'Unknown',
            'size': size or 'Unknown',
            'description': description,
            'park_code': park.get('parkCode', ''),
            'url': park.get('url', ''),
        }

        # Add brochure information if available
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
            print("No parks found from NPS API. Exiting.")
            return []

        results = []
        total = len(nps_parks)

        print(f"\nProcessing {total} National Parks...")
        print("=" * 80)

        for i, park in enumerate(nps_parks, 1):
            park_name = park.get('fullName', park.get('name', 'Unknown'))
            park_code = park.get('parkCode', '')

            print(f"\n[{i}/{total}] Processing: {park_name} ({park_code})")

            # Try to find brochure page
            brochure_info = None
            if park_code:
                brochure_url = self.find_brochure_url(park_code, park_name)
                if brochure_url:
                    print(f"  Found brochure page: {brochure_url}")
                    brochure_info = self.scrape_brochure_page(brochure_url)
                else:
                    print(f"  No brochure page found on npshistory.com")

            # Extract and format park data
            park_data = self.extract_park_data(park, brochure_info)
            results.append(park_data)

            print(f"  State: {park_data['state']}")
            print(f"  Established: {park_data['established_year']}")
            print(f"  Size: {park_data['size']}")

        print("\n" + "=" * 80)
        print(f"Completed scraping {len(results)} parks")

        return results

    def save_to_json(self, data: List[Dict], filename: str = 'parks_data.json'):
        """Save scraped data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nData saved to {filename}")


def main():
    """Main execution function."""
    # Check for API key
    nps_api_key = os.environ.get('NPS_API_KEY')
    if not nps_api_key:
        print("ERROR: NPS_API_KEY environment variable not set.")
        print("\nTo get an API key:")
        print("1. Visit: https://www.nps.gov/subjects/developer/get-started.htm")
        print("2. Request an API key")
        print("3. Set the environment variable: export NPS_API_KEY='your_key_here'")
        sys.exit(1)

    # Create scraper
    scraper = NationalParkScraper(nps_api_key=nps_api_key, rate_limit_delay=5.0)

    # Scrape all parks
    parks_data = scraper.scrape_all_parks()

    if parks_data:
        # Save to JSON
        scraper.save_to_json(parks_data)

        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Review the parks_data.json file")
        print("2. Run the Google Sheets uploader:")
        print("   python upload_to_sheets.py")
        print("\nMake sure you have set up Google Sheets credentials first!")
    else:
        print("\nNo data was scraped.")
        sys.exit(1)


if __name__ == '__main__':
    main()
