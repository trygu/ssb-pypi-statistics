def save_results_to_csv(results, api_key, github_token, output_file="./src/results.csv"):
    """
    Format the search results, fetch GitHub metadata, and save to CSV.
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

        # Fetch GitHub metadata safely
        github_metadata = fetch_github_metadata(repository_url, github_token) or {}
        owner_info = github_metadata.get("owner", {})

        # Append cleaned data
        formatted_results.append({
            "Name": result.get("name", "N/A"),
            "Platform": result.get("platform", "N/A"),
            "Latest Version": result.get("latest_release_number", "N/A"),
            "Last Updated": result.get("latest_release_published_at", "N/A"),
            "Description": result.get("description", "N/A"),
            "Homepage": result.get("homepage", "N/A"),
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
