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
LIBRARIESIO_API_KEY = os.getenv("LIBRARIESIO_API_KEY")  # Move API key to a global variable

if not LIBRARIESIO_API_KEY:
    raise Exception("Libraries.io API key not found. Please set LIBRARIESIO_API_KEY in the environment.")

def normalize_package_name(package_name):
    """Normalize package name for PyPI query."""
    return package_name.lower().replace("_", "-")

def fetch_pypi_metadata(package_name):
    """Fetch PyPi package metadata and return latest version URL."""
    normalized_name = normalize_package_name(package_name)
    homepage = PYPI_PACKAGE_PAGE.format(normalized_name)

    try:
        url = f"{PYPI_API_BASE}/{normalized_name}/json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            owner_name = data["info"].get("author", "N/A")
            return {"Owner Name": owner_name, "Homepage": homepage, "Internal": False}

        print(f"PyPi package '{package_name}' not found.")
    except Exception as e:
        print(f"Error fetching PyPi metadata for {package_name}: {e}")

    # Default fallback
    return {"Owner Name": "N/A", "Homepage": homepage, "Internal": False}

def fetch_cran_metadata(package_name):
    """Fetch CRAN package metadata and return latest version URL."""
    homepage = CRAN_PACKAGE_PAGE.format(package_name)

    try:
        url = CRAN_PACKAGE_URL.format(package_name)
        response = requests.get(url)

        if response.status_code == 200:
            # Parse Maintainer
            maintainer_line = next(
                (line for line in response.text.splitlines() if line.startswith("Maintainer:")),
                None,
            )
            owner_name = re.sub(r"<.*?>", "", maintainer_line.split(":", 1)[1].strip()) if maintainer_line else "N/A"
            return {"Owner Name": owner_name, "Homepage": homepage, "Internal": False}

        print(f"CRAN package '{package_name}' not found.")
    except Exception as e:
        print(f"Error fetching CRAN metadata for {package_name}: {e}")

    # Default fallback
    return {"Owner Name": "N/A", "Homepage": homepage, "Internal": False}

def fetch_search_results(api_key, search_term, platforms):
    """Fetch packages for a specific search term from Libraries.io for specified platforms."""
    all_results = []

    for platform in platforms:
        page = 1
        while True:
            url = f"{LIBRARIES_IO_API_BASE}/search?q={search_term}&platforms={platform}&api_key={api_key}&page={page}"
            response = requests.get(url)

            if response.status_code != 200 or not response.json():
                break

            all_results.extend(response.json())
            page += 1
            time.sleep(RATE_LIMIT_DELAY)

    return all_results

def fetch_all_results(search_terms):
    """Aggregate results from multiple searches."""
    platforms = ['pypi', 'cran']
    aggregated_results = []

    for term in search_terms:
        print(f"Fetching results for search term: '{term}'")
        results = fetch_search_results(LIBRARIESIO_API_KEY, term, platforms)
        aggregated_results.extend(results)

    return aggregated_results

def save_results_to_csv(results, output_file="./src/results.csv"):
    """Format results, fetch metadata, deduplicate, sort, and save to CSV."""
    current_timestamp = datetime.now(timezone.utc).isoformat()

    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    formatted_results = []
    for result in results:
        name = result.get("name", "").strip()
        platform = result.get("platform", "").lower()
        repository_url = result.get("repository_url", "").strip()

        # Skip test libraries
        if name.startswith("ssb-libtest"):
            print(f"Skipping test library: {name}")
            continue

        # Determine internal status based on repository URL
        if repository_url:
            if "github.com/statisticsnorway" not in repository_url:
                print(f"Skipping {name} (external GitHub repository: {repository_url})")
                continue
            internal = False
        else:
            internal = True

        # Add all relevant columns
        formatted_results.append({
            "Name": name,  # Preserve case
            "Platform": result.get("platform", "N/A"),
            "Latest Version": result.get("latest_release_number", "N/A"),
            "Last Updated": result.get("latest_release_published_at", "N/A"),
            "Description": result.get("description", "N/A"),
            "Homepage": result.get("homepage", "N/A"),
            "Repository": repository_url,
            "Owner Name": result.get("owner", "N/A"),
            "Internal": internal,
            "Contributors": result.get("contributors_count", 0),
            "Stars": result.get("stars", 0),
            "Forks": result.get("forks", 0),
            "Number of releases": len(result.get("versions", [])),
            "Dependents Count": result.get("dependents_count", 0),
            "Downloaded At": current_timestamp,
        })

    # Deduplicate by 'Name'
    deduplicated_results = {result['Name']: result for result in formatted_results}.values()

    # Create DataFrame and sort by Last Updated DESC
    df = pd.DataFrame(deduplicated_results)
    df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")
    df.sort_values(by="Last Updated", ascending=False, inplace=True)

    # Save sorted results to CSV
    df.to_csv(output_file, index=False)
    print(f"\nResults successfully saved to '{os.path.abspath(output_file)}'.")

def main():
    search_terms = ["statisticsnorway", "dapla"]
    results = fetch_all_results(search_terms)
    print(f"Fetched {len(results)} results before processing.")

    # Save results to CSV
    save_results_to_csv(results)

if __name__ == "__main__":
    main()
