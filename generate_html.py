import pandas as pd

def generate_html(csv_file="./src/results.csv", template_file="./src/table_template.html", output_file="./src/index.html"):
    """
    Generate an HTML page from the CSV data using a template.
    """
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Generate HTML rows
    rows = ""
    for _, row in df.iterrows():
        rows += "<tr>"
        rows += f"<td>{row['Name']}</td>"
        rows += f"<td>{row['Platform']}</td>"
        rows += f"<td>{row['Latest Version']}</td>"
        rows += f"<td>{row['Last Updated']}</td>"
        rows += f"<td>{row['Description']}</td>"
        rows += f"<td><a href='{row['Homepage']}'>Homepage</a></td>"
        rows += f"<td><a href='{row['Repository']}'>Repository</a></td>"
        rows += f"<td>{row['Stars']}</td>"
        rows += f"<td>{row['Forks']}</td>"
        rows += f"<td>{row['Contributors']}</td>"
        rows += "</tr>"

    # Read the template
    with open(template_file, "r") as template:
        html = template.read()

    # Inject rows into the template
    html = html.replace("<!-- CSV rows will be inserted here -->", rows)

    # Write the output HTML file
    with open(output_file, "w") as output:
        output.write(html)

    print(f"HTML file generated at '{output_file}'.")

if __name__ == "__main__":
    generate_html()
