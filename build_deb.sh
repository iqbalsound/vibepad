#!/usr/bin/env bash
set -e

VERSION=$(grep -m1 '^VERSION' vibepad.py | cut -d'"' -f2)
PKG="vibepad_${VERSION}"
BUILD="build_deb/${PKG}"

rm -rf build_deb
mkdir -p "$BUILD/DEBIAN" "$BUILD/usr/bin" "$BUILD/usr/share/applications" "$BUILD/usr/share/doc/vibepad"

cp vibepad.py "$BUILD/usr/bin/vibepad"
chmod 755 "$BUILD/usr/bin/vibepad"
cp README.md "$BUILD/usr/share/doc/vibepad/"
cp LICENSE "$BUILD/usr/share/doc/vibepad/copyright"

cat > "$BUILD/DEBIAN/control" << EOF
Package: vibepad
Version: ${VERSION}
Section: editors
Priority: optional
Architecture: all
Depends: python3, python3-tk
Maintainer: Iqbal Uddin Khan <your.email@example.com>
Homepage: https://github.com/iqbalsound/vibepad
Description: Simple text editor with themes
 VibePad is a lightweight text editor built with Python and Tkinter.
 Version 2 adds Light, Dark and Green-on-Black themes.
EOF

cat > "$BUILD/usr/share/applications/vibepad.desktop" << EOF
[Desktop Entry]
Name=VibePad
Comment=Simple text editor
Exec=vibepad
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;TextEditor;
EOF

dpkg-deb --build --root-owner-group "$BUILD" "${PKG}_all.deb"
echo "Built ${PKG}_all.deb"
