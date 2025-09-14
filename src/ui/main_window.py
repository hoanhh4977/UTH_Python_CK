import pandas as pd
from tkinter import ttk

from src.ui.components import (
    PlotTab,
    ImportTab,
    DatabaseTab,
    SQLTab
)

class MainWindow:
    def __init__(self, root):
        self.root = root

        # Notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.db_tab = DatabaseTab(self.notebook)
        self.import_tab = ImportTab(self.notebook)
        self.sql_tab = SQLTab(self.notebook)
        self.plot_tab = PlotTab(self.notebook)

        # Add to notebook
        self.notebook.add(self.db_tab.frame, text="Database")
        self.notebook.add(self.import_tab.frame, text="Import")
        self.notebook.add(self.sql_tab.frame, text="SQL")
        self.notebook.add(self.plot_tab.frame, text="Plot")

        # SQLite connection shared across tabs
        self.conn = None

        # Hook connections
        self.import_tab.set_main(self)
        self.db_tab.set_main(self)
        self.sql_tab.set_main(self)
        self.plot_tab.set_main(self)

        # 👉 Gán callback chạy query cho SQLTab
        self.sql_tab.run_query_callback = self.execute_query
        self.sql_tab.send_to_plot_callback = self.send_to_plot

    def execute_query(self, query: str):
        """Chạy SQL query và trả về DataFrame"""
        if not self.conn:
            return pd.DataFrame()
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Query Error", str(e))
            return pd.DataFrame()

    def send_to_plot(self, df: pd.DataFrame):
        # Placeholder: bạn có thể xử lý vẽ chart ở PlotTab
        print("Received data for plotting:", df.head())
