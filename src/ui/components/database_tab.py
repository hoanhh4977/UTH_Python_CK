import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
from pandastable import Table, TableModel
import pandas as pd
import threading
import sqlite3

from src.ui.widgets import Loader


class DatabaseTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.main = None

        self.loader = Loader(self.frame)

        self.build_ui()

    def set_main(self, main_window):
        self.main = main_window

    def build_ui(self):
        frm = self.frame
        frm.rowconfigure(2, weight=1)
        frm.columnconfigure(0, weight=1)

        self.db_entry = ttk.Entry(frm, width=50)
        self.db_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Choose DB", command=self.browse_db).grid(row=0, column=1, padx=5)
        ttk.Button(frm, text="Connect", command=self.connect_db).grid(row=0, column=2, padx=5)

        self.db_frame = ttk.Frame(frm)
        self.db_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.table = Table(self.db_frame, dataframe=pd.DataFrame())
        self.table.show()

    def browse_db(self):
        path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
        if path:
            self.db_entry.delete(0, tk.END)
            self.db_entry.insert(0, path)

    def connect_db(self):
        path = self.db_entry.get()

        self.loader.show()

        def task():
            try:
                if path:
                    self.main.conn = sqlite3.connect(path, check_same_thread=False)
                    query = "SELECT name FROM sqlite_master WHERE type='table';"
                    df = pd.read_sql_query(query, self.main.conn)
                    self.show_table(df)
                else:
                    messagebox.showerror("Lỗi", "Vui lòng chọn file .db")
            except Exception as e:
                self.frame.after(0, lambda: messagebox.showerror("Load Error", str(e)))
            finally:
                self.frame.after(0, self.loader.hide)
        threading.Thread(target=task, daemon=True).start()

    def show_table(self, df):
        self.table.updateModel(TableModel(df))
        self.table.redraw()