import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import pandas as pd
import os

class MovieSelectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Watchlist Movie Selector")
        self.columns = ("Title", "Title Type", "Year", "Genres")
        self.genres = ["Any"]
        self.table = None

        # Make the grid expand with window
        for i in range(4):
            self.root.columnconfigure(i, weight=1)
        for i in range(5):
            self.root.rowconfigure(i, weight=1)
        self.root.minsize(700, 400)

        # Search section
        ttk.Label(root, text="Search Title:").grid(row=1, column=0, padx=10, sticky="ew")
        self.search_entry = ttk.Entry(root)
        self.search_entry.grid(row=1, column=1, padx=10, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_movie()) 
        self.search_btn = ttk.Button(root, text="Search", command=self.search_movie)
        self.search_btn.grid(row=1, column=2, padx=10, sticky="ew")

        # Random selection section
        ttk.Label(root, text="Genre:").grid(row=2, column=0, padx=10, sticky="ew")
        self.genre_var = tk.StringVar()
        self.genre_var.set("Any") # default
        self.genre_combo = ttk.Combobox(root, textvariable=self.genre_var, values=self.genres, state="readonly")
        self.genre_combo.grid(row=2, column=1, padx=10, sticky="ew")

        self.series_var = tk.BooleanVar()
        self.series_check = ttk.Checkbutton(root, text="Series", variable=self.series_var)
        self.series_check.grid(row=2, column=2, padx=10, sticky="ew")
        self.random_btn = ttk.Button(root, text="Select Random", command=self.select_random)
        self.random_btn.grid(row=2, column=3, padx=10, sticky="ew")

        # Table output (Treeview) with scrollbars
        self.tree_frame = ttk.Frame(root)
        self.tree_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.tree_frame.rowconfigure(0, weight=100)
        self.tree_frame.columnconfigure(0, weight=100)
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_x.grid(row=1, column=0, sticky="ew")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=self.columns,
            show="headings",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor = "w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        style = ttk.Style()
        treeview_font = style.lookup("Treeview", "font")
        if not treeview_font:
            treeview_font = "TkDefaultFont"
        self.font = tkfont.nametofont(treeview_font)

        self.load_watchlist()

    def get_csv_files(self, path='.', files = []):
        if os.path.isdir(path):
            for subPath in os.listdir(path):
                if not subPath.startswith('.'):
                    newFiles = self.get_csv_files(os.path.join(path, subPath), files)
                    if newFiles is not None and newFiles != files: 
                        files.extend(newFiles)
        elif path.endswith('.csv'):
            abspath = os.path.abspath(path)
            if abspath not in files:
                files.append(abspath)
        return files

    def load_watchlist(self):
        try:
            paths = self.get_csv_files()
            if paths:
                self.table = pd.read_csv(paths[0])
            else:
                raise FileNotFoundError("File not found or is not accessible.")
            
            genre_set = set()
            for genres in self.table['Genres'].dropna().unique():
                for genre in map(str.strip, genres.split(',')):
                    if genre not in genre_set:
                        genre_set.add(genre)
            self.genres = ["Any"] + sorted(genre_set)
            self.genre_combo['values'] = self.genres
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load watchlist: {e}")
            self.table = None

    def get_filtered_table(self):
        allSeries = self.table['Title Type'].str.contains('Series', case=True, na=False)
        series = self.series_var.get()
        table = self.table[allSeries if series else ~allSeries]
        genre = self.genre_var.get()
        if genre != "Any":
            table = table[table['Genres'].str.contains(genre, case=False, na=False)]
        return table

    def update_table(self, table):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if isinstance(table, pd.Series):
            # Convert Series to DataFrame and order columns
            table = pd.DataFrame([table[self.columns[i]] for i in range(len(self.columns))]).T
        elif isinstance(table, pd.DataFrame):
            if table.empty:
                table = None

        if table is not None:
            for _, row in table.iterrows():
                self.tree.insert("", "end", values=tuple(row))

            # Adjust column widths
            for col in self.columns:
                max_width = self.font.measure(col)
                for item in self.tree.get_children():
                    cell_value = str(self.tree.set(item, col))
                    cell_width = self.font.measure(cell_value)
                    if cell_width > max_width:
                        max_width = cell_width
                width = max_width + 20
                self.tree.column(col, minwidth=width, width=width)
        else:
            messagebox.showinfo("No Entries Found", "Try a different search or genre.")

    def search_movie(self):
        if self.table is None:
            messagebox.showwarning("Warning", "Please load the watchlist first.")
            return
        title = self.search_entry.get()
        if not title:
            messagebox.showinfo("Info", "Enter a title to search.")
            return

        matches = self.get_filtered_table()
        matches = matches[matches['Title'].str.contains(title, case=False, na=False)]

        matches = matches[['Title', 'Title Type', 'Year', 'Genres']].astype({'Year': 'string'}).fillna('N/A').sort_values(by=['Title Type', 'Title'])
        matches['Year'] = matches['Year'].str.replace('.0', '', regex=False)

        self.update_table(matches)

    def select_random(self):
        if self.table is None:
            messagebox.showwarning("Warning", "Please load the watchlist first.")
            return
        filtered_table = self.get_filtered_table()
        selection = filtered_table[~filtered_table['Year'].isna()].astype({'Year': 'string'}).sample(n=1).iloc[0].fillna('N/A')
        selection['Year'] = selection['Year'][:-2]
        self.update_table(selection)

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieSelectorGUI(root)
    root.mainloop()