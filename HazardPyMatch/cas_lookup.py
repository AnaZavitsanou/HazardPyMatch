# cas_lookup.py
import requests
import pandas as pd
import os

print("....................Populating missing CAS Numbers")

def get_cas_number(chemical_name):
    """Fetch CAS number from PubChem API using a chemical name."""
    try:
        # Construct the primary search URL for PubChem
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/xrefs/RegistryID/JSON"
        response = requests.get(search_url)

        if response.status_code == 200:
            # Extract CAS Number from response content
            response_data = response.json()
            # Locate the CAS Number in the JSON response
            registry_ids = response_data.get("InformationList", {}).get("Information", [])
            for entry in registry_ids:
                if "CAS" in entry.get("RegistryID", ""):
                    return entry["RegistryID"]  # Return CAS Number immediately if found

        # If the first URL does not return a result, try the fallback URL
        fallback_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{chemical_name}/xrefs/RegistryID/JSON"
        response = requests.get(fallback_url)

        if response.status_code == 200:
            # Extract CAS Number from the fallback response
            response_data = response.json()
            registry_ids = response_data.get("InformationList", {}).get("Information", [])
            for entry in registry_ids:
                if "CAS" in entry.get("RegistryID", ""):
                    return entry["RegistryID"]  # Return CAS Number

        return None  # Return None if no result is found in both URLs

    except Exception as e:
        print(f"Error fetching CAS Number for {chemical_name}: {e}")
        return None

def clean_cas_number(cas_number):
    """Cleans and formats CAS numbers by removing invalid characters and fixing format."""
    if pd.isna(cas_number) or cas_number in ["", 0]:
        return ""
    
    # Remove "00:00:00" or other trailing text form CAS Number if present
    cas_number = str(cas_number).strip().split(" ")[0]  
    
    # Define invalid characters
    invalid_chars = set(",./?!@#$%^&*():;\"'")

    # Remove CAS Numbers containing letters or invalid characters
    if any(char.isalpha() or char in invalid_chars for char in cas_number):
        return ""

    # Ensure CAS Number follows the correct format (remove leading zero in the last segment)
    if "-" in cas_number:
        parts = cas_number.split("-")
        if len(parts) == 3:
            try:
                parts[2] = str(int(parts[2]))  # Remove leading zeros
                return "-".join(parts)
            except ValueError:
                print(f"Error processing CAS Number: {cas_number}")
                return ""

    return cas_number

def extract_missing_cas(df_inventory, print_intermediate_steps=False, source_folder=None):
    """Extract and process missing CAS numbers in the inventory."""
    
    print("....................Extracting and processing missing CAS Numbers")

    # Identify rows where CAS Number is missing
    missing_cas_mask = df_inventory["CAS Number"].isna() | (df_inventory["CAS Number"] == "") | (df_inventory["CAS Number"] == 0)
    
    # Apply get_cas_number function only to missing CAS values
    df_inventory.loc[missing_cas_mask, "CAS Number"] = df_inventory.loc[missing_cas_mask, "Chemical Name"].apply(get_cas_number)

    # Separate proprietary/unidentified chemicals (still missing CAS numbers)
    df_proprietaryRxs_andOther = df_inventory[df_inventory["CAS Number"].isna() | (df_inventory["CAS Number"] == "")]
    
    # Drop rows where CAS was not found
    df_inventory = df_inventory.dropna(subset=["CAS Number"]).copy()

    # Normalize Chemical Name format for proprietary chemicals
    df_proprietaryRxs_andOther["Chemical Name"] = df_proprietaryRxs_andOther["Chemical Name"].str.strip().str.lower().str.title()
    df_proprietaryRxs_andOther = df_proprietaryRxs_andOther.drop_duplicates(subset="Chemical Name", keep="first")

    # ✅ Always save the list of chemicals with missing CAS numbers
    missing_cas_output_path = os.path.join(source_folder, "Chemical_List_noCAS.xlsx")
    df_proprietaryRxs_andOther.to_excel(missing_cas_output_path, index=False)
    print(f"✅ Missing CAS numbers saved to: {missing_cas_output_path}")

    # ✅ Save full inventory only if print_intermediate_steps is enabled
    if print_intermediate_steps and source_folder:
        inventory_output_path = os.path.join(source_folder, "df_inventory_withCAS.xlsx")
        df_inventory.to_excel(inventory_output_path, index=False)
        print(f"✅ Updated inventory saved to: {inventory_output_path}")

    print("....................CAS Number processing complete")
    
    return df_inventory, df_proprietaryRxs_andOther

if __name__ == "__main__":
    # Example usage: Load chemical inventory and process CAS numbers
    df_inventory = pd.read_excel("path/to/chemical_inventory.xlsx")

    # Clean existing CAS numbers
    df_inventory["CAS Number"] = df_inventory["CAS Number"].apply(clean_cas_number)

    # Extract and update missing CAS numbers
    df_inventory, df_proprietaryRxs_andOther = extract_missing_cas(
        df_inventory, 
        print_intermediate_steps=True, 
        source_folder="path/to/output"
    )

    # ✅ Save the updated inventory
    inventory_output_path = "path/to/updated_inventory.xlsx"
    df_inventory.to_excel(inventory_output_path, index=False)
    print(f"✅ Final inventory saved to: {inventory_output_path}")

    print("CAS Number processing completed.")