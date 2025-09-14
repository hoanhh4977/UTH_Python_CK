import io
import json
import requests
import pandas as pd
from threading import Thread
from urllib.error import URLError

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
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", "Loại file không hỗ trợ."))
                    return

                if duong_dan.lower().endswith(".csv"):
                    # đọc csv (có thể ném EmptyDataError, ParserError, UnicodeDecodeError, FileNotFoundError...)
                    self.data = pd.read_csv(duong_dan)
                else:
                    # đọc json
                    # pd.read_json có thể ném ValueError nếu không parse được
                    self.data = pd.read_json(duong_dan)

                # cập nhật UI trong main thread
                self.root.after(0, self.hien_thi_bang)

            except FileNotFoundError:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm thấy file."))
            except PermissionError:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không có quyền truy cập file."))
            except pd.errors.EmptyDataError:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "File rỗng."))
            except pd.errors.ParserError as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi phân tích file CSV: {e}"))
            except UnicodeDecodeError:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể giải mã file (encoding)."))
            except Exception as e:
                # catch-all để tránh crash; in log để debug
                print("Error load local file:", e)
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi đọc file: {e}"))
            finally:
                # hide loader luôn phải chạy trên main thread
                self.root.after(0, self.loader.hide)

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
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", "Loại file không hỗ trợ."))
                    return

                # tải nội dung với timeout (nếu mạng yếu hoặc không có internet sẽ ném lỗi)
                text = self._download_text(url, timeout=10)

                # chuyển sang DataFrame tùy loại
                if url_l.endswith(".csv"):
                    try:
                        self.data = pd.read_csv(io.StringIO(text))
                    except pd.errors.EmptyDataError:
                        self.root.after(0, lambda: messagebox.showerror("Lỗi", "File CSV rỗng."))
                        return
                    except pd.errors.ParserError as e:
                        self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi phân tích CSV: {e}"))
                        return
                    except UnicodeDecodeError:
                        self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể giải mã nội dung CSV."))
                        return
                else:  # json
                    try:
                        # thử đọc bằng pandas
                        self.data = pd.read_json(io.StringIO(text))
                    except ValueError:
                        # fallback: parse json thủ công rồi normalise
                        obj = json.loads(text)
                        # nếu obj là dict hoặc list, chuyển qua DataFrame
                        self.data = pd.json_normalize(obj)

                # Thành công: cập nhật UI
                self.root.after(0, self.hien_thi_bang)

            except requests.exceptions.Timeout:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Hết thời gian chờ khi tải dữ liệu. Kiểm tra kết nối."))
            except (requests.exceptions.ConnectionError, ConnectionRefusedError):
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể kết nối đến server. Kiểm tra Internet."))
            except requests.exceptions.HTTPError as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Server trả lỗi HTTP: {e}"))
            except URLError:
                # nếu dùng urllib, URLError sẽ được bắt ở đây
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể tải dữ liệu. Kiểm tra kết nối Internet."))
            except json.JSONDecodeError:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Dữ liệu JSON không hợp lệ."))
            except Exception as e:
                print("Error download url:", e)
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu: {e}"))
            finally:
                self.root.after(0, self.loader.hide)

        Thread(target=task, daemon=True).start()

    def hien_thi_bang(self):
        # kiểm tra self.data tồn tại và không rỗng
        if isinstance(self.data, pd.DataFrame) and not self.data.empty:
            self.bang.updateModel(TableModel(self.data))
            self.bang.redraw()
        else:
            # nếu không có dữ liệu, xóa bảng hiện tại
            self.bang.updateModel(TableModel(pd.DataFrame()))
            self.bang.redraw()
            messagebox.showinfo("Thông báo", "Không có dữ liệu để hiển thị.")
        
    def hien_thi_bang(self):
        if not self.data.empty:
            self.bang.updateModel(TableModel(self.data))
            self.bang.redraw()

    def set_main(self, main_window):
        self.main = main_window
    
if __name__ == "__main__":
    app = TabTaiDuLieu()
    app.run()