# cas_lookup.py
import requests
import pubchempy as pcp


print(f"....................Populating missing CAS Numbers")

def get_cas_number(chemical_name):
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
                    return entry["RegistryID"]  # Return the CAS Number

        # If the first URL does not return a result, try the fallback URL
        fallback_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{chemical_name}/xrefs/RegistryID/JSON"
        response = requests.get(fallback_url)

        if response.status_code == 200:
            # Extract CAS Number from the fallback response
            response_data = response.json()
            registry_ids = response_data.get("InformationList", {}).get("Information", [])
            for entry in registry_ids:
                if "CAS" in entry.get("RegistryID", ""):
                    return entry["RegistryID"]  # Return the CAS Number

        return None  # Return None if no result is found in both URLs

    except Exception as e:
        print(f"Error finding CAS Number for {chemical_name}: {e}")
        return None

