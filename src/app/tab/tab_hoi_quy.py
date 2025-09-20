import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from tkinter import StringVar, DoubleVar, IntVar, messagebox
from tkinter.ttk import Frame, LabelFrame, Label, Button, Combobox, Entry

class TabHoiQuy:
    def __init__(self, notebook):
        self.frame = Frame(notebook)

        # Data & model
        self.main = None
        self.df = None
        self.model = None
        self.X_cols = []
        self.Y_col = None

        # UI state
        self.selected_table = StringVar()
        self.selected_y = StringVar()
        self.result_var = StringVar(value="Chưa huấn luyện mô hình")

        # Build UI
        self.build_ui()

    def build_ui(self):
        # --- Khung chọn dữ liệu ---
        khung_chon = LabelFrame(self.frame, text="Chọn dữ liệu")
        khung_chon.pack(side="top", fill="x", padx=5, pady=5)

        Label(khung_chon, text="Chọn bảng:").grid(row=0, column=0, sticky="w")
        self.combo_table = Combobox(khung_chon, textvariable=self.selected_table, state="readonly")
        self.combo_table.grid(row=0, column=1, padx=5)
        self.combo_table.bind("<<ComboboxSelected>>", self.tai_du_lieu_bang)

        Label(khung_chon, text="Chọn cột Y:").grid(row=1, column=0, sticky="w")
        self.combo_y = Combobox(khung_chon, textvariable=self.selected_y, state="readonly")
        self.combo_y.grid(row=1, column=1, padx=5)
        self.combo_y.bind("<<ComboboxSelected>>", self.cap_nhat_cot_x)

        # Nút tải bảng
        Button(khung_chon, text="Làm mới danh sách bảng", command=self.cap_nhat_bang).grid(row=0, column=2, padx=5)

        # --- Khung chọn X ---
        self.khung_x = LabelFrame(self.frame, text="Chọn các cột X")
        self.khung_x.pack(side="top", fill="x", padx=5, pady=5)

        # --- Khung huấn luyện ---
        khung_huanluyen = LabelFrame(self.frame, text="Huấn luyện mô hình")
        khung_huanluyen.pack(side="top", fill="x", padx=5, pady=5)

        Button(khung_huanluyen, text="Huấn luyện mô hình", command=self.huan_luyen_mo_hinh).pack(side="left", padx=5)
        Label(khung_huanluyen, textvariable=self.result_var).pack(side="left", padx=5)

        # --- Khung dự đoán ---
        self.khung_du_doan = LabelFrame(self.frame, text="Dự đoán")
        self.khung_du_doan.pack(side="top", fill="x", padx=5, pady=5)

        self.predict_inputs = {}  # lưu entry/combobox cho từng X
        Button(self.khung_du_doan, text="Dự đoán", command=self.du_doan).pack(side="bottom", pady=5)

    def set_main(self, main_window):
        self.main = main_window


    def cap_nhat_cot_x(self, event=None):
        """Cập nhật danh sách cột X, bỏ qua cột Y đã chọn"""
        if self.df is None:
            return

        # Xóa khung chọn X cũ
        for widget in self.khung_x.winfo_children():
            widget.destroy()

        self.X_vars = {}
        row = 0
        for col in self.df.columns:
            if col == self.selected_y.get():
                continue  # bỏ qua cột Y
            Label(self.khung_x, text=col).grid(row=row, column=0, sticky="w")
            var = StringVar(value="Bỏ qua")
            combo = Combobox(self.khung_x, textvariable=var,
                            values=["Bỏ qua", "Liên tục", "Rời rạc"], state="readonly")
            combo.grid(row=row, column=1, padx=5)
            self.X_vars[col] = var
            row += 1

    def cap_nhat_bang(self):
        """Lấy danh sách bảng từ DB"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';"
        tables = pd.read_sql_query(query, self.main.ketnoi).name.tolist()
        self.combo_table["values"] = tables

    def tai_du_lieu_bang(self, event=None):
        table_name = self.selected_table.get()
        query = f"SELECT * FROM {table_name};"
        self.df = pd.read_sql_query(query, self.main.ketnoi)

        # Cập nhật combobox Y
        self.combo_y["values"] = list(self.df.columns)

        # Mặc định chọn Y = cột đầu tiên (nếu có)
        if len(self.df.columns) > 0:
            self.selected_y.set(self.df.columns[0])

        # Vẽ lại danh sách X (loại cột Y)
        self.cap_nhat_cot_x()


    def huan_luyen_mo_hinh(self):
        """Huấn luyện Linear Regression"""
        if self.df is None:
            messagebox.showwarning("Lỗi", "Chưa chọn bảng dữ liệu")
            return

        self.X_cols = [col for col, var in self.X_vars.items() if var.get() != "Bỏ qua"]
        self.Y_col = self.selected_y.get()

        if not self.X_cols or not self.Y_col:
            messagebox.showwarning("Lỗi", "Chưa chọn đủ cột X và Y")
            return

        X = pd.get_dummies(self.df[self.X_cols], drop_first=True)
        y = self.df[self.Y_col]

        self.model = LinearRegression()
        self.model.fit(X, y)
        y_pred = self.model.predict(X)

        r2 = r2_score(y, y_pred)
        rmse = mean_squared_error(y, y_pred)

        self.result_var.set(f"R²={r2:.3f}, RMSE={rmse:.3f}")

        # Cập nhật giao diện dự đoán
        for widget in self.khung_du_doan.winfo_children():
            widget.destroy()   # xoá sạch toàn bộ con trong khung_du_doan

        self.predict_inputs.clear()

        Label(self.khung_du_doan, text="Nhập giá trị cho các X:").pack(anchor="w", pady=5)

        for col in self.X_cols:
            frame_col = Frame(self.khung_du_doan)
            frame_col.pack(fill="x", pady=2)

            Label(frame_col, text=col).pack(side="left", padx=5)

            if self.X_vars[col].get() == "Rời rạc":
                values = self.df[col].dropna().unique().tolist()
                var = StringVar(value=values[0] if values else "")
                combo = Combobox(frame_col, textvariable=var, values=values, state="readonly")
                combo.pack(side="left", padx=5)
                self.predict_inputs[col] = var
            else:
                var = StringVar(value="0")
                entry = Entry(frame_col, textvariable=var)
                entry.pack(side="left", padx=5)
                self.predict_inputs[col] = var

        Button(self.khung_du_doan, text="Dự đoán", command=self.du_doan).pack(pady=5)

    def du_doan(self):
        """Dự đoán Y từ input người dùng"""
        if self.model is None:
            messagebox.showwarning("Lỗi", "Chưa huấn luyện mô hình")
            return

        input_data = {}
        for col, var in self.predict_inputs.items():
            value = var.get()
            if value == "":
                messagebox.showwarning("Lỗi", f"Chưa nhập giá trị cho {col}")
                return

            # Nếu là số thì convert về float
            try:
                if self.X_vars[col].get() == "Liên tục":
                    value = float(value)
            except ValueError:
                messagebox.showwarning("Lỗi", f"Giá trị nhập cho {col} phải là số")
                return

            input_data[col] = value

        # Tạo DataFrame 1 dòng
        df_input = pd.DataFrame([input_data])

        # One-hot encode (giống train)
        X = pd.get_dummies(df_input, drop_first=True)

        # Bổ sung cột còn thiếu so với training
        for col in self.model.feature_names_in_:
            if col not in X.columns:
                X[col] = 0

        X = X[self.model.feature_names_in_]

        y_pred = self.model.predict(X)[0]
        messagebox.showinfo("Kết quả dự đoán", f"Giá trị dự đoán cho Y = {y_pred:.3f}")

