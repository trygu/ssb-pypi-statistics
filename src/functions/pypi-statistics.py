import requests
import re
import pandas as pd

def fetch_pypi_projects():
    """
    Fetch all project names from PyPi using the simple index API.
    """
    response = requests.get("https://pypi.org/simple/")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch PyPi index: {response.status_code}")
    
    project_names = re.findall(r'<a href=".*?">(.*?)</a>', response.text)
    return project_names

def fetch_project_metadata(project_name):
    """
    Fetch the metadata of a specific project from the PyPi JSON API.
    """
    url = f"https://pypi.org/pypi/{project_name}/json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def filter_statisticsnorway_projects(projects):
    """
    Filter projects that have their repository URL under statisticsnorway GitHub.
    """
    matching_projects = []
    for project in projects:
        metadata = fetch_project_metadata(project)
        if metadata:
            project_info = metadata.get("info", {})
            project_urls = project_info.get("project_urls", {}) or {}
            repo_url = (
                project_info.get("home_page") or
                project_urls.get("Source") or
                project_urls.get("Repository") or ""
            )
            if "github.com/statisticsnorway" in repo_url:
                author = project_info.get("author", "Unknown")
                readme_url = project_urls.get("Documentation", repo_url + "/blob/main/README.md")
                matching_projects.append({
                    "Name": project,
                    "Author": author,
                    "GitHub Repository": repo_url,
                    "README Link": readme_url
                })
    
    return matching_projects

if __name__ == "__main__":
    print("Fetching PyPi projects...")
    all_projects = fetch_pypi_projects()
    
    print(f"Found {len(all_projects)} projects. Filtering for GitHub repositories under statisticsnorway...")
    statsnorway_projects = filter_statisticsnorway_projects(all_projects)
    
    print(f"Found {len(statsnorway_projects)} projects under statisticsnorway.")
    
    # Convert results to a DataFrame
    df = pd.DataFrame(statsnorway_projects)
    
    # Display the table
    import ace_tools as tools; tools.display_dataframe_to_user(name="Statistics Norway PyPi Projects", dataframe=df)
    
    # Save as CSV (optional)
    df.to_csv("statisticsnorway_pypi_projects.csv", index=False)
