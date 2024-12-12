import requests
import pandas as pd
import os
from datetime import datetime, timezone
import time

# Constants
LIBRARIES_IO_API_BASE = "https://libraries.io/api"
GITHUB_API_BASE = "https://api.github.com/repos"
RATE_LIMIT_DELAY = 1  # 1-second delay between requests


def make_request(url, headers=None):
    """
    Make a request with rate-limiting and retry logic.
    """
    while True:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers)

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limit hit. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        # Handle 404 Not Found
        if response.status_code == 404:
            print(f"Page not found: {url}. Skipping.")
            return None

        # Handle other non-200 responses
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}\n{response.text}")
            raise Exception(f"Failed to fetch data: {response.status_code}")

        # Respect the rate limit delay
        time.sleep(RATE_LIMIT_DELAY)

        return response.json()


def fetch_all_results(api_key):
    """
    Fetch packages from Libraries.io based on query.
    """
    platforms = ['pypi', 'cran']
    all_results = []

    for platform in platforms:
        page = 1
        while True:
            url = f"{LIBRARIES_IO_API_BASE}/search?q=statisticsnorway&platforms={platform}&api_key={api_key}&page={page}"
            data = make_request(url)

            if data is None or not data:
                break

            all_results.extend(data)
            page += 1

    return all_results


def fetch_github_metadata(repository_url, github_token):
    """
    Fetch repository metadata from GitHub API using the repo URL.
    """
    if not repository_url.startswith("https://github.com"):
        return {}

    repo_path = "/".join(repository_url.split("/")[-2:])
    url = f"{GITHUB_API_BASE}/{repo_path}"
    headers = {"Authorization": f"token {github_token}"} if github_token else None

    return make_request(url, headers)


def save_results_to_csv(results, api_key, github_token, output_file="./src/results.csv"):
    """
    Format the search results and save to CSV.
    Include repository metadata from GitHub API.
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

        # Fetch GitHub metadata
        github_metadata = fetch_github_metadata(repository_url, github_token)
        owner_info = github_metadata.get("owner", {})

        formatted_results.append({
            "Name": result.get("name"),
            "Platform": result.get("platform"),
            "Latest Version": result.get("latest_release_number"),
            "Last Updated": result.get("latest_release_published_at"),
            "Description": result.get("description"),
            "Homepage": result.get("homepage"),
            "Repository": repository_url,
            "Contributors": result.get("contributors_count", 0),
            "Owner Name": owner_info.get("login", "N/A"),
            "Owner Type": owner_info.get("type", "N/A"),
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
    github_token = os.getenv("GITHUB_TOKEN")

    if not api_key:
        raise Exception("Libraries.io API key not found. Please set LIBRARIESIO_API_KEY in the environment.")

    print("Searching Libraries.io for PyPi and CRAN packages...")

    # Fetch all results across all pages
    results = fetch_all_results(api_key)

    print(f"Fetched {len(results)} results.")

    # Save results with GitHub metadata
    save_results_to_csv(results, api_key, github_token)


if __name__ == "__main__":
    main()
