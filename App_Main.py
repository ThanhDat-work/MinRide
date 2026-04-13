import tkinter as tk
from PIL import Image, ImageTk
import os
from tkinter import messagebox
import TinhNang
import sys
from main_pages.Customers import CustomersPage
from main_pages.Drivers import DriversPage
from main_pages.Rides import RidesPage
from main_pages.Booking import BookingPage
# ================== MAIN APP ==================

def resource_path(relative_path):
        if getattr(sys, 'frozen', False):
            # QUAN TRỌNG: Dòng này bảo code lấy đường dẫn của file EXE hiện tại
            # (Tức là thư mục dist), chứ KHÔNG chui vào Temp nữa.
            base_path = os.path.dirname(sys.executable) 
        else:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MinRide")
        self.geometry("540x960")
        # --- CẤU HÌNH MÃ PIN ---
        self.CORRECT_PIN = "171002"

        ASSET_NAME = "MR.png"
        ASSET_PATH = resource_path(ASSET_NAME)
        if not os.path.exists(ASSET_PATH):
            raise FileNotFoundError(f"Không thấy file ảnh: {ASSET_PATH}")

        # icon cửa sổ (giữ reference)
        self.app_icon = tk.PhotoImage(file=ASSET_PATH)
        self.iconphoto(True, self.app_icon)

        # logo header
        logo_pil = Image.open(ASSET_PATH).resize((32, 32))
        self.logo_img = ImageTk.PhotoImage(logo_pil)

        self.active_color = "#016B61"
        self.inactive_color = "#9AA0A6"

        # Màu sắc chủ đạo
        self.bg_color = "#B5E3D0"
        self.active_color = "#016B61"
        self.inactive_color = "#9AA0A6"

        # Container trang
        self.page_container = tk.Frame(self, bg="#B5E3D0")
        self.page_container.pack(side="top", fill="both", expand=True)
        self.pages = {
            "Customers": CustomersPage(self.page_container, self.logo_img),
            "Drivers": DriversPage(self.page_container, self.logo_img),
            "Rides": RidesPage(self.page_container, self.logo_img),
            "Booking": BookingPage(self.page_container, self.logo_img)
        }
        for p in self.pages.values():
            p.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_bottom_nav()
        self.setup_pin_screen(ASSET_PATH)

    def setup_pin_screen(self, asset_path):
        """Tạo lớp phủ màn hình khóa"""
        self.pin_overlay = tk.Frame(self, bg=self.bg_color)
        self.pin_overlay.place(x=0, y=0, relwidth=1, relheight=1)

        # Logo lớn
        try:
            logo_large_pil = Image.open(asset_path).resize((120, 120))
            self.logo_large = ImageTk.PhotoImage(logo_large_pil)
            tk.Label(self.pin_overlay, image=self.logo_large, bg=self.bg_color).pack(pady=(150, 20))
        except Exception as e:
            print("Lỗi load ảnh logo lớn:", e)

        tk.Label(self.pin_overlay, text="MIN RIDE", font=("Segoe UI", 24, "bold"), 
                 fg=self.active_color, bg=self.bg_color).pack()

        # --- KHUNG NHẬP PIN (Bảng trắng nhỏ) ---
        self.pin_frame = tk.Frame(self.pin_overlay, bg="white", padx=20, pady=20)
        self.pin_frame.pack(pady=40)
        
        tk.Label(self.pin_frame, text="Nhập mã PIN (6 số)", bg="white", font=("Segoe UI", 10)).pack()
        
        self.pin_entry = tk.Entry(self.pin_frame, show="*", font=("Segoe UI", 18), width=10, justify='center')
        self.pin_entry.pack(pady=10)
        self.pin_entry.focus_set()

        # Nút Xác nhận
        tk.Button(self.pin_frame, text="XÁC NHẬN", bg=self.active_color, fg="white", 
                  command=self.check_pin, width=15, font=("Segoe UI", 10, "bold"), 
                  cursor="hand2").pack(pady=5)

        # Nút Quên mật khẩu (Nằm ngay dưới nút Xác nhận)
        tk.Button(self.pin_frame, text="Quên mã PIN?", bg="white", fg=self.active_color, 
                  font=("Segoe UI", 9, "underline"), borderwidth=0, cursor="hand2",
                  command=self.show_forgot_help).pack(pady=5)

        # --- NÚT THOÁT (Dời xuống góc dưới bên trái màn hình) ---
        # Sử dụng place để đặt cố định ở góc
        self.btn_exit_pin = tk.Button(self.pin_overlay, text="🔙 Thoát ứng dụng", 
                                      bg=self.bg_color, fg="#000000", font=("Segoe UI", 11, "bold"),
                                      command=self.destroy, borderwidth=0, cursor="hand2")
        self.btn_exit_pin.place(x=20, y=910) # Tọa độ x, y gần góc dưới bên trái

        # Nút Tiếp tục (Ẩn mặc định)
        self.btn_continue = tk.Button(self.pin_overlay, text="TIẾP TỤC VÀO APP →", 
                                     font=("Segoe UI", 11, "bold"), bg=self.active_color, fg="#FFFFFF",
                                     command=self.enter_main_app, padx=20, pady=10, cursor="hand2")

    def show_forgot_help(self):
        """Hiện bảng hướng dẫn khi quên mã PIN"""
        huong_dan = (
            "HƯỚNG DẪN CẤP LẠI MÃ PIN\n\n"
            "1. Vui lòng liên hệ bộ phận kỹ thuật.\n"
            "2. Hotline: 0327.232.896 (A Đạt)\n"
            "3. Hoặc gửi yêu cầu qua Zalo số trên.\n\n"
            "Ứng dụng sẽ được mở khóa sau khi xác minh danh tính."
        )
        messagebox.showinfo("Quên mã PIN", huong_dan)
    def check_pin(self):
        if self.pin_entry.get() == self.CORRECT_PIN:
            self.pin_frame.destroy() # Xóa bảng nhập PIN
            self.btn_continue.pack(side="bottom", pady=100) # Hiện nút Tiếp tục
        else:
            messagebox.showerror("Lỗi", "Mã PIN không đúng. Vui lòng thử lại!")
            self.pin_entry.delete(0, tk.END)

    def enter_main_app(self):
        """Xóa hoàn toàn màn hình chờ để vào app chính"""
        self.pin_overlay.destroy()
        self.show_page("Customers")
        self.set_active(0)

    def show_page(self, page_name: str):
        page = self.pages[page_name]
        
        # KIỂM TRA: Nếu trang có hàm refresh_data thì gọi nó
        if hasattr(page, "refresh_data"):
            page.refresh_data()
            
        page.tkraise()

    def set_active(self, index: int):
        for i, (icon_lbl, text_lbl) in enumerate(self.btn_refs):
            if i == index:
                icon_lbl.config(fg=self.active_color)
                text_lbl.config(fg=self.active_color, font=("Segoe UI", 10, "bold"))
            else:
                icon_lbl.config(fg=self.inactive_color)
                text_lbl.config(fg=self.inactive_color, font=("Segoe UI", 10))

    def on_tab_click(self, index: int, name: str):
        if name == "Exit":
            self.destroy()
            return
        self.set_active(index)
        self.show_page(name)

    def create_bottom_nav(self):
        nav = tk.Frame(self, bg="white", height=86)
        nav.pack(side="bottom", fill="x")
        nav.pack_propagate(False)

        tk.Frame(nav, bg="#E9E9E9", height=1).pack(side="top", fill="x")

        row = tk.Frame(nav, bg="white")
        row.pack(expand=True, fill="both")

        tabs = [("Customers", "👥"), ("Drivers", "🚗"), ("Rides", "🗺️"), ("Booking", "➕"), ("Exit", "🚪")]
        self.btn_refs = []

        for i, (name, icon) in enumerate(tabs):
            cell = tk.Frame(row, bg="white")
            cell.grid(row=0, column=i, sticky="nsew")
            row.grid_columnconfigure(i, weight=1)

            icon_lbl = tk.Label(cell, text=icon, font=("Segoe UI Emoji", 18),
                                fg=self.inactive_color, bg="white")
            icon_lbl.pack(pady=(8, 0))

            text_lbl = tk.Label(cell, text=name, font=("Segoe UI", 10),
                                fg=self.inactive_color, bg="white")
            text_lbl.pack(pady=(0, 6))

            for w in (cell, icon_lbl, text_lbl):
                w.bind("<Button-1>", lambda e, idx=i, n=name: self.on_tab_click(idx, n))

            self.btn_refs.append((icon_lbl, text_lbl))


if __name__ == "__main__":
    App().mainloop()
