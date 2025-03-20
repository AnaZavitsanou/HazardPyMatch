# protocol_matcher.py

import os
import re
import pandas as pd
import pdfplumber

def get_protocol_filenames(protocols_folder):
    """Retrieves the list of PDF filenames (without extensions) from the given folder."""
    return [os.path.splitext(f)[0] for f in os.listdir(protocols_folder) if f.endswith('.pdf')]

def create_master_list(df_inventory):
    """Creates a master list containing CAS Numbers, synonyms, PubChem IDs, and GHS Codes."""
    print("....................Creating Master List for Protocol Matching")

    master_list = []

    for _, row in df_inventory.iterrows():
        cas_number = row['CAS Number']
        pubchem_id = row['PubChem ID']
        ghs_codes = row['GHS Codes']
        synonyms = row[4:]  # Get all synonyms starting from the 5th column

        for synonym in synonyms:
            if pd.notna(synonym):  # Ensure synonym is not NaN
                master_list.append((cas_number, synonym.strip(), pubchem_id, ghs_codes))

    # Convert master list to DataFrame
    master_list_df = pd.DataFrame(master_list, columns=['CAS Number', 'Synonym', 'PubChem ID', 'GHS Codes'])
    master_list_df.columns = master_list_df.columns.str.replace(' ', '_')

    return master_list_df

def match_hazards_in_protocols(df_inventory, protocols_folder, source_folder):
    """Matches hazards from the chemical inventory against protocol PDFs."""
    print("....................Matching Hazards in Protocols")

    master_list_df = create_master_list(df_inventory)

    hazards = []
    matched_details = []

    # Iterate through the protocol PDF files
    for filename in os.listdir(protocols_folder):
        print(f"Processing protocol: {filename}")  # Current file being processed
        
        if filename.endswith('.pdf') and filename != "Hazards In Protocols.txt":
            extracted_text = ''  # Initialize extracted text for the current PDF
            try:
                with pdfplumber.open(os.path.join(protocols_folder, filename)) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text() or ''  # Extract text from each page

            except Exception as e:
                print(f"Error processing {filename}: {e}")  # Handle PDF processing errors
                continue

            # Search for matches in the extracted text across all synonyms
            matched_cas_numbers = []
            matched_pubchem_ids = []
            matched_ghs_codes = []

            for row in master_list_df.itertuples(index=False):
                cas_number, synonym, pubchem_id, ghs_codes = row

                # Perform case-sensitive whole-word matching using regex
                pattern = fr'\b{re.escape(synonym)}\b'
                if re.search(pattern, extracted_text):  # Check for whole-word match
                    matched_cas_numbers.append(cas_number)
                    matched_pubchem_ids.append(pubchem_id)
                    matched_ghs_codes.append(ghs_codes)

                    # Append details for matched synonyms
                    matched_details.append({
                        'Protocol': filename,
                        'Synonym': synonym,
                        'CAS Number': cas_number,
                        'PubChem_ID': pubchem_id,
                        'GHS_Codes': ghs_codes
                    })

            # Remove duplicate CAS numbers while keeping order
            unique_cas_set = set()
            unique_details = []
            unique_matched_cas_numbers = []
            unique_matched_pubchem_ids = []
            unique_matched_ghs_codes = []

            for i, cas in enumerate(matched_cas_numbers):
                if cas not in unique_cas_set:
                    unique_cas_set.add(cas)
                    unique_matched_cas_numbers.append(cas)
                    unique_matched_pubchem_ids.append(matched_pubchem_ids[i])
                    unique_matched_ghs_codes.append(matched_ghs_codes[i])
                    unique_details.append(matched_details[i])

            matched_cas_numbers = unique_matched_cas_numbers
            matched_pubchem_ids = unique_matched_pubchem_ids
            matched_ghs_codes = unique_matched_ghs_codes
            matched_details = unique_details

            # Prepare hazard entry for each protocol
            list_name = filename.replace('.pdf', '')
            parts = list_name.split('_', 1)  # Split at the first underscore
            protocol = parts[0]
            source = parts[1] if len(parts) > 1 else ""

            if not matched_cas_numbers:
                matched_hazards_str = "N/A"
                print(f"No matches found for {filename}")
            else:
                matched_hazards_str = ', '.join(matched_cas_numbers)
                print(f"Matched CAS numbers for {filename}: {matched_hazards_str}")

            # Append protocol, source, and matched CAS numbers to hazards list
            hazards.append([protocol, source, matched_hazards_str])

    # Convert hazards list to a DataFrame
    df_hazards = pd.DataFrame(hazards, columns=['Protocol', 'Source', 'Hazards'])

    # Convert matched details list to a DataFrame
    df_matched_details = pd.DataFrame(matched_details, columns=['Protocol', 'Synonym', 'CAS Number', 'PubChem_ID', 'GHS_Codes'])

    # Save the hazards DataFrame to an Excel file
    hazards_output_path = os.path.join(source_folder, "hazards_in_protocols.xlsx")
    df_hazards.to_excel(hazards_output_path, index=False)
    print(f"Hazards in Protocols saved to: {hazards_output_path}")

    # Save the matched details DataFrame to an Excel file
    matched_output_path = os.path.join(source_folder, "protocol_matched_hazard_details.xlsx")
    df_matched_details.to_excel(matched_output_path, index=False)
    print(f"Protocol Matched Hazard Details saved to: {matched_output_path}")

    print("....................Protocol Matching Complete")
    
    return df_hazards, df_matched_details
           
