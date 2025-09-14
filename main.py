import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from src.ui.main_window import MainWindow

def main():
    # root = tk.Tk()
    root = ThemedTk(theme="radiance")
    # style = ttk.Style(root)
    # style.theme_use("vista")

    root.title("DB Manager")
    root.geometry("900x700")
    MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
