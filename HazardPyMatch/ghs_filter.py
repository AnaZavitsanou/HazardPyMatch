#ghs_filter.py 

import pandas as pd
import re
import os

def filter_ghs_codes(df_inventory, relevant_ghs_codes, print_intermediate_steps=False, source_folder=None):
    """Filters chemical inventory into relevant and irrelevant GHS codes."""

    print("....................Filtering Relevant GHS Codes")

    # Ensure "GHS Codes" column exists
    if "GHS Codes" not in df_inventory.columns:
        raise KeyError("The DataFrame must contain a 'GHS Codes' column.")

    # Define regex pattern for H-codes
    pattern = r'H\d{3}[A-Z]*'

    # Extract all H### codes from GHS Codes cell
    df_inventory["Extracted GHS"] = df_inventory["GHS Codes"].apply(
        lambda x: re.findall(pattern, str(x)) if pd.notna(x) else []
    )

    # Determine relevance using vectorized filtering
    relevant_mask = df_inventory["Extracted GHS"].apply(lambda codes: any(code in relevant_ghs_codes for code in codes))
    
    # Split DataFrame into relevant and irrelevant GHS codes
    relevant_ghs_df = df_inventory[relevant_mask].drop(columns=["Extracted GHS"]).reset_index(drop=True)
    other_ghs_df = df_inventory[~relevant_mask].drop(columns=["Extracted GHS"]).reset_index(drop=True)

    # Save filtered DataFrames if requested
    if print_intermediate_steps and source_folder:
        relevant_ghs_df.to_excel(os.path.join(source_folder, "Relevant_GHS_Codes.xlsx"), index=False)
        other_ghs_df.to_excel(os.path.join(source_folder, "Irrelevant_GHS_Codes.xlsx"), index=False)
        print("GHS code filtering results saved.")

    print("....................GHS Filtering Complete")
    
    return relevant_ghs_df, other_ghs_df