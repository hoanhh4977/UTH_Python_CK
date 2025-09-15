import pandas as pd
from tkinter import messagebox
from tkinter.ttk import Notebook

from src.app.tab import TabChonFileDB, TabTaiDuLieu, TabSQL, TabVeBieuDo

class ManHinhChinh:
    def __init__(self, root):
        self.root = root
        self.ketnoi = None
        self.imported_data = None
        self.query_data = None

        self.notebook = Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_chon_file_db = TabChonFileDB(self.notebook)
        self.tab_tai_du_lieu = TabTaiDuLieu(self.notebook)
        self.tab_sql = TabSQL(self.notebook)
        self.tab_ve_bieu_do = TabVeBieuDo(self.notebook)

        self.notebook.add(self.tab_chon_file_db.frame, text="Chọn DB")
        self.notebook.add(self.tab_tai_du_lieu.frame, text="Tải Dữ Liệu")
        self.notebook.add(self.tab_sql.frame, text="SQL")
        self.notebook.add(self.tab_ve_bieu_do.frame, text="Vẽ Biểu Đồ")

        self.tab_chon_file_db.set_main(self)
        self.tab_tai_du_lieu.set_main(self)
        self.tab_sql.set_main(self)
        self.tab_ve_bieu_do.set_main(self)

        self.tab_sql.run_query_callback = self.chay_sql
        self.tab_sql.send_to_plot_callback = self.send_to_plot
        
    def chay_sql(self, query: str):
        if not self.ketnoi:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query(query, self.ketnoi)
            return df
        except Exception as e:
            messagebox.showerror("Lỗi truy vấn", str(e))
            return pd.DataFrame()
        
    def send_to_plot(self, df: pd.DataFrame):
        self.query_data = df