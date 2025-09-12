from tkinter import Tk, filedialog, messagebox
import pandas as pd
from tkinter.ttk import Label, Entry, Button, Frame, Treeview

from src.utils.utilities import is_valid_url

class TabTaiDuLieu:
    def __init__(self):
        self.root = Tk()
        self.root.title("App")
        self.root.geometry("900x600")
        self.build_ui()
    
    def build_ui(self):
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        # Dòng đầu tiên
        Label(self.root, text="Tải dữ liệu từ máy:").grid(row=0, column=0, sticky="w")
        self.tai_du_lieu_tu_may_entry = Entry(self.root, width=50)
        self.tai_du_lieu_tu_may_entry.grid(row=0, column=1, sticky="ew")
        Button(self.root, text="Chọn...", command=self.tai_du_lieu_tu_may).grid(row=0, column=2)
        
        # Dòng thứ hai
        Label(self.root, text="Tải dữ liệu từ URL:").grid(row=1, column=0, sticky="w")
        self.tai_du_lieu_tu_url_entry = Entry(self.root, width=50)
        self.tai_du_lieu_tu_url_entry.grid(row=1, column=1, sticky="ew")
        Button(self.root, text="Tải dữ liệu", command=self.tai_du_lieu_tu_url).grid(row=1, column=2)
        
        # Dòng thứ ba
        khung_bang = Frame(self.root)
        khung_bang.grid(row=2, column=0, columnspan=3, sticky="nsew")
        tree = Treeview(khung_bang, show="headings")
        tree.pack(fill="both", expand=True)
        
        # Dòng thứ tư
        Button(self.root,text="Nhập vào CSDL").grid(row=3,column=0)
        
    def run(self):
        self.root.mainloop()
    
    def tai_du_lieu_tu_may(self):
        duong_dan = filedialog.askopenfilename()
        self.tai_du_lieu_tu_may_entry.delete(0, 'end')
        self.tai_du_lieu_tu_may_entry.insert(0, duong_dan)
        if duong_dan.endswith((".csv", ".json")):
            if duong_dan.endswith(".csv"):
                data = pd.read_csv(duong_dan)
            else:
                data = pd.read_json(duong_dan)
            
            self.hien_thi_bang()
        else:
            print("Lỗi")
            
    def tai_du_lieu_tu_url(self):
        url = self.tai_du_lieu_tu_url_entry.get()
        if is_valid_url(url):
            try:
                if url.endswith((".csv", ".json")):
                    if url.endswith(".csv"):
                        data = pd.read_csv(url)
                    else:
                        data = pd.read_json(url)
                        
                    self.hien_thi_bang()
                else:
                    messagebox.showerror(title="Lỗi", message="Loại file không hỗ trợ.")
            except:
                messagebox.showerror(title="Lỗi", message="File không tồn tại.")
        else:
            messagebox.showerror(title="Lỗi", message="URL không hợp lệ.")
        
    def hien_thi_bang(self):
        pass
    
if __name__ == "__main__":
    app = TabTaiDuLieu()
    app.run()