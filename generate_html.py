import pandas as pd

def generate_html(csv_file="./src/results.csv", template_file="./src/table_template.html", output_file="./src/index.html"):
    """
    Generate an HTML page from the CSV data using a template.
    """
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Generate JavaScript-compatible JSON rows for Tabulator
    table_data = df.to_dict(orient="records")
    table_rows = ",\n".join([str(row).replace("'", '"') for row in table_data])

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
