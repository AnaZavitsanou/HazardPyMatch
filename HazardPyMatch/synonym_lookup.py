# synonym_lookup.py
import pandas as pd
import os
import re
import requests

def filter_unique_cas_and_compile_synonyms(df_inventory):
    """Filters unique CAS numbers and compiles in-list synonyms for each CAS."""
    
    print("....................Filtering Unique CAS Numbers and Compiling Synonyms")

    # Ensure CAS Numbers are treated as strings
    df_inventory['CAS Number'] = df_inventory['CAS Number'].astype(str)

    # Sort the dataframe based on CAS Number
    df_sorted = df_inventory.sort_values(by='CAS Number')

    # Store unique CAS numbers
    unique_cas_nums = pd.DataFrame(columns=df_inventory.columns)

    # List to collect synonyms
    new_columns_data = []

    # Group by CAS Number and extract unique chemical names
    for cas_number, group in df_sorted.groupby('CAS Number'):
        # Get the first entry for this CAS number
        first_entry = group.iloc[0].to_frame().T
        unique_cas_nums = pd.concat([unique_cas_nums, first_entry], ignore_index=True)

        # Extract unique chemical names associated with this CAS
        chemical_names = group['Chemical Name'].tolist()
        unique_chemical_names = list(dict.fromkeys(chemical_names))  # Remove duplicates

        # Append to new column data
        new_columns_data.append(unique_chemical_names)

    # Handle empty synonym lists
    if not new_columns_data or all(len(names) == 0 for names in new_columns_data):
        print("⚠️ No chemicals in this inventory with relevant GHS codes!")
        return df_inventory  # No changes

    # Create a DataFrame to store synonyms dynamically
    max_names = max(len(names) for names in new_columns_data)
    chemical_names_df = pd.DataFrame([
        names + [None] * (max_names - len(names)) for names in new_columns_data
    ], columns=[f'In-List Synonym {i+1}' for i in range(max_names)])

    # Merge with unique CAS DataFrame
    unique_cas_nums = pd.concat([unique_cas_nums.reset_index(drop=True), chemical_names_df.reset_index(drop=True)], axis=1)

    print("....................Unique Chemical Name Compilation Complete")
    
    return unique_cas_nums



def fetch_synonyms_from_pubchem(chemical_name):
    """Fetches synonyms for a given chemical name from PubChem API."""
    results = []

    try:
        # Primary request: PubChem Compound API
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/synonyms/TXT"
        response = requests.get(url)

        # Check if request was successful
        if response.status_code == 200:
            synonyms_text = response.text.strip().split("\n")
            results.append([chemical_name] + synonyms_text)
        elif response.status_code == 404:
            # Fallback: Use PubChem Substance API
            substance_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{chemical_name}/synonyms/TXT"
            substance_response = requests.get(substance_url)

            if substance_response.status_code == 200:
                synonyms_text = substance_response.text.strip().split("\n")
                results.append([chemical_name] + synonyms_text)
            else:
                print(f"⚠️ No synonyms found for {chemical_name} in PubChem.")
                results.append([chemical_name, "No synonyms found"])

    except Exception as e:
        print(f"⚠️ Error fetching synonyms for {chemical_name}: {e}")
        results.append([chemical_name, "Error retrieving synonyms"])

    return results if results else [[chemical_name, "No synonyms found"]]

def add_synonyms_to_inventory(df_inventory, print_intermediate_steps=False, source_folder=None):
    """Adds PubChem synonyms to the chemical inventory DataFrame after filtering unique names."""

    print("....................Adding Synonyms to Inventory")

    # Step 1️⃣: Filter unique chemical names before fetching from PubChem
    df_inventory = filter_unique_cas_and_compile_synonyms(df_inventory)

    # Step 2️⃣: Fetch synonyms for **each unique CAS Number**
    synonym_results = df_inventory["CAS Number"].apply(fetch_synonyms_from_pubchem)

    # Step 3️⃣: Convert results into a DataFrame with variable columns
    max_synonyms = max(len(res) for res in synonym_results)
    synonyms_df = pd.DataFrame(synonym_results.tolist(), columns=["CAS Number"] + [f"PubChem Synonym {i+1}" for i in range(1, max_synonyms)])

    # Step 4️⃣: Merge synonyms into df_inventory
    df_inventory = df_inventory.merge(synonyms_df, on="CAS Number", how="left")

    # Step 5️⃣: Deduplicate synonyms in inventory
    print("....................Removing Duplicate Synonyms")
    for index, row in df_inventory.iterrows():
        for col in df_inventory.columns[4:]:  # Skip first few columns (ID, Chemical Name, etc.)
            if pd.notna(row[col]):
                unique_values = list(dict.fromkeys(row[col].split(";")))  # Remove duplicates while maintaining order
                df_inventory.at[index, col] = ";".join(unique_values)

    # Step 6️⃣: Save updated inventory if needed
    if print_intermediate_steps and source_folder:
        output_path = os.path.join(source_folder, "df_inventory_withSynonyms.xlsx")
        df_inventory.to_excel(output_path, index=False)
        print(f"✅ Updated inventory with synonyms saved to: {output_path}")

    print("....................Synonym Lookup & Cleanup Complete")
    
    # Replace df_inventory with output_df
    output_df = df_inventory.copy()

    print('Removing duplicate synonyms')
    for index, row in output_df.iterrows():
        for col in output_df.columns[4:]:  # Skip first few columns
            if pd.notna(row[col]):  
                # Split the cell content into a list of values, remove duplicates while maintaining order, and rejoin
                unique_values = list(dict.fromkeys(row[col].split(";")))
                output_df.at[index, col] = ";".join(unique_values)

    # Print shape of the final dataframe
    dims = output_df.shape
    print(f"Final dataset dimensions: {dims}")
    df_inventory = output_df

    # Save the cleaned dataframe
    output_filename = 'df_inventory_relevantGHScodes_uniquecodes_inlistsyns_ncbisyns.xlsx'
    output_path = os.path.join(source_folder, output_filename)
    df_inventory.to_excel(output_path, index=False)
    print(f"Excel file saved to: {output_path}")

    return df_inventory
