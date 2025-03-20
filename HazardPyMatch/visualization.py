# visualization.py

import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_ghs_code_distribution(df_inventory, source_folder=None):
    """Generates a bar chart of GHS Code frequencies in the chemical inventory."""
    
    print("....................Generating GHS Code Distribution Plot")

    if "GHS Codes" not in df_inventory.columns:
        raise KeyError("The DataFrame must contain a 'GHS Codes' column.")

    # Flatten the GHS Codes into a list
    all_ghs_codes = df_inventory["GHS Codes"].dropna().str.split(" --- ").explode()

    # Count occurrences of each GHS code
    ghs_code_counts = all_ghs_codes.value_counts()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    ghs_code_counts.plot(kind="bar")
    plt.xlabel("GHS Hazard Code")
    plt.ylabel("Frequency")
    plt.title("GHS Hazard Code Distribution in Chemical Inventory")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save or display the plot
    if source_folder:
        output_path = os.path.join(source_folder, "GHS_Code_Distribution.png")
        plt.savefig(output_path, bbox_inches="tight")
        print(f"GHS Code Distribution Plot saved to: {output_path}")
    else:
        plt.show()

    print("....................Visualization Complete")


def plot_hazardous_protocols(df_hazards, source_folder=None):
    """Generates a bar chart of the number of hazardous protocols per protocol type."""
    
    print("....................Generating Hazardous Protocols Plot")

    if "Protocol" not in df_hazards.columns:
        raise KeyError("The DataFrame must contain a 'Protocol' column.")

    # Count the number of hazardous protocols per protocol type
    protocol_counts = df_hazards["Protocol"].value_counts()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    protocol_counts.plot(kind="bar", color="red")
    plt.xlabel("Protocol Type")
    plt.ylabel("Number of Hazardous Instances")
    plt.title("Hazardous Protocols Frequency")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save or display the plot
    if source_folder:
        output_path = os.path.join(source_folder, "Hazardous_Protocols.png")
        plt.savefig(output_path, bbox_inches="tight")
        print(f"Hazardous Protocols Plot saved to: {output_path}")
    else:
        plt.show()

    print("....................Visualization Complete")


def plot_cas_occurrences(df_inventory, source_folder=None):
    """Generates a histogram showing occurrences of unique CAS Numbers."""
    
    print("....................Generating CAS Number Occurrences Plot")

    if "CAS Number" not in df_inventory.columns:
        raise KeyError("The DataFrame must contain a 'CAS Number' column.")

    # Count occurrences of each CAS number
    cas_counts = df_inventory["CAS Number"].value_counts()

    # Create a histogram
    plt.figure(figsize=(10, 6))
    cas_counts.plot(kind="bar", color="blue")
    plt.xlabel("CAS Number")
    plt.ylabel("Occurrences")
    plt.title("CAS Number Occurrences in Inventory")
    plt.xticks(rotation=90)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save or display the plot
    if source_folder:
        output_path = os.path.join(source_folder, "CAS_Number_Occurrences.png")
        plt.savefig(output_path, bbox_inches="tight")
        print(f"CAS Number Occurrences Plot saved to: {output_path}")
    else:
        plt.show()

    print("....................Visualization Complete")

