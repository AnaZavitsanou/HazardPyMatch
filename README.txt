
## ReadMe
This is a Chemical Inventory and Hazard Analysis Pipeline. This script prompts the user for Globally Harmonized System (GHS) H-codes; 
see here for reference: https://pubchem.ncbi.nlm.nih.gov/ghs 

There are 2 inputs. The first is a required Chemical Inventory or list stored as an .xlsx or .csv file. This file should have "Chemical_Inventory" in the file name and contain 2 required column names: "Chemical
Name" and "CAS Number". The second is an optional folder of laboratory protocols. These should be PDF files as HazardPyMatch relies on the pdfplumber python dependency. We suggest naming your files Name of assay_Source.pdf i.e. Western blot (WB)_BioRad.pdf. 

You can easily run this code in Google Colab. See HazardPyMatch/notebooks for the .ipynb file and colabREADME. 

This code prompts the user for source folder and protocol folder paths, GHS codes and the answer to whether you want to print intermediate steps of the chemical inventory dataframe for debugging (y/n). 

The inventory file is automatically loaded from your specified source folder, with missing CAS numbers populated using the PubChem API. HazardPyMatch then retrieves GHS hazard classifications (H-codes), chemical name synonyms, and searches for protocol PDFs that mention the chemicals in the updated list. 

The final outputs include processed chemical inventory lists, matched protocol hazards, and visual analytics, all saved as Excel files and PNG charts in "source_folder".
