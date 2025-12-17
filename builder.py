import PyInstaller.__main__, os

PyInstaller.__main__.run([
    "src/main.py",
    "--onefile",
    "--windowed",
    "--icon=src/icon.ico",
    "--add-data","src/icon.ico;.",
    "--clean",
])

os.rename("dist/main.exe", "dist/Watchlist Random Selector.exe")