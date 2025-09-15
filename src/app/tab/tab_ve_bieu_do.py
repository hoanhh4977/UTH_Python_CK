import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression 

from tkinter import BooleanVar, filedialog, messagebox
from tkinter.ttk import Button, Checkbutton, Label, Entry, Frame, LabelFrame, Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TabVeBieuDo:
    def __init__(self, notebook):
        self.frame = Frame(notebook)
        self.main = None
        self.canvas = None
        self.df = None  # dữ liệu hiện tại
        self.fig = None
        self.ax = None

        self.build_ui()
    
    def build_ui(self):
        # --- Layout ---
        self.khung_tuy_chon = LabelFrame(self.frame, text="Tùy chọn vẽ")
        self.khung_tuy_chon.pack(side="left", fill="y", padx=10, pady=10)

        self.khung_bieu_do = Frame(self.frame)
        self.khung_bieu_do.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- Controls ---
        Label(self.khung_tuy_chon, text="Chọn nguồn dữ liệu:").pack(anchor="w", pady=2)
        self.hop_nguon = Combobox(
            self.khung_tuy_chon,
            values=["CSDL hiện tại", "Dữ liệu import", "Kết quả query"],
            state="readonly",
        )
        self.hop_nguon.current(0)
        self.hop_nguon.bind("<<ComboboxSelected>>", lambda e: self.cap_nhat_bang())
        self.hop_nguon.pack(fill="x", pady=5)

        Label(self.khung_tuy_chon, text="Chọn bảng (nếu có):").pack(anchor="w", pady=2)
        self.hop_bang = Combobox(self.khung_tuy_chon, state="readonly")
        self.hop_bang.bind("<<ComboboxSelected>>", lambda e: self.cap_nhat_cot_theo_bang())
        self.hop_bang.pack(fill="x", pady=5)

        Label(self.khung_tuy_chon, text="Chọn loại biểu đồ:").pack(anchor="w", pady=2)
        self.loai_bieu_do = Combobox(
            self.khung_tuy_chon,
            values=["Pie", "Bar", "Line", "Histogram"],
            state="readonly"
        )
        self.loai_bieu_do.current(0)
        self.loai_bieu_do.pack(fill="x", pady=5)

        Label(self.khung_tuy_chon, text="Chọn cột dữ liệu:").pack(anchor="w", pady=2)
        self.hop_cot = Combobox(self.khung_tuy_chon, state="readonly")
        self.hop_cot.pack(fill="x", pady=5)

        Label(self.khung_tuy_chon, text="Tiêu đề biểu đồ:").pack(anchor="w", pady=2)
        self.o_tieu_de = Entry(self.khung_tuy_chon)
        self.o_tieu_de.pack(fill="x", pady=5)

        self.hien_luoi = BooleanVar(value=True)
        Checkbutton(self.khung_tuy_chon, text="Hiển thị lưới", variable=self.hien_luoi).pack(anchor="w")

        Button(self.khung_tuy_chon, text="Vẽ biểu đồ", command=self.ve_bieu_do).pack(fill="x", pady=5)
        Button(self.khung_tuy_chon, text="Làm mới", command=self.lam_moi).pack(fill="x", pady=5)

        Button(self.khung_tuy_chon, text="Xuất hình", command=self.export_bieu_do).pack(fill="x", pady=5)

        # Ban đầu: hiển thị nhãn placeholder thay vì plot rỗng
        self.label_placeholder = Label(self.khung_bieu_do, text="Chưa có biểu đồ nào được vẽ")
        self.label_placeholder.pack(expand=True)

        # --- Thống kê ---
        Label(self.khung_tuy_chon, text="Thống kê dữ liệu:").pack(anchor="w", pady=5)
        Button(self.khung_tuy_chon, text="Xem thống kê", command=self.thong_ke).pack(fill="x", pady=2)

        # --- Hồi quy ---
        Label(self.khung_tuy_chon, text="Chọn X (độc lập):").pack(anchor="w", pady=2)
        self.hop_x = Combobox(self.khung_tuy_chon, state="readonly")
        self.hop_x.pack(fill="x", pady=2)

        Label(self.khung_tuy_chon, text="Chọn Y (phụ thuộc):").pack(anchor="w", pady=2)
        self.hop_y = Combobox(self.khung_tuy_chon, state="readonly")
        self.hop_y.pack(fill="x", pady=2)

        Button(self.khung_tuy_chon, text="Hồi quy tuyến tính", command=self.hoi_quy).pack(fill="x", pady=5)



    def set_main(self, main_window):
        self.main = main_window

    def cap_nhat_bang(self):
        """Cập nhật danh sách bảng nếu nguồn là CSDL"""
        nguon = self.hop_nguon.get()
        if not self.main:
            return

        if nguon == "CSDL hiện tại":
            # lấy danh sách bảng từ tab Database
            try:
                if self.main.ketnoi:
                    query = "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';"
                    tables = pd.read_sql_query(query, self.main.ketnoi).name.tolist()
                    self.hop_bang["values"] = tables
                    if tables:
                        self.hop_bang.current(0)
                        self.cap_nhat_cot_theo_bang()
                else:
                    messagebox.showerror("Lỗi", "Chưa kết nối CSDL.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lấy danh sách bảng: {e}")
        else:
            self.hop_bang["values"] = []
            self.hop_bang.set("")
            # nguồn khác sẽ lấy df trực tiếp (import hoặc query)
            if nguon == "Dữ liệu import":
                self.cap_nhat_cot(self.main.imported_data)
            else:
                self.cap_nhat_cot(self.main.query_data)

    def cap_nhat_cot_theo_bang(self):
        """Khi chọn bảng → cập nhật df và cột"""
        try:
            bang = self.hop_bang.get()
            if not bang:
                return
            query = f"SELECT * FROM {bang};"
            self.df = pd.read_sql_query(query, self.main.ketnoi)
            self.hop_cot["values"] = list(self.df.columns)
            self.hop_x["values"] = list(self.df.columns)
            self.hop_y["values"] = list(self.df.columns)
            if len(self.df.columns) > 0:
                self.hop_cot.current(0)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu từ bảng: {e}")

    def cap_nhat_cot(self, df):
        self.df = df
        if df is None or df.empty:
            self.hop_cot["values"] = []
            self.hop_x["values"] = []
            self.hop_y["values"] = []
            return
        cols = list(df.columns)
        self.hop_cot["values"] = cols
        self.hop_x["values"] = cols
        self.hop_y["values"] = cols
        self.hop_cot.current(0)

    def thong_ke(self):
        if self.df is None or self.df.empty:
            messagebox.showerror("Lỗi", "Chưa có dữ liệu để thống kê")
            return
        try:
            cot = self.hop_cot.get()
            if not cot:
                messagebox.showerror("Lỗi", "Vui lòng chọn cột dữ liệu")
                return
            stats = self.df[cot].describe()
            msg = "\n".join([f"{k}: {v}" for k, v in stats.to_dict().items()])
            messagebox.showinfo("Thống kê mô tả", msg)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thống kê: {e}")


    def hoi_quy(self):
        if self.df is None or self.df.empty:
            messagebox.showerror("Lỗi", "Chưa có dữ liệu để hồi quy")
            return
        try:
            cot_x = self.hop_x.get()
            cot_y = self.hop_y.get()
            if not cot_x or not cot_y:
                messagebox.showerror("Lỗi", "Vui lòng chọn cả X và Y")
                return

            X = self.df[[cot_x]].dropna().values
            y = self.df[cot_y].dropna().values

            if len(X) != len(y) or len(X) < 2:
                messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ cho hồi quy")
                return

            # Fit mô hình
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)

            # Vẽ scatter + đường hồi quy
            for widget in self.khung_bieu_do.winfo_children():
                widget.destroy()

            self.fig, self.ax = plt.subplots(figsize=(5, 4))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.khung_bieu_do)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

            self.ax.scatter(X, y, label="Dữ liệu thực")
            self.ax.plot(X, y_pred, color="red", label="Đường hồi quy")

            eq = f"y = {model.coef_[0]:.3f}x + {model.intercept_:.3f}"
            self.ax.set_title(f"Hồi quy tuyến tính: {eq}")
            self.ax.legend()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thực hiện hồi quy: {e}")


    def ve_bieu_do(self):
        if self.df is None or self.df.empty:
            if self.main.ketnoi:
                self.cap_nhat_bang()
            messagebox.showerror("Lỗi", "Chưa có dữ liệu để vẽ")
            return

        cot = self.hop_cot.get()
        loai = self.loai_bieu_do.get()
        tieu_de = self.o_tieu_de.get()

        if not cot:
            messagebox.showerror("Lỗi", "Vui lòng chọn cột dữ liệu")
            return

        # xóa placeholder nếu đang hiển thị
        for widget in self.khung_bieu_do.winfo_children():
            widget.destroy()

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.khung_bieu_do)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        try:
            if loai == "Pie":
                self.df[cot].value_counts().plot.pie(ax=self.ax, autopct='%1.1f%%')
            elif loai == "Bar":
                self.df[cot].value_counts().plot.bar(ax=self.ax)
            elif loai == "Line":
                self.df[cot].plot.line(ax=self.ax)
            elif loai == "Histogram":
                self.df[cot].plot.hist(ax=self.ax, bins=10)

            self.ax.set_title(tieu_de if tieu_de else f"Biểu đồ {loai}")
            if self.hien_luoi.get():
                self.ax.grid(True)

            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể vẽ biểu đồ: {e}")

    def lam_moi(self):
        for widget in self.khung_bieu_do.winfo_children():
            widget.destroy()
        self.label_placeholder = Label(self.khung_bieu_do, text="Chưa có biểu đồ nào được vẽ")
        self.label_placeholder.pack(expand=True)


    def export_bieu_do(self):
        if self.fig is None:
            messagebox.showerror("Lỗi", "Chưa có biểu đồ nào để xuất")
            return

        try:
            duong_dan = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF File", "*.pdf"), ("All Files", "*.*")]
            )
            if duong_dan:
                self.fig.savefig(duong_dan, bbox_inches="tight")
                messagebox.showinfo("Thành công", f"Đã xuất biểu đồ ra file:\n{duong_dan}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất biểu đồ: {e}")