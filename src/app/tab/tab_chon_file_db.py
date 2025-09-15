import sqlite3
from threading import Thread

from tkinter.ttk import Entry, Button, Frame, Label
from tkinter import filedialog, messagebox
from pandastable import Table, TableModel
import pandas as pd

from src.app.widgets.loader import Loader


class TabChonFileDB:
    def __init__(self, notebook):
        self.frame = Frame(notebook)
        self.main = None
        self.loader = Loader(self.frame)
        self.build_ui()

    def build_ui(self):
        self.frame.rowconfigure(2, weight=1)
        self.frame.columnconfigure(1, weight=1)  # cột 1 (Entry) sẽ giãn

        # Label
        Label(self.frame, text="File DB: ").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Entry (giãn ngang, căn trái)
        self.chon_file_DB_entry = Entry(self.frame, width=70)
        self.chon_file_DB_entry.grid(row=0, column=1, sticky="ew", padx=(0,5), pady=5)

        # Buttons
        Button(self.frame, text="Chọn...", command=self.chon_file_DB).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        Button(self.frame, text="Kết nối", command=self.ket_noi_DB).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Khung bảng
        khung_bang = Frame(self.frame)
        khung_bang.grid(row=2, column=0, columnspan=4, sticky="nsew")
        self.bang = Table(khung_bang, dataframe=pd.DataFrame())
        self.bang.show()

    def ket_noi_DB(self):
        duong_dan = self.chon_file_DB_entry.get()
        
        if not duong_dan:
            messagebox.showerror("Lỗi", "Bạn chưa nhập đường dẫn.")
            
        self.loader.show()
        def task():
            try:
                if duong_dan.endswith(".db"):
                    try:
                        self.main.ketnoi = sqlite3.connect(duong_dan, check_same_thread=False)
                        self.main.tab_ve_bieu_do.cap_nhat_bang()
                        query = "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';"
                        df = pd.read_sql_query(query, self.main.ketnoi)
                        self.hien_thi_bang(df)
                    except:
                        self.frame.after(0, messagebox.showerror("Lỗi", "File đã chọn không tồn tại"))
                else:
                    self.frame.after(0, messagebox.showerror("Lỗi", "Vui lòng chọn file .db"))
            except Exception as e:
                self.frame.after(0, messagebox.showerror("Lỗi", "Tải dữ liệu thất bại"))
                
            self.frame.after(0, self.loader.hide)
        
        Thread(target=task, daemon=True).start()
        
    def hien_thi_bang(self, df):
        self.bang.updateModel(TableModel(df))
        self.bang.redraw()
        
    def chon_file_DB(self):
        duong_dan = filedialog.askopenfilename()
        
        self.chon_file_DB_entry.delete(0, 'end')
        self.chon_file_DB_entry.insert(0, duong_dan)
        

    def run(self):
        self.frame.mainloop()

    def set_main(self, main_window):
        self.main = main_window

if __name__ == "__main__":
    app = TabChonFileDB()
    app.run()