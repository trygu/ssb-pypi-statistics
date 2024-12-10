import pandas as pd
import json

def sanitize(value):
    """Sanitize values to ensure safe JSON/JavaScript output."""
    if pd.isna(value):
        return None  # Replace NaN with None for JSON compatibility
    if isinstance(value, str):
        # Escape double quotes and remove problematic newlines
        return value.replace('"', '\\"').replace("\n", " ").replace("\r", " ")
    return value

def generate_html(csv_file="./src/results.csv", template_file="./src/table_template.html", output_file="./src/index.html"):
    """Generate an HTML page from the CSV data using a template."""
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Sanitize the data
    sanitized_table_data = df.applymap(sanitize).to_dict(orient="records")

    # Calculate package statistics
    total_packages = len(df)
    platform_counts = df['Platform'].value_counts().to_dict()

    # Convert sanitized data to JSON strings
    table_rows = json.dumps(sanitized_table_data)
    total_packages_json = json.dumps(total_packages)
    platform_counts_json = json.dumps(platform_counts)

    # Read the HTML template
    with open(template_file, "r") as template:
        html = template.read()

    html = html.replace("const platformCounts = {};", f"const platformCounts = {platform_counts_json};")
    html = html.replace("const tableData = [];", f"const tableData = {table_rows};")
    html = html.replace("const totalPackages = 0;", f"const totalPackages = {total_packages_json};")
   
    # Write the final HTML file
    with open(output_file, "w") as output:
        output.write(html)

    print(f"HTML file generated at '{output_file}'.")

if __name__ == "__main__":
    generate_html()
