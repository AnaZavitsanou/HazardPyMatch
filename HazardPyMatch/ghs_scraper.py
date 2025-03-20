# ghs_scraper.py 

import requests
import numpy as np
import pandas as pd
import re
import os
from bs4 import BeautifulSoup
from thermo.chemical import Chemical

print("....................Fetching GHS Hazard Codes and Precautionary Statements")

def scrape_precautionary_statements():
    """Scrapes precautionary statement data from PubChem GHS reference page."""
    try:
        result = requests.get(f'https://pubchem.ncbi.nlm.nih.gov/ghs/#_prec', 'lxml')
        soup = BeautifulSoup(result.text, 'lxml')

        gross_precautions_list = []
        p_codes_list = []
        precaution_statements_list = []

        for i in soup.select('#pcode')[0].select('td'):
            gross_precautions_list.append(i.text)

        for i in range(len(gross_precautions_list)):
            if re.search(r'P\d\d\d', gross_precautions_list[i]):
                p_codes_list.append(gross_precautions_list[i])

        for code in p_codes_list:
            precaution_statements_list.append(gross_precautions_list[gross_precautions_list.index(code) + 1])

        # Ensure dataframe is correctly returned
        precaution_data_dict = {'P Codes': p_codes_list, 'Precautionary Statements': precaution_statements_list}
        df_precaution = pd.DataFrame(precaution_data_dict)

        return df_precaution

    except Exception as e:
        print(f"Error scraping precautionary statements: {e}")
        return pd.DataFrame(columns=['P Codes', 'Precautionary Statements'])

def fetch_pubchem_id(cas_number, df_inventory):
    """Attempts to find the PubChem ID (CID) for a given CAS number."""

    try:
        # Attempt to find PubChem ID using thermo.chemical.Chemical
        chem = Chemical(str(cas_number))
        if chem.PubChem:
            return chem.PubChem
        else:
            raise ValueError("No PubChem ID found via thermo.chemical.Chemical")

    except Exception:
        pass  # Continue to API lookup if thermo lookup fails

    try:
        # First attempt: Use PubChem Compound API
        compound_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas_number}/cids/JSON"
        response = requests.get(compound_url)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Parse JSON response for compound
        data = response.json()
        if 'IdentifierList' in data and 'CID' in data['IdentifierList']:
            cid = data['IdentifierList']['CID'][0]  # Get the first CID
            df_inventory.loc[df_inventory['CAS Number'] == cas_number, 'PubChem ID'] = cid
            print(f"✅ CID {cid} added to 'PubChem ID' for CAS: {cas_number}")  
            return cid
        else:
            raise ValueError("No CID found in Compound API response")

    except Exception:
        try:
            # Fallback: Use PubChem Substance API
            substance_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{cas_number}/cids/JSON"
            response = requests.get(substance_url)
            response.raise_for_status()  # Raise an error for HTTP issues

            # Parse JSON response for substance
            data = response.json()

            if 'InformationList' in data and 'Information' in data['InformationList']:
                # Extract CID from the first match in the substance response
                cids = [
                    cid
                    for info in data['InformationList']['Information']
                    if 'CID' in info
                    for cid in info['CID']
                ]
                if cids:
                    df_inventory.loc[df_inventory['CAS Number'] == cas_number, 'PubChem ID'] = cids[0]
                    print(f"CID {cids[0]} added to 'PubChem ID' using substance database for CAS: {cas_number}")  
                    return cids[0]
                else:
                    raise ValueError("No CID found in Substance API response")
            else:
                raise ValueError("No information found in Substance API response")

        except Exception:
            pass  # Fail silently for unhandled errors

    return None  # Return None if no CID found

# Function to fetch GHS codes from PubChem API if this didn't work with compounds and Pubchem ID (most likely the chemical name is missing a PubchemID)
def fetch_ghs_code(chemical_name):
    try:
        response = requests.get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/substance/{int(chemical_name)}/JSON/?response_type=display&heading=GHS%20Classification','lxml')
        soup = BeautifulSoup(result.text,'lxml').text
        if response.status_code == 200:
            data = response.json()
            # Extracting GHS Codes, placeholder logic (adjust based on actual API structure)
            sections = data.get("Record", {}).get("Section", [])
            for section in sections:
                if "GHS Classification" in section.get("TOCHeading", ""):
                    return section.get("Information", [{}])[0].get("StringValue", "No GHS Codes Found")
            return "No GHS Codes Found"
        else:
            return f"Error {response.status_code}: Unable to fetch data"
    except Exception as e:
        return f"Error: {e}"

def update_ghs_codes(df_inventory, print_intermediate_steps=False, source_folder=None):
    """Fetches and updates GHS hazard classifications based on PubChem IDs or chemical names."""

    # Scrape precautionary statements
    df_precaution = scrape_precautionary_statements()

    # Ensure necessary columns exist before processing
    df_inventory['PubChem ID'] = np.nan
    df_inventory['GHS Codes'] = np.nan
    df_inventory['Precautionary Statements'] = np.nan

    # Lookup GHS classifications using PubChem IDs
    for chem_id in set(df_inventory['PubChem ID'].dropna()):
        try:
            result = requests.get(
                f'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{int(chem_id)}/JSON/?response_type=display&heading=GHS%20Classification',
                'lxml'
            )
            soup = BeautifulSoup(result.text, 'lxml').text

            if len(soup) > 90:
                # Extract GHS H-codes
                pattern_hits = [m.start() for m in re.finditer(r'"H\d\d\d', soup)]
                ghs_codes_set = {soup[ph+1:ph+5] for ph in pattern_hits}
                df_inventory.loc[df_inventory['PubChem ID'] == chem_id, 'GHS Codes'] = ' --- '.join(sorted(ghs_codes_set))

        except Exception as e:
            print(f"⚠️ Error retrieving GHS data for PubChem ID {chem_id}: {e}")

    # Fallback: Use chemical name for GHS classification if no PubChem ID exists
    for index, row in df_inventory.iterrows():
        if not row["GHS Codes"]:
            chemical_name = row["Chemical Name"]
            ghs_code = fetch_ghs_code(chemical_name)
            df_inventory.at[index, "GHS Codes"] = ghs_code

    # Save updated inventory if print_intermediate_steps is enabled
    if print_intermediate_steps and source_folder:
        output_path = os.path.join(source_folder, "df_inventory_withGHScodes.xlsx")
        df_inventory.to_excel(output_path, index=False)
        print(f"Updated inventory with GHS Codes saved to: {output_path}")

    print("....................GHS Code Retrieval Complete")
    return df_inventory