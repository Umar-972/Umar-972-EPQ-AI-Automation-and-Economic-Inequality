#-------------------------
# Import libs
#-------------------------

import matplotlib.pyplot as plt
import pandas as pd

#-------------------------
# Create vars
#-------------------------

# Overall vars
employment_status   : list = ["Full-time employee", "Part-time employee", "Self-employed"]
unemployment_status : str  = "Unemployed"
student             : str  = "Student"
retired             : str  = "Retired"
consent             : str  = "Yes, I agree"    # The exact answer that counts as giving consent
consent_given       : int  = 0                 # Counts people who agreed

# vars for graphs

# vars for Fig 1  
pie_val             : list = []

#vars for Fig 2
years               : list = []
rates_anual         : list = []

#vars for Fig 3
quarters            : list = []
rates_quarterly     : list = []

#vars for Fig 4

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

def parse_unemployed_csv_anual(unemployment_data_file):
    # Anual data lines 1-55
    df_unemployment_anual       = pd.read_csv(unemployment_data_file, header=None, nrows=55)

    years       = df_unemployment_anual[0].tolist()
    rates_anual = df_unemployment_anual[1].tolist()

    # final 5 years
    final_5_yr      = df_unemployment_anual.iloc[-5:, 0].astype(int).to_list()
    final_5_rates   = df_unemployment_anual.iloc[-5:, 1].to_list()

    return df_unemployment_anual, years, rates_anual, final_5_yr, final_5_rates

def parse_unemployed_csv_quarterly(unemployment_data_file):
    # Quarterly data lines 56-275
    df_unemployment_quarterly   = pd.read_csv(unemployment_data_file, header=None, nrows=220)

    quarters        = df_unemployment_quarterly[0].to_list()
    rates_quarterly = df_unemployment_quarterly[1].to_list()

    return df_unemployment_quarterly, quarters, rates_quarterly

def parse_unemployed_csv_monthly(unemployment_data_file):
    # Monthly data lines 278-936
    df_unemployment_monthly = pd.read_csv(unemployment_data_file,header=None, nrows=219)
    return df_unemployment_monthly

#-------------------------
# Main Program
#-------------------------

if __name__ == "__main__":
    test_file                           = "C:/Users/umarn/Desktop/EPQ/Data Analysis/test_data.csv" # Declare the file with data
    unemployment_data_file_anual        = "C:/Users/umarn/Desktop/EPQ/Data Analysis/Scripts for Graphs/Data Files/Unemployment_rate_anual.csv"
    unemployment_data_file_quarterly    = "C:/Users/umarn/Desktop/EPQ/Data Analysis/Scripts for Graphs/Data Files/Unemployment_rate_quarterly.csv"
    unemployment_data_file_monthly      = "C:/Users/umarn/Desktop/EPQ/Data Analysis/Scripts for Graphs/Data Files/Unemployment_rate_monthly.csv"

    # Create All DataFrames
    df, consent_given, no_consent                                           = to_df(test_file, consent) # Turns file into DataFrame
    df_employed, df_unemployed, df_students, df_retireds, pie_val           = employed_unemployed(df) # Turn main DataFrame into seperate ones for (un)employed
    df_unemployment_anual, years, rates_anual, final_5_yr, final_5_rates    = parse_unemployed_csv_anual(unemployment_data_file_anual)
    df_unemployment_quarterly, quarters, rates_quarterly                    = parse_unemployed_csv_quarterly(unemployment_data_file_quarterly)

    # Calculates Percentages
    employed_percent   = (len(df_employed) / consent_given) * 100
    unemployed_percent = (len(df_unemployed) / consent_given) * 100

    #-------------------------
    # Show All Figures
    #-------------------------

    # Fig1.png
    # plt.figure()
    # plt.pie(pie_val, labels=["Employed", "Unemployed", "Students", "Retireds"], autopct="%1.1f%%")
    # plt.title("Employment status of respondents")
    # plt.savefig("Data Analysis/Graphs/Fig1.png", dpi=300, bbox_inches="tight")
    # plt.show()
    # plt.close()

    # Fig2a.png
    # plt.figure(figsize=(12, 6))
    # plt.plot(years, rates_anual, marker="x")
    # plt.title("Unemployment rates from 1971-2025")
    # plt.xlabel("Year")
    # plt.ylabel("Unemployment rate (%)")
    # plt.tight_layout()
    # plt.savefig("Data Analysis/Graphs/Fig2a.png", dpi=300, bbox_inches="tight")
    # plt.show()

    # Fig2b.png
    # plt.figure()
    # plt.plot(final_5_yr, final_5_rates, marker="x")
    # plt.title("Unemployment rates from 2020-2025")
    # plt.savefig("Data Analysis/Graphs/Fig2b.png", dpi=300, bbox_inches="tight")
    # plt.show()
    # plt.close()

    # Fig3.png
    # plt.figure(figsize=(12, 6))
    # plt.plot(quarters, rates_quarterly)
    # plt.title("Unemployment from 1971-2025 Quarterly")
    # plt.xlabel("Year")
    # plt.ylabel("Unemployment rate (%)")
    # plt.xticks(range(0, len(quarters), 20), quarters[::20], rotation=45) # Show label every 5 years
    # plt.tight_layout()
    # plt.savefig("Data Analysis/Graphs/Fig3.png", dpi=300, bbox_inches="tight")
    # plt.show()
    # plt.close()

    # Fig4.png