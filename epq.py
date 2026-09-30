#-------------------------
# Import libs
#-------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#-------------------------
# Create vars & open file
#-------------------------

pie_val             : list = []

consent             : str  = "Yes, I agree"    # The exact answer that counts as giving consent
consent_given       : int  = 0                 # Counts people who agreed
no_consent          : int  = 0                 # Counts people who did not agree
kept_rows           : list = []                # Will hold only the rows of people who agreed

employment_status   : list = ["Full-time employee", "Part-time employee", "Self-employed"]
unemployment_status : str  = "Unemployed"
student             : str  = "Student"
retired             : str  = "Retired"

#-------------------------
# Subprograms
#-------------------------

# Reads the whole csv file into a table (DataFrame) so it can be analysed
def to_df(path, consent):

    # keep_default_na=False stops pandas turning the text "N/A" into a missing value
    df = pd.read_csv(path, encoding="utf-8", keep_default_na=False)

    # Makes a True/False list (True if they consent)
    agreed = df["Do you agree to participate?"] == consent

    # Counts how many people did and didn't give consent
    consent_given = int(agreed.sum())
    no_consent    = int((~agreed).sum())

    # Keep rows of people who consent
    df = df[agreed]
    
    # Remove columns that are not needed
    df = df.drop(columns=["Submission ID", "Respondent ID", "Submitted at"])

    
    return df, consent_given, no_consent

# Creates two different DFs (1 for employed, 1 for unemployed)
def employed_unemployed(df):

    # Seperate emplyed & unemployed datasets
    employed      = df["What is your current employment status?"].isin(employment_status)
    unemployed    = df["What is your current employment status?"] == unemployment_status
    students      = df["What is your current employment status?"] == student
    retireds      = df["What is your current employment status?"] == retired

    # Turn datasets into proper DataFrames
    df_employed   = df[employed]
    df_unemployed = df[unemployed]
    df_students   = df[students]
    df_retireds   = df[retireds]

    pie_val = [len(df_employed), len(df_unemployed), len(df_students), len(df_retireds)]

    return df_employed, df_unemployed, df_students, df_retireds, pie_val

#-------------------------
# Main Program
#-------------------------

if __name__ == "__main__":
    file = "test_data.csv" # Declare the file with data

    df, consent_given, no_consent                                 = to_df(file, consent) # Turns file into DataFrame
    df_employed, df_unemployed, df_students, df_retireds, pie_val = employed_unemployed(df) # Turn main DataFrame into seperate ones for (un)employed

    #print(consent_given)
    employed_percent   = (len(df_employed) / consent_given) * 100
    unemployed_percent = (len(df_unemployed) / consent_given) * 100
    #print(len(df_employed))

    #print(f"{employed_percent:.2f}%")
    #print(f"{unemployed_percent:.2f}%")
    plt.pie(pie_val, labels=["Employed", "Unemployed", "Students", "Retirerds"], autopct="%1.1f%%")
    plt.title("Employment status of respondents")
    plt.show()

    #print(f"DF shape: {df.shape}")
    #print(f"Employed shape: {df_employed.shape}")
    #print(f"Unemployed shape: {df_unemployed.shape}")

    #print(f"Consent : {consent_given}")
    #print(f"Not Consented: {no_consent}")






# Note:
#   Because the EPQ is to be presented to a "non-specialist audience" I have decided to leave plenty of comments
#   explaining the process behind the program and how it operates for others to understand whilst marking or viewing
#   the code.