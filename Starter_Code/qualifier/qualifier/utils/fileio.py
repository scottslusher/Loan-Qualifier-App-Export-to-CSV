# -*- coding: utf-8 -*-
"""Helper functions to load and save CSV data.

This contains a helper function for loading and saving CSV files.

"""
from prompt_toolkit.shortcuts.prompt import CompleteStyle
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


def save_csv(qualifying_loans, csvpath):
    """Saves the qualifying loans to a CSV file. 
    
    Args:
        qualifying_loans (list of lists): The qualified bank loans.
        csvpath: A direct path to save the file into 
        
    Returns:
        A CSV file saved as whatever name the user inputs that is located in
        the folder the user inputs
    """
    # Set the output header
    header = ["Lender", "Max Loan Amount", "Max LTV", "Max DTI", "Min Credit Score", "Interest Rate"]
    
    # Opened the output CSV file path using 'with open'
    with open(csvpath, 'w', newline='') as csvfile:
        # Created a csv writer
        csvwriter = csv.writer(csvfile, delimiter=",")
        # Wrote the header to the CSV file
        csvwriter.writerow(header)
        # Took the value of each row of the list of lists and added its own row
        for row in qualifying_loans:
            csvwriter.writerow(row)
    
    