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
```
cd ~/projects/vibepad
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install pyinstaller
```

    Your prompt will show (.venv). That means you’re inside the isolated environment.

### Step 2: Build
    pyinstaller --onefile --windowed --name vibepad vibepad.py
-  --onefile bundles everything into one file
-  --windowed means no terminal window opens with the app
-  --name vibepad sets the output name

### Step 3: Test
`./dist/vibepad`

### Step 4: Install it system-wide (optional)
`sudo cp dist/vibepad /usr/local/bin/vibepad`
`vibepad            # now runs from anywhere`

### Step 5: Git hygiene
    Don’t commit dist/ or build/ (our .gitignore already excludes them). Also add the venv:
`echo ".venv/" >> .gitignore`
`deactivate         # leave the virtual environment`

__Note: The binary is built for the system you build on. A binary built on a newer Ubuntu may not run on an older one, so build on the oldest system you want to support.__

### Option B: Build a .DEB Package
    A .deb is just a folder with a specific layout, packed with dpkg-deb. We’ll install the Python script and let apt pull in python3 and python3-tk automatically.

## Step 1: Prepare the script
    Edit vibepad.py and make sure the first line is:

`#!/usr/bin/env python3`

### Step 2: Create the package folder structure
```
cd ~/projects/vibepad
mkdir -p packaging/vibepad_1.0.0/DEBIAN
mkdir -p packaging/vibepad_1.0.0/usr/bin
mkdir -p packaging/vibepad_1.0.0/usr/share/applications
mkdir -p packaging/vibepad_1.0.0/usr/share/doc/vibepad
```

**The folders under vibepad_1.0.0/ mirror where files land on the target system (usr/bin becomes /usr/bin).**

### Step 3: Copy the files into place
```
cp vibepad.py packaging/vibepad_1.0.0/usr/bin/vibepad
chmod 755 packaging/vibepad_1.0.0/usr/bin/vibepad
cp README.md packaging/vibepad_1.0.0/usr/share/doc/vibepad/

```

_We drop the .py extension so users just type vibepad._

### Step 4: Create the control file
    This describes your package:

```
cat > packaging/vibepad_1.0.0/DEBIAN/control << 'EOF'
Package: vibepad
Version: 1.0.0
Section: editors
Priority: optional
Architecture: all
Depends: python3, python3-tk
Maintainer: Your Name <you@example.com>
Description: Simple text editor
 VibePad is a lightweight text editor built with Python and Tkinter.
 It supports open, save, undo/redo, find and word count.
EOF
```
**Important rules:**

-  Architecture: all means it’s pure Python and works on any CPU
-  The description’s extra lines must start with one space
-  Keep a blank line out of the file’s end issues by ensuring it ends with a newline (the heredoc does this)

### Step 5: Create the menu launcher
```
cat > packaging/vibepad_1.0.0/usr/share/applications/vibepad.desktop << 'EOF'
[Desktop Entry]
Name=VibePad
Comment=Simple text editor
Exec=vibepad
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;TextEditor;
EOF
```

### Step 6: Build the .deb
`dpkg-deb --build --root-owner-group packaging/vibepad_1.0.0`

    This creates packaging/vibepad_1.0.0.deb. Move it to a cleaner name:

`mv packaging/vibepad_1.0.0.deb vibepad_1.0.0_all.deb`

### Step 7: Inspect it
```
dpkg-deb --info vibepad_1.0.0_all.deb       # shows the control info
dpkg-deb --contents vibepad_1.0.0_all.deb   # lists the files
```

### Step 8: Install and test
`sudo apt install ./vibepad_1.0.0_all.deb`

    Using apt install ./file.deb (with the ./) automatically installs the dependencies, which is better than dpkg -i.

    Then run vibepad in a terminal, or search for VibePad in the Kubuntu application launcher.

### Step 9: Uninstall (to test cleanup)
`sudo apt remove vibepad`

### Step 10: Check for packaging mistakes (optional)
```
sudo apt install lintian
lintian vibepad_1.0.0_all.deb
```

**You’ll see some warnings (like missing changelog or copyright). Those only matter if you publish to official repositories.**