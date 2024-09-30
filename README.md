# PDF Data Extraction and CSV Generation

## Description

This Python script extracts data from tables within PDF files located in a specified directory. It processes reference codes and gencodes, applies predefined replacements, and generates structured CSV files for easier data analysis.

## Requirements

- Python 3.x
- Libraries:
  - `pdfplumber` (for PDF processing)
- Standard libraries:
  - `re`
  - `collections`
  - `os`

## Files

### `script.py`

This is the primary script responsible for:

1. **Extracting Data**: Reads tables from PDFs and accumulates relevant text and UVC counts.
2. **Processing Codes**: Extracts reference codes and gencodes using regular expressions.
3. **Preparing Results**: Combines reference codes, gencodes, and UVC values into a structured format.
4. **Saving Output**: Writes the extracted data into CSV files, creating a new file whenever the reference code changes.

#### Key Functions

- `extract_table_data(pdf_path)`: 
  - Extracts text and UVC values from each PDF page.

- `extract_ref_cdes_and_gencodes(all_text)`:
  - Uses regex to find reference codes and their associated gencodes.

- `prepare_final_results(results, all_nbre_uvc_values)`:
  - Formats the final data for CSV output, applying gencode replacements.

- `save_to_csv(final_results, pdf_filename, main_folder)`:
  - Saves data to CSV files, organized by reference code.

### `run_script.cmd`

This batch file allows you to run `script.py` with a double-click, simplifying execution without needing to use the command line directly.

## Setup Instructions

1. **Install Dependencies**:
   - Ensure you have Python installed.
   - Install the `pdfplumber` library using pip:
     ```bash
     pip install pdfplumber
     ```

2. **Update the Script**:
   - Modify the `pdf_directory` variable in `script.py` to point to the directory containing your PDF files.

3. **Run the Script**:
   - You can run the script directly in the terminal:
     ```bash
     python script.py
     ```
     > Windows:
   - Alternatively, use `run_script.cmd` to execute it with a double-click.
     > Mac:
   - Alternatively, use `run_script.sh` to execute it with a double-click.

## Output

- The script creates a folder named `<original_folder_name>_CSV`, where all generated CSV files will be stored.
- Each CSV file corresponds to a PDF file and contains data formatted as follows:

    - **Header Format**:
      ```
      H;HCEN3;HCEN3;;SDH;{ref_code};{date};{date};1;1
      ```

    - **Data Format**:
      ```
      L;{gencode};UN;{nbre_uvc}
      ```

## Gencode Replacement Mapping

The script includes a mapping for gencode replacements to ensure consistency in data output:

```python
gencode_replacement = {
    "314007": "107812",
    "345010": "111474",
    "317025": "3342",
    "337011": "107811",
    "336015": "107884",
    "311037": "107810"
}
