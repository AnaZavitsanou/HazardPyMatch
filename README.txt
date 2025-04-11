Check out our preprint! https://www.biorxiv.org/content/10.1101/2025.03.14.643365v1                   ![Logo](HazardPyMatch_logo_simple.png)
## ReadMe
This is a Chemical Inventory and Hazard Analysis Pipeline. You can easily run this code in Google Colab. See HazardPyMatch/notebooks for the .ipynb file and colabREADME. 

For general use, see below. 

This script prompts the user for Globally Harmonized System (GHS) H-codes. At least 1 H-code is required. See here for reference: https://pubchem.ncbi.nlm.nih.gov/ghs 

There are 2 inputs. The first is a required Chemical Inventory or list stored as an .xlsx or .csv file. This file should have "Chemical_Inventory" in the file name and contain 2 required column names: "Chemical
Name" and "CAS Number". The second is an optional folder of laboratory protocols. These should be PDF files as HazardPyMatch relies on the pdfplumber python dependency. We suggest naming your files Name of assay_Source.pdf i.e. Western blot (WB)_BioRad.pdf 

This code prompts the user for source folder and protocol folder paths, GHS hazard classifications H-codes and an answer to whether to print intermediate steps of the chemical inventory dataframe for debugging (y/n). 

The inventory file is automatically loaded from your specified source folder, with missing CAS numbers populated using the PubChem API. HazardPyMatch then retrieves and filters based on GHS H-codes, retrieves and filters based on chemical name synonyms, and searches for protocol PDFs that mention the chemicals in the updated list. 

The final outputs include filtered chemical inventory lists, matched protocol hazards, and visual analytics, all saved as Excel files or PNGs in "source_folder".
