from tkinter.ttk import Notebook

from src.app.tab import TabChonFileDB, TabTaiDuLieu

class HoangAnh:
    def __init__(self, root):
        self.root = root

        self.notebook = Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_chon_file_db = TabChonFileDB(self.notebook)
        self.tab_tai_du_lieu = TabTaiDuLieu(self.notebook)

        self.notebook.add(self.tab_chon_file_db.root, text="Chọn DB")
        self.notebook.add(self.tab_tai_du_lieu.root, text="Tải Dữ Liệu")

        self.tab_chon_file_db.set_main(self)
        self.tab_tai_du_lieu.set_main(self)