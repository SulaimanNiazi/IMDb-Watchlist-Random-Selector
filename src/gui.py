import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import pandas as pd
from main import load_watchlist, find_matches

class MovieSelectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Watchlist Movie Selector")
        self.columns = ("Title", "Title Type", "Year", "Genres")
        self.table = None

        # Make the grid expand with window
        for i in range(4):
            self.root.columnconfigure(i, weight=1)
        for i in range(5):
            self.root.rowconfigure(i, weight=1)
        self.root.minsize(700, 400)

        self.load_watchlist()

        # Search section
        ttk.Label(root, text="Search Title:").grid(row=1, column=0, padx=10, sticky="ew")
        self.search_entry = ttk.Entry(root)
        self.search_entry.grid(row=1, column=1, padx=10, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_movie()) 
        self.search_btn = ttk.Button(root, text="Search", command=self.search_movie)
        self.search_btn.grid(row=1, column=2, padx=10, sticky="ew")

        # Random selection section
        ttk.Label(root, text="Genre:").grid(row=2, column=0, padx=10, sticky="ew")
        self.genre_entry = ttk.Entry(root)
        self.genre_entry.grid(row=2, column=1, padx=10, sticky="ew")
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
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_table(c, False))
            self.tree.column(col, anchor = "w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        style = ttk.Style()
        treeview_font = style.lookup("Treeview", "font")
        if not treeview_font:
            treeview_font = "TkDefaultFont"
        self.font = tkfont.nametofont(treeview_font)

    def load_watchlist(self):
        try:
            self.table = load_watchlist()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load watchlist: {e}")
            self.table = None

    def sort_table(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_table(col, not reverse))

    def update_table(self, table):
        for row in self.tree.get_children():
            self.tree.delete(row)

        table = pd.DataFrame(table) if table is not None else None

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
            messagebox.showinfo("No entries", "No entry found.")

    def search_movie(self):
        if self.table is None:
            messagebox.showwarning("Warning", "Please load the watchlist first.")
            return
        title = self.search_entry.get()
        if not title:
            messagebox.showinfo("Info", "Enter a title to search.")
            return
        
        matches = find_matches(self.table, title)
        self.update_table(matches)

    def select_random(self):
        return

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieSelectorGUI(root)
    root.mainloop()