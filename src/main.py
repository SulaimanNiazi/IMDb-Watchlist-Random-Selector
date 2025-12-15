from tkinter import messagebox, filedialog, Label, Entry, Button, StringVar, BooleanVar, Checkbutton, Frame, Scrollbar, Tk
from tkinter.ttk import Treeview, Style, Combobox
import tkinter.font as tkfont
from pandas import read_csv, Series, DataFrame
import os

class MovieSelectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Watchlist Movie Selector")
        self.columns = ("Title", "Title Type", "Year", "Genres")
        self.table = None

        # Responsive grid
        for i in range(5): 
            self.root.columnconfigure(i, weight=1)
            self.root.rowconfigure(i, weight=1)
        self.root.columnconfigure(1, weight=10)
        self.root.rowconfigure(3, weight=30)
        self.root.minsize(700, 400)

        # Search section
        Label(root, text="Search Title:").grid(row=1, column=0, padx=10, sticky="ew")
        self.search_entry = Entry(root)
        self.search_entry.grid(row=1, column=1, padx=10, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_movie())
        self.search_btn = Button(root, text="Search", command=self.search_movie)
        self.search_btn.grid(row=1, column=2, columnspan=2, padx=10, sticky="ew")

        # Genre dropdown
        Label(root, text="Genre:").grid(row=2, column=0, padx=10, sticky="ew")
        self.genre_var = StringVar(value="Any")
        self.genre_combo = Combobox(root, textvariable=self.genre_var, state="readonly")
        self.genre_combo.grid(row=2, column=1, padx=10, sticky="ew")

        # Series and Movie checkboxes
        def ensure_selection(movies = True):
            if not self.series_var.get() and not self.movies_var.get(): self.series_var.set(True) if movies else self.movies_var.set(True)
        
        self.series_var = BooleanVar(value=True)
        self.series_check = Checkbutton(root, text="Series", variable=self.series_var, command=lambda:ensure_selection(False))
        self.series_check.grid(row=2, column=2, padx=10, sticky="ew")

        self.movies_var = BooleanVar(value=True)
        self.movies_check = Checkbutton(root, text="Movies", variable=self.movies_var, command=lambda:ensure_selection(True))
        self.movies_check.grid(row=2, column=3, padx=10, sticky="ew")

        # Load New Watchlist and Select Random to Watch buttons
        self.random_btn = Button(root, text="Load New Watchlist", command=lambda:self.load_watchlist(auto=False))
        self.random_btn.grid(row=1, column=4, padx=10, sticky="ew")

        self.random_btn = Button(root, text="Select Random to Watch", command=self.select_random)
        self.random_btn.grid(row=2, column=4, padx=10, sticky="ew")

        # Table output
        self.tree_frame = Frame(root)
        self.tree_frame.grid(row=3, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_scroll_y = Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree_scroll_x = Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_x.grid(row=1, column=0, sticky="ew")
        self.tree = Treeview(
            self.tree_frame, columns=self.columns, show="headings", 
            yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set
        )
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        self.count = Label(root, text="Count: 0", padx=10)
        self.count.grid(row=4, column=0, sticky="ew")

        # Font for measuring column width
        style = Style()
        treeview_font = style.lookup("Treeview", "font") or "TkDefaultFont"
        self.font = tkfont.nametofont(treeview_font)

        self.load_watchlist()

    def get_csv_files(self, path='.', files=[]):
        if os.path.isdir(path):
            for subPath in os.listdir(path):
                if not subPath.startswith('.'):
                    newFiles = self.get_csv_files(os.path.join(path, subPath), files)
                    if newFiles is not None and newFiles != files: files.extend(newFiles)
        elif path.endswith('.csv'):
            abspath = os.path.abspath(path)
            if abspath not in files: files.append(abspath)
        return files

    def load_watchlist(self, auto=True):
        try:
            paths = self.get_csv_files() if auto else [filedialog.askopenfilename(
                title="Select Watchlist CSV", filetypes=[("CSV Files", "*.csv")], initialdir="."
            )]

            if not paths: raise FileNotFoundError("No CSV file found.")
            self.table = read_csv(paths[0])
            self.search_movie()
        except Exception as e:
            self.table = None
            self.tree.delete(*self.tree.get_children())
            messagebox.showerror("Error", f"Failed to load watchlist: {e}")
            if not auto:
                messagebox.showinfo("Retrying...", "Attempting to find nearest .csv file")
                self.load_watchlist()
            return

        # Extract unique genres
        self.genres = ["Any"] + sorted(
            Series([g.strip() for sublist in self.table['Genres'].dropna().str.split(',') for g in sublist]).unique()
        )
        self.genre_combo['values'] = self.genres

    def get_filtered_table(self):
        if self.table is None: return DataFrame(columns=self.columns)
        
        all_series = self.table['Title Type'].str.contains('Series', na=False)
        series = self.series_var.get()
        table = self.table[all_series if series else ~all_series] if series != self.movies_var.get() else self.table.copy()
        
        genre = self.genre_var.get()
        if genre != "Any": table = table[table['Genres'].str.contains(genre, case=False, na=False)]
        
        table = table[list(self.columns)].astype({'Year': 'string'}).fillna('N/A')
        table['Year'] = table['Year'].str.replace('.0', '', regex=False)
        table = table.assign(
            SortKey=table['Title'].str.startswith(('[', ']', '(', ')', '{', '}')).map({True: 0, False: 1})
        ).sort_values(by=['SortKey', 'Title']).drop(columns=['SortKey'])
        return table

    def update_table(self, table):
        self.tree.delete(*self.tree.get_children())
        if table.empty:
            messagebox.showinfo("No Entries Found", "Try a different search or genre.")
        else:
            for _, row in table.iterrows(): self.tree.insert("", "end", values=tuple(row))
            # Auto-size columns
            for col in self.columns:
                max_width = self.font.measure(col)
                for item in self.tree.get_children():
                    cell_width = self.font.measure(str(self.tree.set(item, col)))
                    max_width = max(max_width, cell_width)
                final_width = max_width + 20
                self.tree.column(col, minwidth=final_width, width=final_width)
        self.count.config(text=f"Count: {len(table)}")

    def search_movie(self):
        matches = self.get_filtered_table()
        title = self.search_entry.get()
        if title: matches = matches[matches['Title'].str.contains(title, case=False, na=False)]
        self.update_table(matches)

    def select_random(self):
        filtered_table = self.get_filtered_table()
        filtered_table = filtered_table[~filtered_table['Year'].str.contains('N/A', na=False)]
        self.update_table(filtered_table if filtered_table.empty() else filtered_table.sample(n=1))

if __name__ == "__main__":
    root = Tk()
    app = MovieSelectorGUI(root)
    root.mainloop()