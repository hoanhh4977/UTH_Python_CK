import io
import json
import requests
import pandas as pd
from threading import Thread
from urllib.error import URLError

from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Label, Entry, Button, Frame
from pandastable import Table, TableModel

from src.app.widgets.loader import Loader
from src.utils.utilities import is_valid_url

class TabTaiDuLieu:
    def __init__(self, notebook):
        self.frame = Frame(notebook)
        self.loader = Loader(self.frame)
        self.main = None
        self.build_ui()
    
    def build_ui(self):
        self.frame.rowconfigure(2, weight=1)
        self.frame.columnconfigure(0, weight=1)
        # Dòng đầu tiên
        Label(self.frame, text="Tải dữ liệu từ máy:").grid(row=0, column=0, sticky="w")
        self.tai_du_lieu_tu_may_entry = Entry(self.frame, width=50, state="disabled")
        self.tai_du_lieu_tu_may_entry.grid(row=0, column=1, sticky="ew", padx=10)
        Button(self.frame, text="Chọn...", command=self.tai_du_lieu_tu_may).grid(row=0, column=2)
        
        # Dòng thứ hai
        Label(self.frame, text="Tải dữ liệu từ URL:").grid(row=1, column=0, sticky="w")
        self.tai_du_lieu_tu_url_entry = Entry(self.frame, width=50)
        self.tai_du_lieu_tu_url_entry.grid(row=1, column=1, sticky="ew", padx=10)
        Button(self.frame, text="Tải dữ liệu", command=self.tai_du_lieu_tu_url).grid(row=1, column=2)
        
        # Dòng thứ ba
        khung_bang = Frame(self.frame)
        khung_bang.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.bang = Table(khung_bang, dataframe=pd.DataFrame())
        self.bang.show()

        # Dòng thứ tư
        Button(self.frame,text="Nhập vào CSDL", command=self.nhap_vao_csdl).grid(row=3,column=0, columnspan=3)
        
    def run(self):
        self.frame.mainloop()
    
    # --- Tải file từ máy ---
    def tai_du_lieu_tu_may(self):
        duong_dan = filedialog.askopenfilename()
        if not duong_dan:
            return
        self.tai_du_lieu_tu_may_entry.delete(0, 'end')
        self.tai_du_lieu_tu_may_entry.insert(0, duong_dan)

        self.loader.show()

        def task():
            try:
                if not duong_dan.lower().endswith((".csv", ".json")):
                    # không hỗ trợ định dạng
                    self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Loại file không hỗ trợ."))
                    return

                if duong_dan.lower().endswith(".csv"):
                    # đọc csv
                    self.main.imported_data = pd.read_csv(duong_dan)
                else:
                    # đọc json
                    self.main.imported_data = pd.read_json(duong_dan)

                # cập nhật UI trong main thread
                self.frame.after(0, self.hien_thi_bang)

            except FileNotFoundError:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm thấy file."))
            except PermissionError:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Không có quyền truy cập file."))
            except pd.errors.EmptyDataError:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "File rỗng."))
            except pd.errors.ParserError as e:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi phân tích file CSV"))
            except UnicodeDecodeError:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Không thể giải mã file (encoding)."))
            except Exception as e:
                # catch-all để tránh crash; in log để debug
                print("Error load local file:", e)
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi đọc file"))
            finally:
                # hide loader luôn phải chạy trên main thread
                self.frame.after(0, self.loader.hide)

        Thread(target=task, daemon=True).start()
            
    # --- Tải file từ URL ---
    def tai_du_lieu_tu_url(self):
        url = self.tai_du_lieu_tu_url_entry.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL.")
            return

        if not is_valid_url(url):
            messagebox.showerror("Lỗi", "URL không hợp lệ.")
            return

        self.loader.show()

        def task():
            try:
                url_l = url.lower()
                if not url_l.endswith((".csv", ".json")):
                    self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Loại file không hỗ trợ."))
                    return

                # tải nội dung với timeout (nếu mạng yếu hoặc không có internet sẽ ném lỗi)
                text = self._download_text(url, timeout=10)

                # chuyển sang DataFrame tùy loại
                if url_l.endswith(".csv"):
                    try:
                        self.main.imported_data = pd.read_csv(io.StringIO(text))
                    except pd.errors.EmptyDataError:
                        self.frame.after(0, lambda: messagebox.showerror("Lỗi", "File CSV rỗng."))
                        return
                    except pd.errors.ParserError as e:
                        self.frame.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi phân tích CSV: {e}"))
                        return
                    except UnicodeDecodeError:
                        self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Không thể giải mã nội dung CSV."))
                        return
                else:  # json
                    try:
                        # thử đọc bằng pandas
                        self.main.imported_data = pd.read_json(io.StringIO(text))
                    except ValueError:
                        # fallback: parse json thủ công rồi normalise
                        obj = json.loads(text)
                        # nếu obj là dict hoặc list, chuyển qua DataFrame
                        self.main.imported_data = pd.json_normalize(obj)

                # Thành công: cập nhật UI
                self.frame.after(0, self.hien_thi_bang)

            except requests.exceptions.Timeout:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Hết thời gian chờ khi tải dữ liệu. Kiểm tra kết nối."))
            except (requests.exceptions.ConnectionError, ConnectionRefusedError):
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Không thể kết nối đến server. Kiểm tra Internet."))
            except requests.exceptions.HTTPError as e:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", f"Server trả lỗi HTTP: {e}"))
            except URLError:
                # nếu dùng urllib, URLError sẽ được bắt ở đây
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Không thể tải dữ liệu. Kiểm tra kết nối Internet."))
            except json.JSONDecodeError:
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", "Dữ liệu JSON không hợp lệ."))
            except Exception as e:
                print("Error download url:", e)
                self.frame.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu"))
            finally:
                self.frame.after(0, self.loader.hide)

        Thread(target=task, daemon=True).start()

    def hien_thi_bang(self):
        # kiểm tra self.main.imported_data tồn tại và không rỗng
        if isinstance(self.main.imported_data, pd.DataFrame) and not self.main.imported_data.empty:
            self.bang.updateModel(TableModel(self.main.imported_data))
            self.bang.redraw()
        else:
            # nếu không có dữ liệu, xóa bảng hiện tại
            self.bang.updateModel(TableModel(pd.DataFrame()))
            self.bang.redraw()
            messagebox.showinfo("Thông báo", "Không có dữ liệu để hiển thị.")
        
    def nhap_vao_csdl(self):
        if self.main.imported_data is None or self.main.imported_data.empty:
            messagebox.showerror("Lỗi", "Không có dữ liệu để nhập.")
            return

        if not hasattr(self.main, "ketnoi") or self.main.ketnoi is None:
            messagebox.showerror("Lỗi", "Chưa kết nối tới CSDL.")
            return

        conn = self.main.ketnoi

        # Hỏi người dùng muốn tạo mới hay thêm
        lua_chon = messagebox.askquestion(
            "Nhập vào CSDL",
            "Bạn có muốn tạo bảng mới không?\n"
            "Chọn 'Yes' để tạo bảng mới.\n"
            "Chọn 'No' để thêm vào bảng có sẵn."
        )

        if lua_chon == "yes":
            # Nhập tên bảng
            table_name = simpledialog.askstring("Tên bảng", "Nhập tên bảng mới:")
            if not table_name:
                return

            try:
                self.main.imported_data.to_sql(table_name, conn, if_exists="fail", index=False)
                self.main.tab_chon_file_db.ket_noi_DB()
                messagebox.showinfo("Thành công", f"Đã tạo bảng '{table_name}' và nhập dữ liệu.")
            except ValueError:
                messagebox.showerror("Lỗi", f"Bảng '{table_name}' đã tồn tại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo bảng mới: {e}")
            return

        else:
            # Lấy danh sách bảng hiện có
            try:
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';",
                    conn
                )["name"].tolist()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lấy danh sách bảng: {e}")
                return

            if not tables:
                messagebox.showerror("Lỗi", "CSDL không có bảng nào để thêm dữ liệu.")
                return

            # Cho người dùng chọn bảng (đơn giản bằng dialog nhập tên)
            table_name = simpledialog.askstring(
                "Tên bảng",
                f"Nhập tên bảng để thêm (các bảng hiện có: {', '.join(tables)})"
            )
            if not table_name or table_name not in tables:
                messagebox.showerror("Lỗi", "Tên bảng không hợp lệ.")
                return

            # Kiểm tra schema
            try:
                existing = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 0;", conn)
                missing_cols = [c for c in self.main.imported_data.columns if c not in existing.columns]
                extra_cols = [c for c in existing.columns if c not in self.main.imported_data.columns]

                if missing_cols or extra_cols:
                    msg = "Schema không khớp:\n"
                    if missing_cols:
                        msg += f"- Cột mới không có trong bảng: {missing_cols}\n"
                    if extra_cols:
                        msg += f"- Cột trong bảng nhưng thiếu trong dữ liệu: {extra_cols}\n"
                    messagebox.showerror("Lỗi", msg)
                    return

                # Nếu schema hợp lệ, append dữ liệu
                self.main.imported_data.to_sql(table_name, conn, if_exists="append", index=False)
                messagebox.showinfo("Thành công", f"Đã thêm {len(self.main.imported_data)} dòng vào bảng '{table_name}'.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm dữ liệu vào bảng '{table_name}': {e}")
    def _download_text(self, url, timeout=10):
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    def set_main(self, main_window):
        self.main = main_window
