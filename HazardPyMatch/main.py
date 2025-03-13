# main.py (Entry Point for User Prompts and Execution)

from paths import prompt_user_paths
from inventory_loader import load_inventory, prompt_print_intermediate_steps
from ghs_scraper import get_relevant_ghs_codes

def main():
    print("Starting Hazard Analysis Pipeline...")
    source_folder, protocols_folder = prompt_user_paths()
    print_intermediate_steps = prompt_print_intermediate_steps()
    relevant_ghs_codes = get_relevant_ghs_codes()
    
    df = load_inventory(source_folder)
    
    print("Processing complete with the following settings:")
    print(f"Source Folder: {source_folder}")
    print(f"Protocols Folder: {protocols_folder}")
    print(f"Print Intermediate Steps: {print_intermediate_steps}")
    print(f"Relevant GHS Codes: {relevant_ghs_codes}")

if __name__ == "__main__":
    main()

