INPUT = "dist/main.exe"
OUTPUT = "dist/Watchlist Random Selector.exe"

import PyInstaller.__main__, os

PyInstaller.__main__.run([
    "src/main.py",
    "--onefile",
    "--windowed",
    "--icon=src/icon.ico",
    "--add-data","src/icon.ico;.",
    "--clean",
])

if os.path.exists(OUTPUT): os.remove(OUTPUT)
os.rename(INPUT, OUTPUT)