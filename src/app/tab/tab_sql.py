
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Frame
from pandastable import Table, TableModel
import pandas as pd

class TabSQL:
    def __init__(self, notebook):
        self.frame = Frame(notebook)
        self.main = None
        self.run_query_callback = None
        self.send_to_plot_callback = None
        self.build_ui()

        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=0)
        self.frame.columnconfigure(0, weight=1)
        
    def set_main(self, main_window):
        self.main = main_window
        
    def build_ui(self):
        
        editor_frame = ttk.Frame(self.frame)
        editor_frame.pack(fill = "x", padx=5, pady=5)
        
        tk.Label(editor_frame, text="Câu lệnh SQL:").pack(anchor="w")
        self.sql_text = tk.Text(editor_frame, height=8, wrap="none")
        self.sql_text.pack(side="left", fill="x", expand=True)
        
        #Thanh cuon cho o nhap
        sql_scroll = ttk.Scrollbar(editor_frame, command=self.sql_text.yview)
        sql_scroll.pack(side="right", fill="y")
        self.sql_text.config(yscrollcommand=sql_scroll.set)
        
        #Nut tro ly LLM(placeholder)
        # assist_btn = ttk.Button(editor_frame, text="🤖", width=3, command=self.llm_assist)
        # assist_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        # ---------- Kết quả truy vấn ----------
        result_frame = ttk.Frame(self.frame)
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(result_frame, text="Kết quả truy vấn:").pack(anchor="w")

        self.table_frame = tk.Frame(result_frame)
        self.table_frame.pack(fill="both", expand=True)

        # Tạo bảng trống ban đầu
        self.ptable = Table(self.table_frame, dataframe=pd.DataFrame())
        self.ptable.show()

        # ---------- Nhật ký thực thi ----------
        log_frame = ttk.Frame(self.frame)
        log_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(log_frame, text="Nhật ký thực thi:").pack(anchor="w")

        self.log_text = tk.Text(log_frame, height=4, wrap="word", state="disabled")
        self.log_text.pack(fill="x", expand=True)

        # ---------- Các nút thao tác ----------
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(button_frame, text="Chạy", command=self.run_query).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.clear_query).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Lưu kết quả", command=self.save_result).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Gửi sang biểu đồ", command=self.send_to_plot).pack(side="left", padx=5)

    # --------- Các phương thức xử lý ---------
    def run_query(self):
        query = self.sql_text.get("1.0", "end").strip()
        if not query:
            return self.log("⚠️ Chưa nhập câu lệnh SQL.")
        try:
            self.main.ketnoi.cursor().execute(f"EXPLAIN {query}")
            self.log(f"Đang chạy câu lệnh:\n{query}")
            if self.run_query_callback:
                df = self.run_query_callback(query)
                if isinstance(df, pd.DataFrame):
                    self.update_result_table(df)
                    self.log(f"✅ Trả về {len(df)} dòng.")
                else:
                    self.log("⚠️ Không có dữ liệu trả về.")
        except Exception as e:
            self.log(f"Câu lệnh SQL không hợp lệ: {str(e)}")

    def clear_query(self):
        self.sql_text.delete("1.0", "end")

    def save_result(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Lưu kết quả dưới dạng CSV"
        )
        if not file_path:
            return
        try:
            df = self.ptable.model.df
            df.to_csv(file_path, index=False)
            self.log(f"💾 Đã lưu kết quả vào {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def send_to_plot(self):
        if self.send_to_plot_callback:
            df = self.ptable.model.df
            self.send_to_plot_callback(df)
            self.log("📊 Đã gửi dữ liệu sang tab Biểu đồ.")

    def update_result_table(self, df: pd.DataFrame):
        # Cập nhật DataFrame trong pandastable
        self.ptable.updateModel(TableModel(df))
        self.ptable.redraw()

    def log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def llm_assist(self):
        query = self.sql_text.get().strip()
        self.log(f"[🤖 Trợ lý] (placeholder) Sẽ gửi đến LLM:\n{query if query else '(trống)'}")
        
    def run(self):
        self.frame.mainloop()
        
if __name__ == "__main__":
    app = TabSQL()
    app.run()