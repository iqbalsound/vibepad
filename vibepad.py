#!/usr/bin/env python3
"""VibePad 2.0 - a simple text editor with Light, Dark and Green-on-Black themes."""

import json
import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

VERSION = "2.1.0"

# ---- About box info: edit these to your own details ----
APP_NAME = "VibePad"
APP_DESCRIPTION = "A simple, fast text editor with Light, Dark\nand Green-on-Black themes."
AUTHOR_NAME = "Iqbal Uddin Khan"
AUTHOR_TITLE = "Assistant Professor | DIT -HU -- NN Site KHI"        # <- edit
AUTHOR_EMAIL = "iqbalsound@yahoo.com"         # <- edit
GITHUB_URL = "https://github.com/iqbalsound/vibepad"   # <- check repo name
COPYRIGHT = "© 2026 Iqbal Uddin Khan. Released under the MIT License."

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "vibepad")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Each theme is just a set of colors.
THEMES = {
    "Light": {
        "bg": "#ffffff", "fg": "#1e1e1e", "cursor": "#000000",
        "select_bg": "#b3d4fc", "select_fg": "#000000",
        "bar_bg": "#f0f0f0", "bar_fg": "#1e1e1e",
        "find_bg": "#ffeb3b", "find_fg": "#000000",
    },
    "Dark": {
        "bg": "#1e1e1e", "fg": "#d4d4d4", "cursor": "#ffffff",
        "select_bg": "#264f78", "select_fg": "#ffffff",
        "bar_bg": "#2d2d2d", "bar_fg": "#d4d4d4",
        "find_bg": "#7a6a00", "find_fg": "#ffffff",
    },
    "Green on Black": {
        "bg": "#000000", "fg": "#00ff41", "cursor": "#00ff41",
        "select_bg": "#006b1b", "select_fg": "#ffffff",
        "bar_bg": "#0a0a0a", "bar_fg": "#00ff41",
        "find_bg": "#00ff41", "find_fg": "#000000",
    },
}
DEFAULT_THEME = "Dark"


class VibePad(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x550")
        self.current_file = None      # path of the open file (None = unsaved)
        self.is_dirty = False         # True when there are unsaved changes
        self.menus = []               # every menu, so themes can recolor them

        saved = self.load_settings().get("theme", DEFAULT_THEME)
        if saved not in THEMES:
            saved = DEFAULT_THEME
        self.theme_var = tk.StringVar(value=saved)

        self.build_status_bar()       # packed first so it never gets squeezed out
        self.build_text_area()
        self.build_menu()
        self.bind_shortcuts()
        self.apply_theme(save=False)

        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.update_title()
        self.update_status()

    # ---------- Settings ----------
    def load_settings(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def save_settings(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"theme": self.theme_var.get()}, f)
        except OSError:
            pass   # settings are optional; never crash because of them

    # ---------- UI building ----------
    def build_status_bar(self):
        self.status = tk.Label(self, text="", anchor="e", relief="sunken")
        self.status.pack(side="bottom", fill="x")

    def build_text_area(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        self.text = tk.Text(frame, wrap="word", undo=True,
                            font=("DejaVu Sans Mono", 12), padx=8, pady=8,
                            borderwidth=0, highlightthickness=0)
        self.scroll = tk.Scrollbar(frame, command=self.text.yview)
        self.text.config(yscrollcommand=self.scroll.set)

        self.scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.focus_set()
        self.text.bind("<<Modified>>", self.on_modified)

    def build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z",
                              command=lambda: self.text.edit_undo())
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y",
                              command=lambda: self.text.edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X",
                              command=lambda: self.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C",
                              command=lambda: self.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V",
                              command=lambda: self.text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", accelerator="Ctrl+F", command=self.find_text)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        for name in THEMES:
            view_menu.add_radiobutton(label=name, variable=self.theme_var,
                                      value=name, command=self.apply_theme)
        view_menu.add_separator()
        view_menu.add_command(label="Next Theme", accelerator="Ctrl+T",
                              command=self.cycle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About VibePad", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)
        self.menus = [menubar, file_menu, edit_menu, view_menu, help_menu]

    def bind_shortcuts(self):
        # Bound on the text widget and "break" is returned, so Tk's built-in
        # Emacs-style keys (Ctrl+O, Ctrl+A, Ctrl+Y, Ctrl+T...) don't also fire.
        keys = {
            "<Control-n>": self.new_file,
            "<Control-o>": self.open_file,
            "<Control-s>": self.save_file,
            "<Control-S>": self.save_as,          # Ctrl+Shift+S
            "<Control-q>": self.exit_app,
            "<Control-f>": self.find_text,
            "<Control-a>": self.select_all,
            "<Control-y>": lambda: self.text.edit_redo(),
            "<Control-t>": self.cycle_theme,
        }
        for sequence, action in keys.items():
            self.text.bind(sequence, lambda e, f=action: self.run_shortcut(f))

    def run_shortcut(self, action):
        action()
        return "break"

    # ---------- Themes ----------
    def apply_theme(self, save=True):
        t = THEMES[self.theme_var.get()]

        self.text.config(bg=t["bg"], fg=t["fg"], insertbackground=t["cursor"],
                         selectbackground=t["select_bg"],
                         selectforeground=t["select_fg"],
                         inactiveselectbackground=t["select_bg"])
        self.text.tag_config("found", background=t["find_bg"], foreground=t["find_fg"])

        self.config(bg=t["bar_bg"])
        self.status.config(bg=t["bar_bg"], fg=t["bar_fg"])
        self.scroll.config(bg=t["bar_bg"], troughcolor=t["bg"],
                           activebackground=t["select_bg"])

        for menu in self.menus:
            menu.config(bg=t["bar_bg"], fg=t["bar_fg"],
                        activebackground=t["select_bg"],
                        activeforeground=t["select_fg"],
                        selectcolor=t["bar_fg"])
        if save:
            self.save_settings()

    def cycle_theme(self):
        names = list(THEMES)
        current = names.index(self.theme_var.get())
        self.theme_var.set(names[(current + 1) % len(names)])
        self.apply_theme()

    # ---------- Status / title ----------
    def update_status(self):
        content = self.text.get("1.0", "end-1c")
        self.status.config(text=f"Words: {len(content.split())} | Characters: {len(content)}")

    def update_title(self):
        name = self.current_file if self.current_file else "Untitled"
        star = "*" if self.is_dirty else ""
        self.title(f"{star}{name} - VibePad")

    def mark_dirty(self, value):
        self.is_dirty = value
        self.update_title()

    def on_modified(self, event=None):
        """Runs every time the text changes."""
        if self.text.edit_modified():
            self.update_status()
            self.text.edit_modified(False)   # reset so it can fire again
            self.mark_dirty(True)

    def show_about(self):
        """A custom About window that follows the current theme."""
        t = THEMES[self.theme_var.get()]
        win = tk.Toplevel(self)
        win.title(f"About {APP_NAME}")
        win.configure(bg=t["bar_bg"], padx=28, pady=22)
        win.resizable(False, False)
        win.transient(self)                     # stays on top of the main window

        def add_label(text, size=10, bold=False):
            tk.Label(win, text=text, bg=t["bar_bg"], fg=t["bar_fg"],
                     font=("DejaVu Sans", size, "bold" if bold else "normal"),
                     justify="center").pack(pady=2)

        add_label(APP_NAME, 22, bold=True)
        add_label(f"Version {VERSION}", 11)
        add_label(APP_DESCRIPTION, 10)

        tk.Frame(win, height=1, bg=t["fg"]).pack(fill="x", pady=12)   # divider line

        add_label("Developed by", 9)
        add_label(AUTHOR_NAME, 14, bold=True)
        add_label(AUTHOR_TITLE, 10)
        add_label(AUTHOR_EMAIL, 10)

        # Clickable link
        link = tk.Label(win, text=GITHUB_URL, bg=t["bar_bg"], fg=t["fg"],
                        cursor="hand2", font=("DejaVu Sans", 10, "underline"))
        link.pack(pady=4)
        link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

        add_label(COPYRIGHT, 9)

        tk.Button(win, text="Close", command=win.destroy,
                  bg=t["bg"], fg=t["fg"], activebackground=t["select_bg"],
                  activeforeground=t["select_fg"], relief="flat",
                  padx=20, pady=4).pack(pady=(14, 0))

        # Center the window over the main VibePad window
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        win.grab_set()                          # focus stays in About until closed

    # ---------- File actions ----------
    def confirm_discard(self):
        """Ask to save if there are unsaved changes. Returns False if user cancels."""
        if not self.is_dirty:
            return True
        answer = messagebox.askyesnocancel("Unsaved changes",
                                           "Do you want to save your changes?")
        if answer is None:        # Cancel
            return False
        if answer:                # Yes -> save first
            return self.save_file()
        return True               # No -> discard

    def new_file(self):
        if self.confirm_discard():
            self.text.delete("1.0", tk.END)
            self.text.edit_reset()
            self.text.edit_modified(False)
            self.current_file = None
            self.mark_dirty(False)
            self.update_status()

    def open_file(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as err:
            messagebox.showerror("Error", f"Could not open file:\n{err}")
            return
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.edit_reset()               # clear undo history
        self.text.edit_modified(False)
        self.current_file = path
        self.mark_dirty(False)
        self.update_status()

    def save_file(self):
        if self.current_file is None:
            return self.save_as()
        return self.write_to(self.current_file)

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            return self.write_to(path)
        return False

    def write_to(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
        except OSError as err:
            messagebox.showerror("Error", f"Could not save file:\n{err}")
            return False
        self.current_file = path
        self.mark_dirty(False)
        return True

    def exit_app(self):
        if self.confirm_discard():
            self.destroy()

    # ---------- Edit actions ----------
    def select_all(self):
        self.text.tag_add("sel", "1.0", "end")

    def find_text(self):
        term = simpledialog.askstring("Find", "Search for:", parent=self)
        self.text.tag_remove("found", "1.0", tk.END)
        if not term:
            return
        start, count = "1.0", 0
        while True:
            start = self.text.search(term, start, stopindex=tk.END, nocase=True)
            if not start:
                break
            end = f"{start}+{len(term)}c"
            self.text.tag_add("found", start, end)
            start = end
            count += 1
        if count == 0:
            messagebox.showinfo("Find", "No matches found.")


if __name__ == "__main__":
    VibePad().mainloop()
