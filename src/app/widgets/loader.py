import tkinter as tk
from tkinter import ttk

class Loader:
    def __init__(self, parent):
        self.parent = parent
        self.progress = None

    def show(self, is_pack = False):
        if self.progress is None:
            self.progress = ttk.Progressbar(self.parent, mode="indeterminate")
            # place it at the bottom row, spanning all columns
            if is_pack:
                self.progress.pack(fill="x", pady=5)
            else:
                self.progress.grid(row=99, column=0, columnspan=3, sticky="ew", pady=5)
            self.progress.start()

    def hide(self):
        if self.progress:
            self.progress.stop()
            self.progress.destroy()
            self.progress = None
