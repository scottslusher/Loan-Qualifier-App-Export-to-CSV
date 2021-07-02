# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
import sys
import fire
import csv
import questionary
from pathlib import Path



from qualifier.utils.fileio import (
    load_csv,
    save_csv,
)

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """
    # I have added simple instructions to help set the expectations in order to successfully complete the application
    print("")
    print("")
    print("___________________________Loan Qualifier___________________________")
    print("")
    print("You are about to begin the Loan Qualifier App. There are 3 basic steps to complete the process:")
    print("")
    print("1. Provide a file path to import the data:")
    print("")
    print("     a. Begin typing the file folder name you would like to save your file in and 'tab' to autocomplete.")
    print("     b. Start typing the name of the data file you are importing, and if the file exists in that folder you will be able to 'tab' to autocomplete.")
    print("     c. Press ENTER twice to continue.")
    print("")
    print("2. Provide valid information to the loan qualification questions.")
    print("")
    print("3. Exporting available qualifying loans:")
    print("")
    print("     a. Confirm (Y) to Export qualifying loans into a .csv file to be further analyzed")
    print("         i. You must provide a valid folder path by beginning to type the name of the folder and 'tab' to autocomplete.")
    print("         ii. Provide a name you would like the file to be saved as.")
    print("         iii. DON'T FORGET THE .CSV!!!!!")
    print("")
    print("     b. You may choose not to export the file and only view them in the CLI by selecting 'n' to the export question.")
    print("_________________________________________________________________")
    ## This is to insure the user has read all instructions before entering the application
    enter_loan_qualifier = questionary.confirm("Are you willing to meet the above criteria to complete the Loan Qualifier App?").ask()
    if enter_loan_qualifier == True:
        # I decided to go with the questionary.path to make it a little more user friendly with the autocomplete 
        csvpath = questionary.path("Enter a file path to a rate-sheet (.csv):").ask()
        csvpath = Path(csvpath)
        # This if statement is to check that the file path provided actually exists and there weren't any typos
        if not csvpath.exists():
            sys.exit(f"Oops! Can't find this path: {csvpath}")
        return load_csv(csvpath)
    # This is a system exit if the user isn't ready to enter the application after reading the instructions    
    else:
        sys.exit("Try again when you are ready.")


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """
    # Gathering the first bit of information that has to be within a certain range
    credit_score = questionary.text("What's your credit score?").ask()
    credit_score = int(credit_score)
    # Checking to make sure the credit score is a valid score that ranges between 350 and 800
    if credit_score < 850 and credit_score > 300:
        debt = questionary.text("What's your current amount of monthly debt?").ask()
        income = questionary.text("What's your total monthly income?").ask()
        loan_amount = questionary.text("What's your desired loan amount?").ask()
        home_value = questionary.text("What's your home value?").ask()
    # If the initial entry is not a valid credit score the user will receive a second prompt with further explaination.    
    else:
        credit_score = questionary.text("Credit Scores range from 300 to 850. Please enter a valid credit score.").ask()
        credit_score = int(credit_score)
        if credit_score <= 850 and credit_score >= 300:
            # Apologies for the repetition of the code from above, but I could not find a way to save the questions as a function in a data_questions.py file in the utils folder and still have it return the data so it can be used in the next chain of the code
            debt = questionary.text("What's your current amount of monthly debt?").ask()
            income = questionary.text("What's your total monthly income?").ask()
            loan_amount = questionary.text("What's your desired loan amount?").ask()
            home_value = questionary.text("What's your home value?").ask()
        # If after the second chance of entering a valid credit score the user is unsuccessful the system will exit and the user will have to start over.    
        else:
            sys.exit("That is not a valid Credit Score. Please try again later.")
   

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    print(f"Found {len(bank_data_filtered)} qualifying loans")
    
    return bank_data_filtered


def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    # @TODO: Complete the usability dialog for savings the CSV Files.
    ## The first line of defense. If there are 0 qualifying loans then give message and exit.
    if len(qualifying_loans) == 0:
        sys.exit("There are no qualifying loans based on the data provided. Have a nice day.")
    ## If there are qualifying loans then start the process of saving the loan as csv
    else:
        # This is a yes/no prompt asking if the user would like to save the file
        save_as_csv = questionary.confirm("Would you like to save a copy as a .csv?").ask()
        
        # Since the .confirm() returns a boolean number the if statement should take a True / False value
        if save_as_csv == True:
            # again I used questionary.path to make inputting a file path and "name".csv a little easier on the user instead of having to remember to "../../" into parent folders
            file_path = questionary.path("Please provide file path to save csv file?").ask()
            csvpath = Path(file_path)
            # If somehow the user does not enter a valid file path the program will simply print the results in the CLI
            if file_path == False:
                print(qualifying_loans)
            # If the file_path is valid then the save_csv function will save the file to that path and print and exit
            else:
                save_csv(qualifying_loans, csvpath)
                print(f"Saving file to file path {file_path}...")
                sys.exit("The file has been saved!")
        # If the user does not want to save the file to a .csv then they will have a second option to view the loans in the CLI        
        else:
            view_loans = questionary.confirm("Would you like to view the qualifying loans?").ask()
            if view_loans == True:
                sys.exit(qualifying_loans)
            else:
                sys.exit("Have a great day!")


def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )
        
    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)

    




if __name__ == "__main__":
    fire.Fire(run)
