#!/usr/bin/env bash
set -e

VERSION="1.0.0"
PKG="vibepad_${VERSION}"
BUILD="build_deb/${PKG}"

rm -rf build_deb
mkdir -p "$BUILD/DEBIAN" "$BUILD/usr/bin" "$BUILD/usr/share/applications" "$BUILD/usr/share/doc/vibepad"

cp vibepad.py "$BUILD/usr/bin/vibepad"
chmod 755 "$BUILD/usr/bin/vibepad"
cp README.md "$BUILD/usr/share/doc/vibepad/"

cat > "$BUILD/DEBIAN/control" << EOF
Package: vibepad
Version: ${VERSION}
Section: editors
Priority: optional
Architecture: all
Depends: python3, python3-tk
Maintainer: Your Name <you@example.com>
Description: Simple text editor
 VibePad is a lightweight text editor built with Python and Tkinter.
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
