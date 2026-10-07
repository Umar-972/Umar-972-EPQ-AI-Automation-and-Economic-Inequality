import pandas as pd

def process_data(file_path):
    # 1. Load the CSV directly into a DataFrame
    df = pd.read_csv(file_path, encoding='utf-8')
    
    df.iloc[:, 1] = df.iloc[:, 1].astype(str).str.strip()
    
    # 3. Get unique names (this replaces your 'AI' list logic)
    unique_ai_names = df.iloc[:, 1].unique().tolist()
    
    print("Unique AI Names:", unique_ai_names)
    return df

if __name__ == "__main__":
    csv_path = 'Genarated Stuff/Results.csv'
    
    # Run the function and print the DataFrame
    df = process_data(csv_path)
    print("\nFull DataFrame:")
    print(df)
