# -*- coding: utf-8 -*-
"""Helper functions to load and save CSV data.

This contains a helper function for loading and saving CSV files.

"""
import questionary
import csv
from pathlib import Path
import sys

from questionary import question

def load_csv(csvpath):
    """Reads the CSV file from path provided.

    Args:
        csvpath (Path): The csv file path.

    Returns:
        A list of lists that contains the rows of data from the CSV file.

    """
    with open(csvpath, "r") as csvfile:
        data = []
        csvreader = csv.reader(csvfile, delimiter=",")

        # Skip the CSV Header
        next(csvreader)

        # Read the CSV data
        for row in csvreader:
            data.append(row)
    return data


def save_csv(qualifying_loans):
    """Saves the qualifying loans to a CSV file. 
    
    Args:
        qualifying_loans (list of lists): The qualify bank loans.
        
    Returns:
        A CSV file saved as "qualifying_loans.csv" that is located in the same
        folder as the application that is running this code
    """
    # Set the output header
    header = ["Lender", "Max Loan Amount", "Max LTV", "Max DTI", "Min Credit Score", "Interest Rate"]
    # Created file path to save new csv as "qualifying_loans.csv"
    file_path = questionary.path("Please provide file path to save csv file?").ask()
    csvpath = Path(file_path)
    
    # Opened the output CSV file path using 'with open'
    with open(csvpath, 'w', newline='') as csvfile:
        # Created a csv writer
        csvwriter = csv.writer(csvfile, delimiter=",")
        # Wrote the header to the CSV file
        csvwriter.writerow(header)
        # Took the value of each row of the list of lists and added its own row
        for row in qualifying_loans:
            csvwriter.writerow(row)
    print(f"Saving file to file path {file_path}...")