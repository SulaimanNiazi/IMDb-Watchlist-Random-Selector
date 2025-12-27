from tkinter import messagebox, filedialog, Label, Entry, Button, StringVar, BooleanVar, Checkbutton, Frame, Scrollbar, Tk, font, Event
from tkinter.ttk import Treeview, Style, Combobox
from pandas import read_csv, Series, DataFrame
from os.path import isdir, join, abspath
from os import listdir
import sys

class MovieSelectorGUI:
    def __init__(self, root:Tk):
        root.title("Watchlist Random Selector")
        self.data = None

        resource_path = lambda relative_path: join(sys._MEIPASS if hasattr(sys, "_MEIPASS") else abspath("src"), relative_path)
        icon_path = resource_path("icon.ico")
        root.iconbitmap(icon_path)

        # Responsive grid
        for i in range(5): 
            root.columnconfigure(i, weight=1)
            root.rowconfigure(i, weight=1)
        root.columnconfigure(1, weight=10)
        root.rowconfigure(3, weight=30)
        root.minsize(700, 400)
        root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())

        # Search section
        Label(root, text="Search Title:").grid(row=1, column=0, padx=10, sticky="ew")
        self.search_entry = Entry(root)
        self.search_entry.grid(row=1, column=1, padx=10, sticky="ew")
        self.search_entry.bind("<Return>", lambda _: self.search_movie())
        Button(root, text="Search", command=self.search_movie).grid(row=1, column=2, columnspan=2, padx=10, sticky="ew")

        # Genre dropdown
        Label(root, text="Genre:").grid(row=2, column=0, padx=10, sticky="ew")
        self.genre_var = StringVar(value="Any")
        self.genres = Combobox(root, textvariable=self.genre_var, state="readonly")
        self.genres.grid(row=2, column=1, padx=10, sticky="ew")

        # Series and Movie checkboxes
        def ensure_selection(movies = True):
            if not self.series_var.get() and not self.movies_var.get(): self.series_var.set(True) if movies else self.movies_var.set(True)
        
        self.series_var = BooleanVar(value=True)
        Checkbutton(root, text="Series", variable=self.series_var, command=lambda:ensure_selection(False)).grid(row=2, column=2, padx=10, sticky="ew")
        self.movies_var = BooleanVar(value=True)
        Checkbutton(root, text="Movies", variable=self.movies_var, command=lambda:ensure_selection(True)).grid(row=2, column=3, padx=10, sticky="ew")

        # Load New Watchlist and Select Random to Watch buttons
        Button(root, text="Load New Watchlist", command=lambda:self.load_watchlist(auto=False)).grid(row=1, column=4, padx=10, sticky="ew")
        Button(root, text="Select Random to Watch", command=self.select_random).grid(row=2, column=4, padx=10, sticky="ew")

        # Table output
        tree_frame = Frame(root)
        tree_frame.grid(row=3, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.columns = ["Title", "Year", "Title Type", "Genres", "IMDb Rating", "Runtime", "URL"]
        self.sort_setting = ["Title", True]
        tree_scroll_y = Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x = Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        self.table = Treeview(tree_frame, columns=self.columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.table.yview)
        tree_scroll_x.config(command=self.table.xview)

        for col in self.columns[:-1]:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="w")
        self.table.column("URL", width=0, stretch=False)

        self.table.grid(row=0, column=0, sticky="nsew")

        def on_double_click(event:Event):
            region = self.table.identify("region", event.x, event.y)
            if region == "heading":
                heading = self.table.heading(self.table.identify_column(event.x), "text")
                if heading == self.sort_setting[0]: self.sort_setting[1] = not self.sort_setting[1]
                else: self.sort_setting = [heading, heading != "IMDb Rating"]
                self.search_movie()
                self.sort_text.config(text=f"Sorted according to {heading} in {"ascending" if self.sort_setting[1] else "descending"} order")
            
            elif region == "cell":
                url = self.table.set(self.table.identify_row(event.y))["URL"]
                root.clipboard_clear()
                root.clipboard_append(url)
                messagebox.showinfo("Copied to Clipboard", url)

        self.table.bind("<Double-1>", on_double_click)
        
        self.table.tag_configure("odd", background="#d3d3d3")
        self.table.tag_configure("even", background="#aaaaaa")

        # Bottom text
        self.count = Label(root, text="Count: 0", padx=10)
        self.count.grid(row=4, column=0, sticky="ew")

        self.sort_text = Label(root, text=f"Sorted according to Title in ascending order")
        self.sort_text.grid(row=4, column=1, sticky="w")

        # Font for measuring column width
        style = Style()
        treeview_font = style.lookup("Treeview", "font") or "TkDefaultFont"
        self.font = font.nametofont(treeview_font)
        style.configure("Treeview", rowheight=30)

        self.load_watchlist()

    def get_csv_files(self, path=".", files:list[str]=[]):
        if isdir(path):
            for subPath in listdir(path):
                if not subPath.startswith("."):
                    newFiles = self.get_csv_files(join(path, subPath), files)
                    if newFiles is not None and newFiles != files: files.extend(newFiles)
        elif path.endswith(".csv"):
            abs = abspath(path)
            if abs not in files: files.append(abs)
        return files

    def load_watchlist(self, auto=True):
        try:
            paths = self.get_csv_files() if auto else [filedialog.askopenfilename(title="Select Watchlist CSV", filetypes=[("CSV Files", "*.csv")], initialdir=".")]
            if not paths: raise FileNotFoundError("No CSV file found.")
            self.data = read_csv(paths[0])
            self.data = self.data.rename(columns={"Runtime (mins)": "Runtime"}).astype("string").fillna("N/A")
        
        except Exception as e:
            self.data = None
            self.table.delete(*self.table.get_children())
            messagebox.showerror("Error", f"Failed to load watchlist: {e}")
            if not auto:
                messagebox.showinfo("Retrying...", "Attempting to find nearest .csv file")
                self.load_watchlist()
            return
        
        def merge_titles(t:Series):
            t = list(t)
            if t[0] in t[1]: return t[1]
            elif t[1] in t[0]: return t[0]
            else: return f"{t[1]}\n{t[0]}"
        def mins_to_time(t:Series):
            t = t.values[0]
            try:
                m = int(float(t))
                t = f"{int(m/60):02d}:{m%60:02d}"
            finally: return t

        self.data["Title"] = self.data[["Title", "Original Title"]].apply(merge_titles, 1)
        self.data["Runtime"] = self.data[["Runtime"]].apply(mins_to_time, 1)
        self.data["Year"] = self.data["Year"].str.replace(".0", "")
        self.genres["values"] = ["Any"] + sorted(Series([g.strip() for sublist in self.data["Genres"].dropna().str.split(",") for g in sublist]).unique())
        
        self.search_movie()

    def get_filtered_table(self):
        if self.data is None: return DataFrame(columns=self.columns)
        table = self.data[self.columns]
        
        series = self.series_var.get()
        if series ^ self.movies_var.get():
            all_series = self.data["Title Type"].str.contains("Series", na=False)
            table = table[all_series if series else ~all_series]

        genre = self.genre_var.get()
        if genre != "Any": table = table[table["Genres"].str.contains(genre, case=False, na=False)]

        if self.sort_setting[0] in ("Genres", "Title Type"):
            genres = list(table[self.sort_setting[0]])
            SortKey = [genres.count(g) for g in genres]
        else:
            nums = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
            if   self.sort_setting[0] == "Title":       least = ("[", "]", "(", ")", "{", "}")
            elif self.sort_setting[0] == "IMDb Rating": least = "N/A"
            elif self.sort_setting[0] == "Year":        least = nums
            elif self.sort_setting[0] == "Runtime":     least = nums if self.sort_setting[1] else "N/A"
            
            else: return table.sort_values(self.sort_setting[0], ascending=self.sort_setting[1])
            
            SortKey = table[self.sort_setting[0]].str.startswith(least).map({True: 0, False: 1})
        return table.assign(SortKey=SortKey).sort_values(["SortKey", self.sort_setting[0]], ascending=self.sort_setting[1]).drop(columns=["SortKey"])

    def update_table(self, table:DataFrame):
        self.table.delete(*self.table.get_children())
        if table.empty: messagebox.showinfo("No Entries Found", "Try a different search or genre.")
        else:
            for _, row in table.iterrows(): self.table.insert("", "end", values=tuple(row))
            
            # Auto-size columns
            for col in self.columns[:-1]:
                max_width = self.font.measure(col)
                for ind, id in enumerate(self.table.get_children()):
                    text = str(self.table.set(id, col))
                    if text.__contains__('\n'):
                        texts = text.split('\n')
                        text = texts[int(len(texts[0]) < len(texts[1]))]
                    cell_width = self.font.measure(text)
                    max_width = max(max_width, cell_width)
                    self.table.item(id, tags=("odd" if ind % 2 else "even",))
                final_width = max_width + 20
                self.table.column(col, minwidth=final_width, width=final_width)

        self.count.config(text=f"Count: {len(table)}")

    def search_movie(self):
        matches = self.get_filtered_table()
        title = self.search_entry.get()
        if title: matches = matches[matches["Title"].str.contains(title, case=False, na=False)]
        self.update_table(matches)

    def select_random(self):
        filtered_table = self.get_filtered_table()
        filtered_table = filtered_table[~filtered_table["Year"].str.contains("N/A", na=False)]
        self.update_table(filtered_table if filtered_table.empty else filtered_table.sample(n=1))

if __name__ == "__main__":
    root = Tk()
    app = MovieSelectorGUI(root)
    root.mainloop()