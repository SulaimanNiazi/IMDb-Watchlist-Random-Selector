import PyInstaller.__main__

PyInstaller.__main__.run([
    "src/main.py",
    "--onefile",
    "--windowed",
    "--icon=src/icon.ico",
    "--add-data","src/icon.ico;.",
    "--clean",
])