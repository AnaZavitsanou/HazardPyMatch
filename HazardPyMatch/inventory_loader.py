# inventory loader - load chemical inventory and prompt user for answers to questions
 
import os
import pandas as pd

def prompt_print_intermediate_steps():
    """Prompts the user to decide whether to print intermediate steps."""
    response = input("Would you like to print intermediate steps? (yes/no): ").strip().lower()
    return response == 'yes'

def get_relevant_ghs_codes():
    """Prompts the user to input relevant GHS hazard codes."""
    print("\nEnter relevant GHS hazard codes separated by commas (e.g., H200,H201,H360FD).")
    relevant_ghs_codes = input("GHS Codes: ").strip().split(',')
    return [code.strip().upper() for code in relevant_ghs_codes if code.strip()]


def load_inventory(source_folder):
    """Loads the Chemical Inventory from a .xlsx or .csv file."""
    
    # Search for inventory file (must contain 'Chemical_Inventory' in its name)
    inventory_files = [f for f in os.listdir(source_folder) if 'Chemical_Inventory' in f and f.endswith(('xlsx', 'csv'))]

    if not inventory_files:
        raise FileNotFoundError("No Chemical Inventory file found with 'Chemical_Inventory' in the name.")

    file_path = os.path.join(source_folder, inventory_files[0])  # Load the first matching file
    print(f"📂 Loading file: {file_path}")

    # Load file into Pandas DataFrame
    df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)

    # Always print the first few rows of the inventory
    print("\n🔍 Inventory Preview:\n", df.head())

    return df