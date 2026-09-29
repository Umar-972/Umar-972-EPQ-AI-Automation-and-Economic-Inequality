#-------------------------
# Import libs
#-------------------------

import pandas as pd
import numpy as np

#-------------------------
# Create vars & open file
#-------------------------

consent             : str  = "Yes, I agree"    # The exact answer that counts as giving consent
consent_given       : int  = 0                 # Counts people who agreed
no_consent          : int  = 0                 # Counts people who did not agree
kept_rows           : list = []                # Will hold only the rows of people who agreed

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

    # Only keeps the rows of people who gave consent
    df = df[agreed]

    # Removes columns that are not needed for the analysis
    df = df.drop(columns=["Submission ID", "Respondent ID", "Submitted at"])

    return df, consent_given, no_consent
  
#-------------------------
# Main Program
#-------------------------

if __name__ == "__main__":
    file = "test_data.csv"
    df, consent_given, no_consent = to_df(file, consent)
    print(f"Consent : {consent_given}")
    print(f"Not Consented: {no_consent}")
    print(df.shape) # Prints (rows, columns) of the table that is left






# Note:
#   Because the EPQ is to be presented to a "non-specialist audience" I have decided to leave lots of comments
#   explaining the process behind the program and how it operates for others to understand whilst marking or viewing
#   the code.