import pandas as pd

def sanitize(value):
    """
    Sanitize values to ensure safe and consistent HTML/JavaScript output.
    Replace problematic characters such as quotes and newlines.
    """
    if isinstance(value, str):
        return value.replace('"', '\\"').replace("\n", " ").replace("\r", " ")
    return value

def generate_html(csv_file="./src/results.csv", template_file="./src/table_template.html", output_file="./src/index.html"):
    """
    Generate an HTML page from the CSV data using a template.
    """
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Sanitize the data
    sanitized_table_data = df.applymap(sanitize).to_dict(orient="records")

    # Generate JavaScript-compatible JSON rows for Tabulator
    table_rows = ",\n".join([str(row).replace("'", '"') for row in sanitized_table_data])

    # Read the template
    with open(template_file, "r") as template:
        html = template.read()

    # Inject rows into the TABLE_ROWS_PLACEHOLDER
    html = html.replace("<!-- TABLE_ROWS_PLACEHOLDER -->", table_rows)

    # Write the output HTML file
    with open(output_file, "w") as output:
        output.write(html)

    print(f"HTML file generated at '{output_file}'.")

if __name__ == "__main__":
    generate_html()
