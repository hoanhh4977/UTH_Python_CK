from tkinter import ttk

class PlotTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.main = None

    def set_main(self, main_window):
        self.main = main_window
