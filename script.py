import re
from collections import defaultdict
import pdfplumber
import os

# Path to the directory containing the PDF files
pdf_directory = "20240826_190444"  # Change this to your directory path
folder_name = os.path.basename(pdf_directory)  # Get only the last folder name
main_folder = f"{folder_name}_CSV"

# Gencode replacement dictionary
gencode_replacement = {
    "314007": "107812",
    "345010": "111474",
    "317025": "3342",
    "337011": "107811",
    "336015": "107884",
    "311037": "107810"
}

def extract_table_data(pdf_path):
    all_text = ""  # Accumulate all text across pages
    all_nbre_uvc_values = []  # To collect UVC counts across pages

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract table data from the page
                table_data = page.extract_table()

                if table_data:
                    # Accumulate text
                    text = table_data[1][1]  # Adjust if your table structure is different
                    all_text += text + " "  # Add space to separate text from different pages
                    
                    # Check if UVC values exist in the table
                    if len(table_data) > 1 and len(table_data[1]) > 4:
                        nbre_uvc_values = table_data[1][4].split("\n")  # Assuming UVC values are here
                        all_nbre_uvc_values.extend(nbre_uvc_values)  # Collecting UVC counts
    except Exception as e:
        print(f"Error reading PDF: {e}")

    return all_text, all_nbre_uvc_values

def extract_ref_cdes_and_gencodes(all_text):
    # Regex patterns for reference codes and Gencods
    ref_cde_pattern = r"Ref Cde: (\w+)"
    gencode_pattern = r"Gencod : (\d+)"

    # Find all Ref Cde occurrences
    ref_cdes = re.findall(ref_cde_pattern, all_text)

    # Store results in a dictionary
    results = defaultdict(list)

    # Initialize the current position in the text
    current_position = 0

    # Loop through each Ref Cde
    for i in range(len(ref_cdes)):
        ref_cde = ref_cdes[i]
        # Find the position of the current Ref Cde
        ref_position = all_text.index(ref_cde, current_position)

        # Extract Gencods until the next Ref Cde or end of text
        next_ref_position = len(all_text)
        if i + 1 < len(ref_cdes):
            next_ref_cde = ref_cdes[i + 1]
            next_ref_position = all_text.index(next_ref_cde, ref_position) if next_ref_cde in all_text else len(all_text)

        # Extract Gencods in the range
        gencodes_section = all_text[ref_position:next_ref_position]
        gencodes = re.findall(gencode_pattern, gencodes_section)

        # Append unique Gencods to the results
        for gencode in gencodes:
            if gencode not in results[ref_cde]:
                results[ref_cde].append(gencode)

        # Update current position
        current_position = ref_position + len(ref_cde)

    return results

def prepare_final_results(results, all_nbre_uvc_values):
    # Prepare final output with Nbre d’UVC
    final_results = []
    for ref_cde in results.keys():
        gencods = results[ref_cde]

        # Get the corresponding Nbre d’UVC values
        ref_index = list(results.keys()).index(ref_cde)  # Find the index of the reference code
        nbre_uvc_index = ref_index * 2  # Each Ref Cde corresponds to 2 UVC values in your logic

        for j, gencode in enumerate(gencods):
            # Replace gencode if it's in the replacement dictionary
            if gencode in gencode_replacement:
                gencode = gencode_replacement[gencode]

            if nbre_uvc_index + j < len(all_nbre_uvc_values):  # Ensure we don't go out of bounds
                nbre_uvc = all_nbre_uvc_values[nbre_uvc_index + j].strip()  # Strip leading/trailing spaces
                final_results.append({
                    "Ref Cde": ref_cde,
                    "Gencode": gencode,
                    "Nbre d’UVC": nbre_uvc
                })

    return final_results

def save_to_csv(final_results, pdf_filename, main_folder):
    # Create a folder named after the PDF file (without the extension) inside the main folder
    folder_name = os.path.splitext(pdf_filename)[0]
    csv_folder_path = os.path.join(main_folder, folder_name)
    os.makedirs(csv_folder_path, exist_ok=True)

    current_ref_code = None
    output_lines = []
    file_count = 1  # To count the number of CSV files created

    for result in final_results:
        ref_code = result["Ref Cde"]

        if len(ref_code) == 3:
            ref_code += '01'

        gencode = result["Gencode"]
        nbre_uvc = result["Nbre d’UVC"]

        # Check if the reference code has changed
        if current_ref_code != ref_code:
            if output_lines:  # Save previous results if they exist
                filename = os.path.join(csv_folder_path, f"{folder_name}_{file_count}.csv")
                with open(filename, 'w') as f:
                    for line in output_lines:
                        f.write(line + '\n')
                output_lines = []  # Reset for new ref code
                file_count += 1  # Increment the file count

            # Create new header line
            header_line = f"H;HCEN3;HCEN3;;SDH;{ref_code};20240501;20240501;1;1"
            output_lines.append(header_line)
            current_ref_code = ref_code

        # Add line for 'L'
        line = f"L;{gencode};UN;{nbre_uvc}"
        output_lines.append(line)

    # Save the last set of lines if any exist
    if output_lines:
        filename = os.path.join(csv_folder_path, f"{folder_name}_{file_count}.csv")
        with open(filename, 'w') as f:
            for line in output_lines:
                f.write(line + '\n')

# Create the main folder for CSV files
os.makedirs(main_folder, exist_ok=True)

# Process all PDF files in the specified directory
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        print(f"Processing {pdf_path}...")
        
        all_text, all_nbre_uvc_values = extract_table_data(pdf_path)
        results = extract_ref_cdes_and_gencodes(all_text)
        final_results = prepare_final_results(results, all_nbre_uvc_values)
        save_to_csv(final_results, os.path.basename(pdf_path), main_folder)

print("Data extraction and CSV creation completed for all PDF files.")
