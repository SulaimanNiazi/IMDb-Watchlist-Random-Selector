import pandas as pd
import os

def get_csv_files(path, files = []):
    if os.path.isdir(path):
        for subPath in os.listdir(path):
            if not subPath.startswith('.'):
                newFiles = get_csv_files(os.path.join(path, subPath), files)
                if newFiles is not None and newFiles != files: 
                    files.extend(newFiles)
    elif path.endswith('.csv'):
        abspath = os.path.abspath(path)
        if abspath not in files:
            files.append(abspath)
    return files

def load_watchlist(file_path='.'):
    paths = get_csv_files(file_path)
    if paths:
        return pd.read_csv(paths[0])
    raise FileNotFoundError("File not found or is not accessable.")

def find_matches(table, title):
    matches = table[table['Title'].str.contains(title, case=False, na=False)]
    if matches.empty:
        return None
    else:
        return matches[['Title', 'Title Type', 'Year', 'Genres']].astype({'Year': 'int'}).to_string(index=False)

def get_random_selection(table, genre = None, series = False):
    if series:
        table = table[table['Title Type'].str.contains('Series', case=True, na=False)]
    else:
        table = table[~table['Title Type'].str.contains('Series', case=True, na=False)]

    matches = table[table['Genres'].str.contains(genre, case=False, na=False)] if genre else table
    if matches.empty:
        return None
    selection = matches.sample(n=1).iloc[0]
    return f"{selection['Title']} ({int(selection['Year'])}) - {selection['Genres']} - ({selection['Title Type']})"

def main():
    print("Loading watchlist...")
    table = load_watchlist()
    print("Watchlist loaded.\n\nFinding matches...")
    matches = find_matches(table, "simpsons")
    print("Matches found:")
    print(matches)
    print("\nGetting random selection...")
    movie = get_random_selection(table, "comedy", series=False)
    print("Random selection:", movie)

if __name__ == "__main__":
    print("Loading...")
    os.system('cls' if os.name == 'nt' else 'clear')
    main()