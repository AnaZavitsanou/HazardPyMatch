# main.py (HazardPyMatch Pipeline)

import os
import pandas as pd
from paths import prompt_user_paths
from inventory_loader import load_inventory, prompt_print_intermediate_steps, get_relevant_ghs_codes
from cas_lookup import extract_missing_cas
from ghs_scraper import update_ghs_codes
from ghs_filter import filter_ghs_codes
from synonym_lookup import add_synonyms_to_inventory
from protocol_matcher import match_hazards_in_protocols
from visualization import plot_ghs_code_distribution, plot_hazardous_protocols, plot_cas_occurrences

def main():
    print("🚀 Starting Hazard Analysis Pipeline...\n")

    # ✅ Step 1: User Inputs
    source_folder, protocols_folder = prompt_user_paths()
    print_intermediate_steps = prompt_print_intermediate_steps()
    relevant_ghs_codes = get_relevant_ghs_codes()

    # ✅ Step 2: Load Chemical Inventory
    df_inventory = load_inventory(source_folder)

    # ✅ Step 3: Process Missing CAS Numbers
    df_inventory, df_proprietaryRxs_andOther = extract_missing_cas(
        df_inventory, 
        print_intermediate_steps=print_intermediate_steps, 
        source_folder=source_folder
    )

    # ✅ Step 4: Retrieve GHS Hazard Codes
    df_inventory = update_ghs_codes(
        df_inventory, 
        print_intermediate_steps=print_intermediate_steps, 
        source_folder=source_folder
    )

    # ✅ Step 5: Filter Relevant GHS Codes
    relevant_ghs_df, other_ghs_df = filter_ghs_codes(
        df_inventory, 
        relevant_ghs_codes, 
        print_intermediate_steps=print_intermediate_steps, 
        source_folder=source_folder
    )

    # ✅ Step 6: Lookup Synonyms for Inventory Chemicals
    df_inventory = add_synonyms_to_inventory(
        relevant_ghs_df, 
        print_intermediate_steps=print_intermediate_steps, 
        source_folder=source_folder
    )

    # ✅ Step 7: Match Hazards in Protocols
    df_hazards, df_matched_details = match_hazards_in_protocols(
        df_inventory, 
        protocols_folder, 
        source_folder
    )

    # ✅ Step 8: Generate Visualizations
    plot_ghs_code_distribution(df_inventory, source_folder=source_folder)
    plot_hazardous_protocols(df_hazards, source_folder=source_folder)
    plot_cas_occurrences(df_inventory, source_folder=source_folder)

    # ✅ Summary Output
    print("\n✅ Processing complete with the following settings:")
    print(f"📂 Source Folder: {source_folder}")
    print(f"📂 Protocols Folder: {protocols_folder}")
    print(f"📊 Print Intermediate Steps: {print_intermediate_steps}")
    print(f"🔍 Relevant GHS Codes: {relevant_ghs_codes}")
    print(f"📄 Processed Inventory saved to: {source_folder}/df_inventory_withGHScodes.xlsx")
    print(f"❌ Missing CAS Numbers saved to: {source_folder}/Chemical_List_noCAS.xlsx")
    print(f"⚠️ Hazardous Protocols saved to: {source_folder}/hazards_in_protocols.xlsx")
    print(f"🔍 Protocol Matched Hazard Details saved to: {source_folder}/protocol_matched_hazard_details.xlsx")
    print(f"📊 Visualizations saved in: {source_folder}")

    print("\n🎉 Hazard Analysis Pipeline Completed Successfully!")

if __name__ == "__main__":
    main()
