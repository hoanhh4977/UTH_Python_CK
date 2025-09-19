
import re
import tkinter as tk
from threading import Thread
from tkinter import ttk, Text, messagebox, filedialog, Frame
from tkinter.ttk import Label, Button, Entry, Scrollbar
from pandastable import Table, TableModel
import pandas as pd

from src.gpt.text2sql import Text2SQLAgent
from src.app.widgets.loader import Loader

class TabSQL:
    def __init__(self, notebook):
        self.agent = Text2SQLAgent()

        self.frame = Frame(notebook)
        self.main = None
        self.loader = Loader(self.frame)
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
        
        # --- Khung nhập SQL ---
        editor_frame = Frame(self.frame)
        editor_frame.pack(fill="x", padx=5, pady=5)

        Label(editor_frame, text="Câu lệnh SQL:").pack(anchor="w")

        # Frame con cho SQL + scroll
        sql_box_frame = Frame(editor_frame)
        sql_box_frame.pack(fill="x")

        self.sql_text = Text(sql_box_frame, height=8, wrap="none")
        self.sql_text.pack(side="left", fill="x", expand=True)

        # Thanh cuộn cho ô SQL
        sql_scroll = Scrollbar(sql_box_frame, command=self.sql_text.yview)
        sql_scroll.pack(side="right", fill="y")
        self.sql_text.config(yscrollcommand=sql_scroll.set)


        # --- Khung trợ lý + nhập ngôn ngữ tự nhiên ---
        assist_frame = Frame(self.frame)
        assist_frame.pack(fill="x", padx=5, pady=5)

        Label(assist_frame, text="Mô tả bằng ngôn ngữ:").pack(anchor="w")

        # Frame con cho NL input + scroll + button
        nl_box_frame = Frame(assist_frame)
        nl_box_frame.pack(fill="x")

        # Ô nhập ngôn ngữ tự nhiên
        self.nl_input = tk.Text(nl_box_frame, height=3, wrap="word")
        self.nl_input.pack(side="left", fill="x", expand=True)

        # Thanh cuộn riêng cho ô NL
        nl_scroll = Scrollbar(nl_box_frame, command=self.nl_input.yview)
        nl_scroll.pack(side="right", fill="y")
        self.nl_input.config(yscrollcommand=nl_scroll.set)

        # Nút GPT trợ lý (nằm bên phải NL input)
        assist_btn = Button(
            assist_frame, text="🤖", width=4, command=self.llm_assist
        )
        assist_btn.pack(anchor="e", pady=2)
        
        # ---------- Kết quả truy vấn + Nhật ký thực thi ----------
        container_frame = Frame(self.frame)
        container_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Kết quả truy vấn ---
        result_frame = Frame(container_frame)
        result_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        Label(result_frame, text="Kết quả truy vấn:").pack(anchor="w")

        self.table_frame = Frame(result_frame)
        self.table_frame.pack(fill="both", expand=True)

        # Tạo bảng trống ban đầu
        self.ptable = Table(self.table_frame, dataframe=pd.DataFrame())
        self.ptable.show()

        # --- Nhật ký thực thi ---
        log_frame = Frame(container_frame, width=70)  # đặt width cho cân đối
        log_frame.pack(side="right", fill="both")

        Label(log_frame, text="Nhật ký thực thi:").pack(anchor="w")

        self.log_text = Text(log_frame, height=8, width=70, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)

        # ---------- Các nút thao tác ----------
        button_frame = Frame(self.frame)
        button_frame.pack(fill="x", pady=5)

        Button(button_frame, text="Chạy", command=self.run_query).pack(side="left", padx=5)
        Button(button_frame, text="Xóa", command=self.clear_query).pack(side="left", padx=5)
        Button(button_frame, text="Lưu kết quả", command=self.save_result).pack(side="left", padx=5)
        Button(button_frame, text="Gửi sang biểu đồ", command=self.send_to_plot).pack(side="left", padx=5)

    # --------- Các phương thức xử lý ---------
    def run_query(self):
        # Thực thi câu lệnh SQL
        query = self.sql_text.get("1.0", "end").strip()
        if not query:
            return self.log("⚠️ Chưa nhập câu lệnh SQL.")

        def task():
            try:
                self.main.ketnoi.cursor().execute(f"EXPLAIN {query}")
                self._log_threadsafe(f"Đang chạy câu lệnh:\n{query}")
                if self.run_query_callback:
                    df = self.run_query_callback(query)
                    if isinstance(df, pd.DataFrame):
                        self._update_result_table_threadsafe(df)
                        self._log_threadsafe(f"✅ Trả về {len(df)} dòng.")
                    else:
                        self._log_threadsafe("⚠️ Không có dữ liệu trả về.")
            except Exception as e:
                self._log_threadsafe(f"Câu lệnh SQL không hợp lệ: {str(e)}")
            finally:
                self.frame.after(0, self.loader.hide)

        self.loader.show(is_pack=True)
        Thread(target=task, daemon=True).start()


    def clear_query(self):
        # Xóa câu lệnh SQL hiện tại
        self.sql_text.delete("1.0", "end")

    def save_result(self):
        # Lưu kết quả vào 1 file csv
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
        # Gửi kết quả vào biến query_data của màn hình chính
        if self.send_to_plot_callback:
            df = self.ptable.model.df
            self.send_to_plot_callback(df)
            self.log("📊 Đã gửi dữ liệu sang tab Biểu đồ.")

    def update_result_table(self, df: pd.DataFrame):
        # Cập nhật DataFrame trong pandastable
        self.ptable.updateModel(TableModel(df))
        self.ptable.redraw()

    def log(self, message: str):
        # In ra thông tin vào ô nhật ký thực thi
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def llm_assist(self):
        # Sử dụng AI để sinh ra câu lệnh SQL
        query = self.nl_input.get("1.0", "end-1c").strip()
        db_path = self.main.tab_chon_file_db.chon_file_DB_entry.get().strip()
        self.log(f"[🤖 Trợ lý] (placeholder) Sẽ gửi đến LLM:\n{query if query else '(trống)'}")

        def task():
            try:
                messages, sql_query = self.agent.run(query=query, db_path=db_path)
                self.frame.after(0, lambda: self._set_sql_text(sql_query))

                for message in messages:
                    message_content = re.sub(r"=+", "=====", message.pretty_repr())
                    self._log_threadsafe(message_content)
            except Exception as e:
                self._log_threadsafe(f"Lỗi khi gọi LLM: {str(e)}")
            finally:
                self.frame.after(0, self.loader.hide)

        self.loader.show(is_pack=True)
        Thread(target=task, daemon=True).start()

    def _log_threadsafe(self, message: str):
        self.frame.after(0, lambda: self.log(message))

    def _update_result_table_threadsafe(self, df: pd.DataFrame):
        self.frame.after(0, lambda: self.update_result_table(df))

    def _set_sql_text(self, sql_query: str):
        self.sql_text.delete("1.0", "end")
        if sql_query:
            self.sql_text.insert("1.0", sql_query)
