import pandas as pd
import threading
from pandastable import Table, TableModel

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from src.services import data_loader
from src.ui.widgets import Loader


class ImportTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.df_cache = None
        self.main = None  # link to MainWindow
        self.loader = Loader(self.frame)

        self.build_ui()

        self.empty_df = pd.DataFrame()  # placeholder empty dataframe
        self.table = Table(self.import_frame, dataframe=self.empty_df,
                        showtoolbar=False, showstatusbar=False)
        self.table.show()

    def set_main(self, main_window):
        self.main = main_window

    def build_ui(self):
        frm = self.frame
        frm.rowconfigure(2, weight=1)
        frm.columnconfigure(0, weight=1)

        # Local file
        ttk.Label(frm, text="Local File:").grid(row=0, column=0, sticky="w")
        self.csv_entry = ttk.Entry(frm, width=50)
        self.csv_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)

        # URL input
        ttk.Label(frm, text="URL:").grid(row=1, column=0, sticky="w")
        self.url_entry = ttk.Entry(frm, width=50)
        self.url_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Load", command=self.load_url).grid(row=1, column=2, padx=5)

        # Preview area
        self.import_frame = ttk.Frame(frm)
        self.import_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")

        ttk.Button(frm, text="Import to DB", command=self.import_to_db).grid(row=3, column=0, columnspan=3, pady=5)


    def load_url(self):
        url = self.url_entry.get().strip()
        if not url:
            return

        self.loader.show()  # show loader

        def task():
            try:
                df = data_loader.load_from_url(url)
                self.df_cache = df
                self.frame.after(0, lambda: self.show_table(df))
            except Exception as e:
                self.frame.after(0, lambda: messagebox.showerror("Load Error", str(e)))
            finally:
                self.frame.after(0, self.loader.hide)  # hide loader

        threading.Thread(target=task, daemon=True).start()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV/JSON files", "*.csv *.json")])
        if not path:
            return
        self.csv_entry.delete(0, tk.END)
        self.csv_entry.insert(0, path)
        try:
            df = data_loader.load_from_file(path)
            self.df_cache = df
            self.show_table(df)
        except Exception as e:
            messagebox.showerror("File Error", str(e))

    def import_to_db(self):
        if not self.main.conn:
            messagebox.showerror("No Database", "Please connect to a database first in the Database tab.")
            return
        if self.df_cache is None:
            messagebox.showerror("No Data", "Please load some data first.")
            return

        # Ask user: insert or new table
        choice = messagebox.askquestion(
            "Import Option",
            "Do you want to insert into an existing table?\n(Choose 'No' to create a new table)"
        )

        if choice == "yes":  # Insert into existing
            try:
                cur = self.main.conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cur.fetchall()]
                if not tables:
                    messagebox.showerror("No Tables", "No existing tables found. Please create a new one.")
                    return
                table_name = simpledialog.askstring("Table Name", f"Available tables:\n{tables}\n\nEnter table to insert into:")
                if table_name not in tables:
                    messagebox.showerror("Invalid", "Selected table does not exist.")
                    return
                self.df_cache.to_sql(table_name, self.main.conn, if_exists="append", index=False)
                messagebox.showinfo("Success", f"Data inserted into {table_name}")
            except Exception as e:
                messagebox.showerror("Insert Error", str(e))

        else:  # Create new table
            table_name = simpledialog.askstring("New Table", "Enter name for new table:")
            if not table_name:
                return

            # Preview schema (could be replaced with GPT later)
            schema_preview = "\n".join([f"{col}: {dtype}" for col, dtype in self.df_cache.dtypes.items()])
            confirm = messagebox.askyesno("Schema Preview",
                                          f"Detected schema:\n\n{schema_preview}\n\nProceed with this schema?")
            if not confirm:
                return

            try:
                self.df_cache.to_sql(table_name, self.main.conn, if_exists="replace", index=False)
                messagebox.showinfo("Success", f"New table {table_name} created and data imported.")
            except Exception as e:
                messagebox.showerror("Create Error", str(e))

    def show_table(self, df):
        if self.table is not None:
            # update existing table instead of recreating
            self.table.updateModel(TableModel(df))
            self.table.redraw()
        else:
            # fallback if somehow not initialized
            self.table = Table(self.import_frame, dataframe=df,
                            showtoolbar=False, showstatusbar=False)
            self.table.show()

