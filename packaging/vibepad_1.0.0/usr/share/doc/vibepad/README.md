# VibePad

A simple text editor for Linux (Ubuntu/Kubuntu) built with Python and Tkinter.

## Features
- New, Open, Save, Save As
- Undo/Redo, Cut/Copy/Paste, Find
- Word and character count
- Keyboard shortcuts

## Run
    sudo apt install python3 python3-tk
    python3 vibepad.py

## Option A: Standalone Executable (PyInstaller)
### Step 1: Install PyInstaller
    On recent Ubuntu/Kubuntu, pip install system-wide is blocked, so use a virtual environment:
- cd ~/projects/vibepad
- sudo apt install python3-venv
- python3 -m venv .venv
- source .venv/bin/activate
- pip install pyinstaller

    Your prompt will show (.venv). That means you’re inside the isolated environment.

### Step 2: Build
    pyinstaller --onefile --windowed --name vibepad vibepad.py
-  --onefile bundles everything into one file
-  --windowed means no terminal window opens with the app
-  --name vibepad sets the output name

### Step 3: Test
-  ./dist/vibepad

### Step 4: Install it system-wide (optional)
- sudo cp dist/vibepad /usr/local/bin/vibepad
- vibepad            # now runs from anywhere

### Step 5: Git hygiene
    Don’t commit dist/ or build/ (our .gitignore already excludes them). Also add the venv:
- echo ".venv/" >> .gitignore
- deactivate         # leave the virtual environment

__Note: The binary is built for the system you build on. A binary built on a newer Ubuntu may not run on an older one, so build on the oldest system you want to support.__
