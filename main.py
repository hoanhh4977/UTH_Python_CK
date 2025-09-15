import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

from src.app.man_hinh_chinh import ManHinhChinh


class WelcomeScreen:
    def __init__(self, root):
        self.root = root

        # --- Load ảnh nền ---
        self.bg_image = Image.open("assets/Ranitas.jfif")
        self.bg_image = self.bg_image.resize((1200, 750))  # vừa với cửa sổ
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # --- Tạo label nền ---
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- Frame cho nội dung chào ---
        self.frame = ttk.Frame(root, padding=20)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            self.frame,
            text="Chào mừng đến với Quản lý CSDL 🎉",
            font=("Helvetica", 20, "bold"),
            foreground="darkblue"
        ).pack(pady=20)

        ttk.Button(
            self.frame,
            text="👉 Bắt đầu ngay",
            command=self.start_app
        ).pack(pady=10)

    def start_app(self):
        # Xóa màn hình welcome
        self.frame.destroy()
        self.bg_label.destroy()

        # Gọi màn hình chính
        ManHinhChinh(self.root)


def main():
    root = ThemedTk(theme="radiance")
    root.title("Quản lý CSDL - Nguyễn Hoàng Anh - 066306006917")
    root.geometry("1200x750")
    # root.state("zoomed")

    WelcomeScreen(root)  # Bắt đầu với màn hình chào

    root.mainloop()


if __name__ == "__main__":
    main()
