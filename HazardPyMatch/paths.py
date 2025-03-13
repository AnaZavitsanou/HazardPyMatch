# paths.py

import os

def prompt_user_paths():
    print("Your Chemical_Inventory .xlsx or .csv file is stored in your source_folder.")
    print("Your protocol .pdf files are stored in a folder for protocols within source_folder.")

    print("Please define the source_folder and protocols_folder paths for your project.")
    source_folder = input("Enter the path to your source folder: ").strip()
    protocols_folder = input("Enter the path to your protocols folder: ").strip()
    return source_folder, protocols_folder

