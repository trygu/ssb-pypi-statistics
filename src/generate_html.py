import pandas as pd
import json
from collections import defaultdict

def sanitize(value):
    """Sanitize values to ensure safe JSON/JavaScript output."""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        return value.replace('"', '\\"').replace("\n", " ").replace("\r", " ")
    return value

def generate_html(csv_file="./src/results.csv", template_file="./src/table_template.html", output_file="./src/index.html"):
    """Generate an HTML page from the CSV data using a template."""
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file '{csv_file}' is empty or invalid.")
        return

    # Ensure required columns exist
    if df.empty or 'Platform' not in df.columns or 'Last Updated' not in df.columns:
        print("Error: Required data not found in the CSV.")
        platform_counts = {}
        platform_activity = {}
        total_packages = 0
        last_updated = "N/A"
        sanitized_table_data = []
    else:
        # Sanitize and calculate statistics
        sanitized_table_data = df.applymap(sanitize).to_dict(orient="records")
        total_packages = len(df)
        platform_counts = df['Platform'].value_counts().to_dict()

        # Extract the most recent "Downloaded At" timestamp
        if 'Downloaded At' in df.columns:
            last_updated = pd.to_datetime(df['Downloaded At'], errors='coerce').max()
            last_updated = last_updated.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(last_updated) else "N/A"
        else:
            last_updated = "N/A"

        # Calculate update activity
        platform_activity = defaultdict(lambda: defaultdict(int))
        df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

        # Group by platform and month-year
        monthly_updates = df.groupby([df['Platform'], df['Last Updated'].dt.to_period("M")]).size()

        # Reformat for JS injection
        for (platform, period), count in monthly_updates.items():
            platform_activity[platform][str(period)] = count

    # Convert to JSON
    table_rows = json.dumps(sanitized_table_data, ensure_ascii=False)
    total_packages_json = json.dumps(total_packages)
    platform_counts_json = json.dumps(platform_counts, ensure_ascii=False)
    platform_activity_json = json.dumps(platform_activity, ensure_ascii=False)

    # Inject data into HTML
    with open(template_file, "r") as template:
        html = template.read()

    html = html.replace("const tableData = [];", f"const tableData = {table_rows};")
    html = html.replace("const totalPackages = 0;", f"const totalPackages = {total_packages_json};")
    html = html.replace("const platformCounts = {};", f"const platformCounts = {platform_counts_json};")
    html = html.replace("const platformActivity = {};", f"const platformActivity = {platform_activity_json};")
    html = html.replace("<span id='last-updated'>N/A</span>", f"<span id='last-updated'>{last_updated}</span>")

    with open(output_file, "w") as output:
        output.write(html)

    print(f"HTML file generated at '{output_file}'.")

if __name__ == "__main__":
    generate_html()
