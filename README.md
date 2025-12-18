# Watchlist Movie Selector

**Watchlist Movie Selector** is a Python desktop application built with **Tkinter** that helps you organize, filter, and randomly select movies or TV series from an **IMDb-exported watchlist CSV file**.

It is designed for users who want a quick and convenient way to decide *what to watch next* based on genres, title type, or search terms.

---

## Features

* Import IMDb watchlists via **CSV file** using a file dialog
* Display watchlist entries in a structured table
* Filter by:

  * Movie / TV Series
  * Genre
  * Title search
* Combine multiple filters simultaneously
* Select a **random title** from the filtered list with a single button
* Clean and responsive Tkinter-based GUI
* Scrollable, sortable table view
* Displays total count of matching entries

---

## Requirements

* Python **3.9+** (recommended)
* Install all required python libraries using [requirements.txt](requirements.txt):

```bash
pip install -r requirements.txt
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SulaimanNiazi/IMDb-Watchlist-Random-Selector.git
cd watchlist-movie-selector
```

### 2. Export Your IMDb Watchlist

1. Go to **IMDb → Your Watchlist**
2. Export your watchlist as a **CSV file**
3. Save it locally (preferably in the same directory with the .exe file)

---

### 3. Run the Application

```bash
python main.py
```

---

## Usage

1. Click **Load New Watchlist**
2. Select your IMDb-exported CSV file
3. Use the filters:

   * Search by title
   * Filter by genre
   * Choose Movies and/or Series
4. Click **Search** to apply filters
5. Click **Select Random to Watch** to randomly choose from the filtered list

The selected entry will be highlighted in the table.

---

## CSV Format Compatibility

The application is designed to work with the **standard IMDb watchlist CSV export**, which includes fields such as:

* Title
* Title Type
* Year
* Genres

No manual editing of the CSV file is required.

---

## Note

It is possible your local antivirus may not trust the .exe file at first, it is normal to see it scanned and then tolerated.

If for some reason the antivirus flags the .exe file as dangerous, the code is available in [main.py](./src/main.py) and you can easily generate the exe file using [builder.py](builder.py).
