import requests
import pandas as pd
import os
from datetime import datetime, timezone
import time

# Constants
LIBRARIES_IO_API_BASE = "https://libraries.io/api"
RATE_LIMIT_DELAY = 1  # 1-second delay between requests to respect 60 requests/minute

def make_request(url, api_key):
    """
    Make a request to the Libraries.io API with rate-limiting and retry logic.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    while True:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers)

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))  # Default to 60 seconds
            print(f"Rate limit hit. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        # Handle not found (404)
        if response.status_code == 404:
            print(f"Page not found: {url}. Stopping pagination.")
            return None  # Signal to stop pagination

        # Handle other non-200 responses
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}\n{response.text}")
            raise Exception(f"Failed to fetch Libraries.io results: {response.status_code}")

        # Respect the rate limit delay
        time.sleep(RATE_LIMIT_DELAY)

        return response.json()

def fetch_all_results(api_key):
    """
    Fetch all results for PyPi and CRAN packages related to 'statisticsnorway' from Libraries.io.
    """
    platforms = ['pypi', 'cran']
    all_results = []

    for platform in platforms:
        page = 1
        while True:
            # Optimized query
            url = f"{LIBRARIES_IO_API_BASE}/search?q=statisticsnorway&platforms={platform}&api_key={api_key}&page={page}"
            data = make_request(url, api_key)

            # Stop pagination if no data is returned (e.g., 404 or empty)
            if data is None or not data:
                break

            all_results.extend(data)
            page += 1

    return all_results

def fetch_owner_metadata(platform, name, api_key):
    """
    Fetch detailed owner metadata from Libraries.io.
    """
    url = f"{LIBRARIES_IO_API_BASE}/{platform}/{name}?api_key={api_key}"
    return make_request(url, api_key)

def save_results_to_csv(results, api_key, output_file="./src/results.csv"):
    """
    Format the search results, fetch owner metadata, and save to CSV.
    Only include packages hosted on github.com/statisticsnorway.
    """
    current_timestamp = datetime.now(timezone.utc).isoformat()

    formatted_results = []
    for result in results:
        name = result.get("name", "").lower()
        platform = result.get("platform", "").lower()
        repository_url = result.get("repository_url", "").lower()

        # Filter out unwanted libraries
        if name.startswith("ssb-libtest") or "github.com/statisticsnorway" not in repository_url:
            continue

        # Fetch owner metadata
        owner_data = fetch_owner_metadata(platform, name, api_key)

        formatted_results.append({
            "Name": result.get("name"),
            "Platform": result.get("platform"),
            "Latest Version": result.get("latest_release_number"),
            "Last Updated": result.get("latest_release_published_at"),
            "Description": result.get("description"),
            "Homepage": result.get("homepage"),
            "Repository": repository_url,
            "Contributors": result.get("contributors_count", 0),
            "Owner Name": owner_data.get("owner", {}).get("login", "N/A"),
            "Owner Type": owner_data.get("owner", {}).get("type", "N/A"),
            "Owner Email": owner_data.get("owner", {}).get("email", "N/A"),
            "Stars": result.get("stars", 0),
            "Forks": result.get("forks", 0),
            "Dependents Count": result.get("dependents_count", 0),
            "Downloaded At": current_timestamp
        })

    # Save to CSV
    df = pd.DataFrame(formatted_results)
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to '{output_file}'.")

def main():
    api_key = os.getenv("LIBRARIESIO_API_KEY")
    if not api_key:
        raise Exception("API key not found. Please set LIBRARIESIO_API_KEY in the environment.")

    print("Searching Libraries.io for PyPi and CRAN packages...")

    # Fetch all results across all pages
    results = fetch_all_results(api_key)

    print(f"Fetched {len(results)} results.")

    # Save results with additional owner metadata
    save_results_to_csv(results, api_key)

if __name__ == "__main__":
    main()
