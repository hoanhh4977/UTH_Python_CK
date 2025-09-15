from ttkthemes import ThemedTk
from src.app.main_window import HoangAnh

def main():
    # root = tk.Tk()
    root = ThemedTk(theme="radiance")
    # style = ttk.Style(root)
    # style.theme_use("vista")

    root.title("Quản lý CSDL")
    root.geometry("900x750")
    HoangAnh(root)
    root.mainloop()

if __name__ == "__main__":
    main()