from tkinter import Tk
from tkinter.ttk import Entry, Button, Frame, Label
from pandastable import Table, TableModel
import pandas as pd


class TabChonFileDB:
    def __init__(self, notebook):
        self.root = Frame(notebook)
        self.main = None
        self.build_ui()

    def build_ui(self):
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(1, weight=1)  # cột 1 (Entry) sẽ giãn

        # Label
        Label(self.root, text="File DB: ").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Entry (giãn ngang, căn trái)
        self.chon_file_DB_entry = Entry(self.root, width=70)
        self.chon_file_DB_entry.grid(row=0, column=1, sticky="ew", padx=(0,5), pady=5)

        # Buttons
        Button(self.root, text="Chọn...", command=self.chon_file_DB).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        Button(self.root, text="Kết nối", command=self.ket_noi_DB).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Khung bảng
        khung_bang = Frame(self.root)
        khung_bang.grid(row=2, column=0, columnspan=4, sticky="nsew")
        self.bang = Table(khung_bang, dataframe=pd.DataFrame())
        self.bang.show()

    def ket_noi_DB(self):
        print("ket noi DB thanh cong ")
    def chon_file_DB(self):
        print("Dang chon file db")

    def run(self):
        self.root.mainloop()

    def set_main(self, main_window):
        self.main = main_window

if __name__ == "__main__":
    app = TabChonFileDB()
    app.run()