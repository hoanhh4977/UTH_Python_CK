import pandas as pd
from threading import Thread
from tkinter import Tk, filedialog, messagebox
from tkinter.ttk import Label, Entry, Button, Frame
from pandastable import Table, TableModel

from src.app.widgets import Loader
from src.utils.utilities import is_valid_url

class TabTaiDuLieu:
    def __init__(self, notebook):
        self.root = Frame(notebook)
        self.data = None
        self.loader = Loader(self.root)
        self.main = None
        self.build_ui()
    
    def build_ui(self):
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        # Dòng đầu tiên
        Label(self.root, text="Tải dữ liệu từ máy:").grid(row=0, column=0, sticky="w")
        self.tai_du_lieu_tu_may_entry = Entry(self.root, width=50)
        self.tai_du_lieu_tu_may_entry.grid(row=0, column=1, sticky="ew", padx=10)
        Button(self.root, text="Chọn...", command=self.tai_du_lieu_tu_may).grid(row=0, column=2)
        
        # Dòng thứ hai
        Label(self.root, text="Tải dữ liệu từ URL:").grid(row=1, column=0, sticky="w")
        self.tai_du_lieu_tu_url_entry = Entry(self.root, width=50)
        self.tai_du_lieu_tu_url_entry.grid(row=1, column=1, sticky="ew", padx=10)
        Button(self.root, text="Tải dữ liệu", command=self.tai_du_lieu_tu_url).grid(row=1, column=2)
        
        # Dòng thứ ba
        khung_bang = Frame(self.root)
        khung_bang.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.bang = Table(khung_bang, dataframe=pd.DataFrame())
        self.bang.show()
        # tree.pack(fill="both", expand=True)
        
        # Dòng thứ tư
        Button(self.root,text="Nhập vào CSDL").grid(row=3,column=0, columnspan=3)
        
    def run(self):
        self.root.mainloop()
    
    def tai_du_lieu_tu_may(self):
        duong_dan = filedialog.askopenfilename()
        self.tai_du_lieu_tu_may_entry.delete(0, 'end')
        self.tai_du_lieu_tu_may_entry.insert(0, duong_dan)

        self.loader.show()
        def task():
            if duong_dan.endswith((".csv", ".json")):
                if duong_dan.endswith(".csv"):
                    self.data = pd.read_csv(duong_dan)
                else:
                    self.data = pd.read_json(duong_dan)

                self.hien_thi_bang()
            else:
                self.loader.hide()
                if duong_dan != "":
                    self.root.after(0, messagebox.showerror(title="Lỗi", message="Loại file không hỗ trợ."))
            
            self.loader.hide()
        
        Thread(target=task, daemon=True).start()
            
    def tai_du_lieu_tu_url(self):
        url = self.tai_du_lieu_tu_url_entry.get()

        self.loader.show()

        def task():
            if is_valid_url(url):
                try:
                    if url.endswith((".csv", ".json")):
                        if url.endswith(".csv"):
                            self.data = pd.read_csv(url)
                        else:
                            self.data = pd.read_json(url)
                            
                        self.root.after(0, self.hien_thi_bang())
                    else:
                        self.loader.hide()
                        self.root.after(0, messagebox.showerror(title="Lỗi", message="Loại file không hỗ trợ."))
                except Exception as e:
                    print(str(e))
                    self.loader.hide()
                    self.root.after(0, messagebox.showerror(title="Lỗi", message="File không tồn tại."))
            else:
                self.loader.hide()
                self.root.after(0, lambda: messagebox.showerror(title="Lỗi", message="URL không hợp lệ."))

            self.root.after(0, self.loader.hide)
        
        Thread(target=task, daemon=True).start()
        
    def hien_thi_bang(self):
        if not self.data.empty:
            self.bang.updateModel(TableModel(self.data))
            self.bang.redraw()

    def set_main(self, main_window):
        self.main = main_window
    
if __name__ == "__main__":
    app = TabTaiDuLieu()
    app.run()