import requests
import pandas as pd
import os
import re
from datetime import datetime, timezone
import time

# Constants
LIBRARIES_IO_API_BASE = "https://libraries.io/api"
PYPI_API_BASE = "https://pypi.org/pypi"
CRAN_PACKAGE_URL = "https://cran.r-project.org/web/packages/{}/DESCRIPTION"
CRAN_PACKAGE_PAGE = "https://cran.r-project.org/web/packages/{}"
PYPI_PACKAGE_PAGE = "https://pypi.org/project/{}"
RATE_LIMIT_DELAY = 1  # Delay between API requests


def fetch_pypi_metadata(package_name):
    """Fetch PyPi package metadata and return latest version URL."""
    homepage = PYPI_PACKAGE_PAGE.format(package_name)

    try:
        url = f"{PYPI_API_BASE}/{package_name}/json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            owner_name = data["info"].get("author", "N/A")
            return {"Owner Name": owner_name, "Homepage": homepage}

        print(f"PyPi package '{package_name}' not found.")
    except Exception as e:
        print(f"Error fetching PyPi metadata for {package_name}: {e}")

    # Default fallback
    return {"Owner Name": "N/A", "Homepage": homepage}


def fetch_cran_metadata(package_name):
    """Fetch CRAN package metadata and return latest version URL."""
    homepage = CRAN_PACKAGE_PAGE.format(package_name)

    try:
        url = CRAN_PACKAGE_URL.format(package_name)
        response = requests.get(url)

        if response.status_code == 200:
            # Extract Maintainer using regex for better matching
            match = re.search(r'^Maintainer:\s*(.+)$', response.text, re.MULTILINE)
            owner_name = match.group(1) if match else "N/A"
            return {"Owner Name": owner_name, "Homepage": homepage}

        print(f"CRAN package '{package_name}' not found.")
    except Exception as e:
        print(f"Error fetching CRAN metadata for {package_name}: {e}")

    # Default fallback
    return {"Owner Name": "N/A", "Homepage": homepage}


def fetch_all_results(api_key):
    """Fetch packages from Libraries.io for PyPi and CRAN."""
    platforms = ['pypi', 'cran']
    all_results = []

    for platform in platforms:
        page = 1
        while True:
            url = f"{LIBRARIES_IO_API_BASE}/search?q=statisticsnorway&platforms={platform}&api_key={api_key}&page={page}"
            response = requests.get(url)

            if response.status_code != 200 or not response.json():
                break

            all_results.extend(response.json())
            page += 1
            time.sleep(RATE_LIMIT_DELAY)

    return all_results


def save_results_to_csv(results, output_file="./src/results.csv"):
    """Format results, fetch metadata, sort, and save to CSV."""
    current_timestamp = datetime.now(timezone.utc).isoformat()

    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    formatted_results = []
    for result in results:
        name = result.get("name", "").lower()
        platform = result.get("platform", "").lower()
        repository_url = result.get("repository_url", "").lower()

        # Skip unwanted packages
        if name.startswith("ssb-libtest") or "github.com/statisticsnorway" not in repository_url:
            print(f"Skipping {name} (test library or not hosted by Statistics Norway)")
            continue

        # Fetch relevant metadata
        if platform == "pypi":
            metadata = fetch_pypi_metadata(name)
        elif platform == "cran":
            metadata = fetch_cran_metadata(name)
        else:
            metadata = {"Owner Name": "N/A", "Homepage": "N/A"}

        # Add all relevant columns
        formatted_results.append({
            "Name": result.get("name", "N/A"),
            "Platform": result.get("platform", "N/A"),
            "Latest Version": result.get("latest_release_number", "N/A"),
            "Last Updated": result.get("latest_release_published_at", "N/A"),
            "Description": result.get("description", "N/A"),
            "Homepage": metadata.get("Homepage", "N/A"),
            "Repository": repository_url,
            "Owner Name": metadata.get("Owner Name", "N/A"),
            "Contributors": result.get("contributors_count", 0),
            "Stars": result.get("stars", 0),
            "Forks": result.get("forks", 0),
            "Dependents Count": result.get("dependents_count", 0),
            "Downloaded At": current_timestamp,
        })

    # Create DataFrame and sort by Last Updated DESC
    df = pd.DataFrame(formatted_results)
    df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")
    df.sort_values(by="Last Updated", ascending=False, inplace=True)

    # Save sorted results to CSV
    df.to_csv(output_file, index=False)
    print(f"\nResults successfully saved to '{os.path.abspath(output_file)}'.")


def main():
    api_key = os.getenv("LIBRARIESIO_API_KEY")
    if not api_key:
        raise Exception("Libraries.io API key not found. Please set LIBRARIESIO_API_KEY in the environment.")

    print("Searching Libraries.io for PyPi and CRAN packages...")
    results = fetch_all_results(api_key)
    print(f"Fetched {len(results)} results.")

    # Save results to CSV
    save_results_to_csv(results)


if __name__ == "__main__":
    main()
