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

from questionary import question

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
    print("     a. You may choose not to export the file and only view them in the CLI by selecting 'n' to the export question.")
    print("_________________________________________________________________")
    enter_loan_qualifier = questionary.confirm("Are you willing to meet the above criteria to complete the Loan Qualifier App?").ask()
    if enter_loan_qualifier == True:
        csvpath = questionary.path("Enter a file path to a rate-sheet (.csv):").ask()
        csvpath = Path(csvpath)
        if not csvpath.exists():
            sys.exit(f"Oops! Can't find this path: {csvpath}")
        return load_csv(csvpath)
    else:
        sys.exit("Try again when you are ready.")


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """

    credit_score = questionary.text("What's your credit score?").ask()
    credit_score = int(credit_score)
    if credit_score < 850 and credit_score > 300:
        debt = questionary.text("What's your current amount of monthly debt?").ask()
        income = questionary.text("What's your total monthly income?").ask()
        loan_amount = questionary.text("What's your desired loan amount?").ask()
        home_value = questionary.text("What's your home value?").ask()
    else:
        credit_score = questionary.text("Credit Scores range from 300 to 850. Please enter a valid credit score.").ask()
        credit_score = int(credit_score)
        if credit_score <= 850 and credit_score >= 300:
            debt = questionary.text("What's your current amount of monthly debt?").ask()
            income = questionary.text("What's your total monthly income?").ask()
            loan_amount = questionary.text("What's your desired loan amount?").ask()
            home_value = questionary.text("What's your home value?").ask()
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
        save_as_csv = questionary.confirm("Would you like to save a copy as a .csv?").ask()
        # Since the .confirm() returns a boolean number the if statement should take a True / False value
        if save_as_csv == True:
            save_csv(qualifying_loans)
            sys.exit("The file has been saved!")
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
