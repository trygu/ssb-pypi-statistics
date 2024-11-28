# SSB Package Statistics Viewer

This project provides a tool to download, process, and interactively explore statistics about public packages using the [Libraries.io API](https://libraries.io/). It fetches data about all public packages associated with Statistics Norway and presents the results in an interactive table format.

If you're just interested in the processed results, visit the [GitHub Pages deployment](https://trygu.github.io/ssb-pypi-statistics/).

## Features

- **Package Data Fetching**: Fetches data about all public packages from Libraries.io.
- **Interactive Table**: Displays package data in a dynamic, searchable, and sortable table using [Tabulator.js](http://tabulator.info/).
- **CSV Download**: Allows users to download the dataset as a CSV file for offline use.
- **DuckDB Integration**: Easily query and sample the data in the DuckDB Web Shell for further analysis.

## Requirements

To fetch and process data using the Libraries.io API:
1. **Libraries.io API Key**:
   - You'll need a valid API key from Libraries.io. You can sign up for one [here](https://libraries.io/account).
   - Add your API key to the appropriate part of the data-fetching script.

2. **Python Environment**:
   - Install the required Python dependencies:
     ```bash
     pip install pandas requests
     ```

## How to Use

### 1. Download and Process Data
Run the data-fetching script to download the package data:
```bash
python fetch_data.py
```
The script will:
- Fetch all public packages associated with Statistics Norway from Libraries.io.
- Save the results as `results.csv` in the `src/` directory.

### 2. Open the Results Viewer
- Open `index.html` in your browser to view the interactive table.

### 3. Explore the Results
- Use the **"Download CSV"** button to save the data for offline use.
- Use the **"Open in DuckDB Web Shell"** button to query the dataset directly in the DuckDB Web Shell.

### Preprocessed Results
If you don't want to fetch and process the data yourself, you can access the processed results directly:
- [Interactive Viewer on GitHub Pages](https://trygu.github.io/ssb-pypi-statistics/)

## DuckDB Query Example

The DuckDB Web Shell button includes a query to:
1. Load the dataset into a table called `ssb_packages`.
2. Sample 10 random rows from the table.

The SQL query used:
```sql
-- Load CSV file and create a table
CREATE TABLE ssb_packages AS
SELECT *
FROM read_csv_auto('https://trygu.github.io/ssb-pypi-statistics/results.csv');

-- Sample 10 rows from the table
FROM ssb_packages USING SAMPLE 10;
```

## Development Notes

- Ensure the API key is correctly configured in the `fetch_data.py` script before running it.
- The data viewer (`index.html`) is designed to use a preprocessed `results.csv`. Modify the DuckDB query URL in the HTML if hosting the dataset elsewhere.

## Credits

- [Libraries.io API](https://libraries.io/)
- [DuckDB](https://duckdb.org/)
- [Tabulator.js](http://tabulator.info/)

## License

This project is licensed under the [MIT License](LICENSE).
