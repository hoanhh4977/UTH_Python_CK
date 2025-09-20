import pandas as pd
from tkinter import messagebox
from tkinter.ttk import Notebook

from src.app.tab import TabChonFileDB, TabTaiDuLieu, TabSQL, TabVeBieuDo

class ManHinhChinh:
    def __init__(self, root):
        
        self.root = root
        # Biến dùng để chứa kết nối với file SQL
        self.ketnoi = None
        # Biến chứa data trong tab tải dữ liệu
        self.imported_data = None
        # Biến chứa data khi truy vấn trong tab SQL
        self.query_data = None

        # Màn hình chứa các tab
        self.notebook = Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Tab chọn file DB
        self.tab_chon_file_db = TabChonFileDB(self.notebook)
        # Tab tải dữ liệu
        self.tab_tai_du_lieu = TabTaiDuLieu(self.notebook)
        # Tab SQL
        self.tab_sql = TabSQL(self.notebook)
        # Tab vẽ biểu đồ
        self.tab_ve_bieu_do = TabVeBieuDo(self.notebook)

        # Thêm nút bấm vào tab chọn file db
        self.notebook.add(self.tab_chon_file_db.frame, text="Chọn DB")
        # Thêm nút bấm vào tab tải dữ liệu
        self.notebook.add(self.tab_tai_du_lieu.frame, text="Tải Dữ Liệu")
        # Thêm nút bấm vào tab SQL
        self.notebook.add(self.tab_sql.frame, text="SQL")
        # Thêm nút bấm vào tab vẽ biểu đồ
        self.notebook.add(self.tab_ve_bieu_do.frame, text="Vẽ Biểu Đồ")

        # Truyền self vào cho thuộc tính main để các tab có thể truy cập vào 
        # thuộc tính và phương thức của màn hình chính và các tab còn lại
        self.tab_chon_file_db.set_main(self)
        self.tab_tai_du_lieu.set_main(self)
        self.tab_sql.set_main(self)
        self.tab_ve_bieu_do.set_main(self)

        # Sử dụng để câu lệnh SQL trong tab SQL
        self.tab_sql.run_query_callback = self.chay_sql
        # Sử dụng để gửi dữ liệu truy vấn vào biến query_data
        self.tab_sql.send_to_plot_callback = self.send_to_plot

    def chay_sql(self, query: str):
        # Hàm dùng để chạy câu lệnh SQL trên file db đã chọn
        if not self.ketnoi:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query(query, self.ketnoi)
            return df
        except Exception as e:
            messagebox.showerror("Lỗi truy vấn", str(e))
            return pd.DataFrame()
        
    def send_to_plot(self, df: pd.DataFrame):
        # Gán dữ liệu truy vấn vào biến query_data
        self.query_data = df