import pandas as pd
import os

def load_watchlist(file_path):
    if not file_path.endswith('.csv'):
        raise ValueError("File must be a CSV.")
    try:
        return pd.read_csv(file_path)
    except Exception:
        try:
            return pd.read_csv(os.path.join('src', file_path))
        except Exception:
            raise FileNotFoundError("File not found or is not accessable.")

def find_matches(table, title):
    matches = table[table['Title'].str.contains(title, case=False, na=False)]
    if matches.empty:
        return None
    else:
        return matches[['Title', 'Title Type', 'Year', 'Genres']]

def main():
    table = load_watchlist("watchlist.csv")
    matches = find_matches(table, "simpsons")
    print(matches)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()