import requests
import pandas as pd
import os
from datetime import datetime, timezone

def fetch_all_results(query, api_key):
    """
    Fetch all results for a query from Libraries.io across all pages.
    """
    url = f"https://libraries.io/api/search?q={query}&api_key={api_key}"
    all_results = []

    while url:
        print(f"Fetching: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch Libraries.io results: {response.status_code}\n{response.text}")
        
        # Parse the response
        data = response.json()
        all_results.extend(data)

        # Get the next page URL from the 'Link' header (if available)
        next_url = response.links.get("next", {}).get("url")
        url = next_url  # Continue to the next page or None if there are no more pages

    return all_results

def save_results_to_csv(results, output_file="./src/results.csv"):
    """
    Format the search results and save them to a CSV file.
    Skip libraries with names starting with "ssb-libtest".
    """
    # Get the current timestamp in ISO 8601 format with timezone awareness
    current_timestamp = datetime.now(timezone.utc).isoformat()

    formatted_results = []
    for result in results:
        repository_url = result.get("repository_url")
        name = result.get("name", "").lower()

        # Skip unwanted libraries
        if repository_url and "github.com/statisticsnorway" in repository_url and not name.startswith("ssb-libtest"):
            formatted_results.append({
                "Name": result.get("name"),
                "Platform": result.get("platform"),
                "Latest Version": result.get("latest_release_number"),
                "Last Updated": result.get("latest_release_published_at"),
                "Description": result.get("description"),
                "Homepage": result.get("homepage"),
                "Repository": repository_url,
                "Contributors": result.get("contributors_count", 0),  
                "Keywords": ", ".join(result.get("keywords", [])),
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
    # Get the API key from the environment
    api_key = os.getenv("LIBRARIESIO_API_KEY")
    if not api_key:
        raise Exception("API key not found. Please set LIBRARIESIO_API_KEY in the environment.")

    query = "statisticsnorway"  # Fixed query
    print(f"Searching Libraries.io for '{query}' across all platforms...")
    
    # Fetch all results across all pages
    results = fetch_all_results(query, api_key)

    print(f"Fetched {len(results)} results.")
    
    # Save results
    save_results_to_csv(results)

if __name__ == "__main__":
    main()
