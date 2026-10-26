#!/usr/bin/env python3
"""VibePad - a simple text editor built with Tkinter."""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog


class VibePad(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x550")
        self.current_file = None          # path of the open file (None = unsaved)

        self.build_text_area()
        self.build_menu()
        self.build_status_bar()
        self.bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self.exit_app)  # handle window close (X)
        self.update_title()

    # ---------- UI building ----------
    def build_text_area(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        self.text = tk.Text(frame, wrap="word", undo=True,
                            font=("DejaVu Sans Mono", 12), padx=8, pady=8)
        scroll = tk.Scrollbar(frame, command=self.text.yview)
        self.text.config(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.focus_set()

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

        self.config(menu=menubar)

    def build_status_bar(self):
        self.status = tk.Label(self, text="Words: 0 | Characters: 0",
                               anchor="e", relief="sunken")
        self.status.pack(side="bottom", fill="x")
        self.text.bind("<<Modified>>", self.on_modified)

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_as())   # Ctrl+Shift+S
        self.bind("<Control-q>", lambda e: self.exit_app())
        self.bind("<Control-f>", lambda e: self.find_text())
        self.bind("<Control-y>", lambda e: self.text.edit_redo())

    # ---------- Helpers ----------
    def on_modified(self, event=None):
        """Runs every time the text changes."""
        if self.text.edit_modified():
            content = self.text.get("1.0", "end-1c")
            words = len(content.split())
            self.status.config(text=f"Words: {words} | Characters: {len(content)}")
            self.text.edit_modified(False)   # reset so it can fire again
            self.mark_dirty(True)

    def update_title(self):
        name = self.current_file if self.current_file else "Untitled"
        star = "*" if self.is_dirty else ""
        self.title(f"{star}{name} - VibePad")

    # "dirty" = has unsaved changes
    is_dirty = False

    def mark_dirty(self, value):
        self.is_dirty = value
        self.update_title()

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

    # ---------- File actions ----------
    def new_file(self):
        if self.confirm_discard():
            self.text.delete("1.0", tk.END)
            self.current_file = None
            self.mark_dirty(False)

    def open_file(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError) as err:
                messagebox.showerror("Error", f"Could not open file:\n{err}")
                return
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
            self.text.edit_reset()           # clear undo history
            self.current_file = path
            self.mark_dirty(False)

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
        return "break"

    def find_text(self):
        term = simpledialog.askstring("Find", "Search for:")
        self.text.tag_remove("found", "1.0", tk.END)
        if not term:
            return
        start = "1.0"
        count = 0
        while True:
            start = self.text.search(term, start, stopindex=tk.END, nocase=True)
            if not start:
                break
            end = f"{start}+{len(term)}c"
            self.text.tag_add("found", start, end)
            start = end
            count += 1
        self.text.tag_config("found", background="yellow", foreground="black")
        if count == 0:
            messagebox.showinfo("Find", "No matches found.")


if __name__ == "__main__":
    VibePad().mainloop()
