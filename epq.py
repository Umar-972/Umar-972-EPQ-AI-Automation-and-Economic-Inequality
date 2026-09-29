#-------------------------
# Import libs
#-------------------------

import csv
import pandas as pd
import numpy as np

#-------------------------
# Create vars & opem file
#-------------------------

# file doesn't exist yet
with open('data.csv', 'r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)

#-------------------------
# Subprograms
#-------------------------

def to_df(file):
  df = pd.DataFrame(file)
  
#-------------------------
# Main Program
#-------------------------

if __name__ == "__main__":
  to_df(file)
