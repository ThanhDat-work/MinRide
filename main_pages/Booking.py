import tkinter as tk
import TinhNang
from services.ride_repo import RideManager
from TinhNang import Ride
from services.driver_repo import DriverManager
from services.customer_repo import CustomerManager
import math
import random
# ================== BOOKING PAGE ==================
class BookingPage(tk.Frame):
    def __init__(self, parent, logo_img):
        super().__init__(parent, bg="#B5E3D0")
        self.logo_img=logo_img

        self.cv = tk.Canvas(self, highlightthickness=0, bg="#B5E3D0")
        self.cv.pack(fill="both", expand=True)
        self.cv.bind("<Configure>", self.draw_ui)

        # ===== Tiles =====
        self.tiles = [
            ("Booking", "Book"),
            ("User Guide", "Guide"),
            ("About MinRide", "About")
        ]

        # ===== Accordion state =====
        self.expanded_key = None
        self.expand_window_id = None
        self.panel_frame = None  # panel hiện tại (Frame)

        # ===== Tile effects =====
        self.tile_radius = 18
        self.tile_fill = "white"
        self.tile_hover_fill = "#F3F9F8"
        self.tile_title_color = "#1C1C1C"
        self.tile_hover_title = "#016B61"
        self.tile_shadow_normal = "#DDE7E5"
        self.tile_shadow_hover = "#C9D6D4"
        self.tile_items = {}  # key -> ids

        # ===== In-memory data (demo) =====
        self.ride=RideManager("data/trips.csv")
        self.customer=CustomerManager("data/customers.csv")
        self.driver=DriverManager("data/drivers.csv")

        # ===== shared UI state for panels =====
        self.msg_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="")

        # ===== Trạng thái đặt xe (Steps) =====
        self.booking_step = 1  # 1: Nhập ID, 2: Tìm tài xế, 3: Đánh giá
        self.temp_customer = None
        self.temp_driver = None
        self.cid_var = tk.StringVar()    # Lưu ID khách nhập vào
        self.rating_var = tk.StringVar() # Lưu số sao đánh giá
        self.radius_var = tk.StringVar()
        self.potential_drivers = []
        self.dest_x = tk.StringVar()
        self.dest_y = tk.StringVar()

        # ================= TILE EFFECTS =================
    def _tile_tag(self, key): return f"tile:{key}"

    def _hover_in(self, key):
        info = self.tile_items.get(key)
        if not info: return
        self.cv.itemconfig(info["rect_id"], fill=self.tile_hover_fill)
        self.cv.itemconfig(info["text_id"], fill=self.tile_hover_title)
        self.cv.itemconfig(info["shadow_id"], fill=self.tile_shadow_hover)

    def _hover_out(self, key):
        info = self.tile_items.get(key)
        if not info: return
        self.cv.itemconfig(info["rect_id"], fill=self.tile_fill)
        self.cv.itemconfig(info["text_id"], fill=self.tile_title_color)
        self.cv.itemconfig(info["shadow_id"], fill=self.tile_shadow_normal)

    def _press_in(self, key):
        info = self.tile_items.get(key)
        if not info or info.get("pressed"): return
        info["pressed"] = True
        for _id in info["all_ids"]:
            self.cv.move(_id, 0, 3)

    def _press_out(self, key):
        info = self.tile_items.get(key)
        if not info or not info.get("pressed"): return
        info["pressed"] = False
        for _id in info["all_ids"]:
            self.cv.move(_id, 0, -3)
        self.after(70, lambda: self._expand(key))

    # ================= ACCORDION =================
    def _expand(self, key):
        # toggle
        if self.expanded_key == key:
            self.expanded_key = None
        else:
            self.expanded_key = key

        # reset message/results mỗi lần mở panel
        self.msg_var.set("")
        self.result_var.set("")
        self.draw_ui()

    # ================= DATA OPS =================
    def _find_by_id(self, cid: int):
        for c in self.repo1:
            if c.tripID == cid:
                return c
        return None

    # ================= PANEL BUILDERS =================
    def _panel_wrap(self, parent, title):
        wrap = tk.Frame(parent, bg="white")
        tk.Label(wrap, text=title, bg="white", fg="#1C1C1C",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        if self.msg_var.get() != "":
            tk.Label(wrap, textvariable=self.msg_var, bg="white", fg="#016B61",
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        return wrap

    def _field(self, parent, label, var):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, bg="white", fg="#4A4A4A",
                 font=("Segoe UI", 10)).pack(side="left")
        ent = tk.Entry(row, textvariable=var, font=("Segoe UI", 10),
                       bd=0, relief="flat", bg="#DDF1EE")
        ent.pack(side="right", fill="x", expand=True, padx=(10, 0))
        return ent

    def _result_box(self, parent):
        frame = tk.Frame(parent, bg="#F3F9F8")
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        box = tk.Text(frame, height=9, font=("Consolas", 10), 
                      bd=0, bg="#F3F9F8", yscrollcommand=scrollbar.set)
        box.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=box.yview)

        box.insert("end", self.result_var.get())
        box.config(state="disable") # Chỉ cho đọc, không cho sửa
        return box

    def _build_list_panel(self, parent):
        if self.booking_step == 1:
            return self._step1_input_customer(parent)
        elif self.booking_step == 2:
            return self._step2_find_driver(parent)
        elif self.booking_step == 2.5: # Thêm bước xác nhận này
            return self._step2_5_confirm_booking(parent)
        elif self.booking_step == 3:
            return self._step3_rating_trip(parent)
        
    def _set_step(self, step_number):
        self.booking_step = step_number
        self.msg_var.set("") # Xóa thông báo lỗi cũ khi đổi bước
        self.draw_ui()

    def _step1_input_customer(self, parent):
        wrap = self._panel_wrap(parent, "📍 NHẬP ID KHÁCH HÀNG")
        tk.Label(wrap, text="Hệ thống sẽ tự động định vị tọa độ khách hàng.", 
                 bg="white", fg="gray").pack(anchor="w")
        
        self._field(wrap, "Mã số khách hàng (ID):", self.cid_var)
        self._field(wrap, "Bán kính tìm kiếm (km):", self.radius_var)
        self._field(wrap, "Tọa độ x (điểm đến):", self.dest_x)
        self._field(wrap, "Tọa độ y (điểm đến):", self.dest_y)

        btn_next = tk.Button(wrap, text="Tìm tài xế ➔", bg="#016B61", fg="white",
                             font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                             command=self._logic_step1_to_2)
        btn_next.pack(pady=20, fill="x")
        return wrap

    def _logic_step1_to_2(self):
        # Logic: Tìm khách hàng trong database
        try:
            cid = int(self.cid_var.get())
            radius = float(self.radius_var.get())
            dx = float(self.dest_x.get()) # Điểm đến X
            dy = float(self.dest_y.get()) # Điểm đến Y

            cust = self.customer.find_customer_by_ID(cid) # Giả sử hàm này có trong CustomerManager
            if not cust:
                self.msg_var.set("❌ Không tìm thấy ID khách hàng!")
                self.draw_ui()
                return
            driver= self.driver.find_all_drivers_in_radius(cust.x, cust.y, radius)

            if driver:
                self.temp_customer = cust
                self.potential_drivers=driver
                self.temp_dist_trip = math.sqrt((dx - cust.x)**2 + (dy - cust.y)**2)
                self._set_step(2)
            else:
                # Báo lỗi nếu không có ai ở gần
                self.msg_var.set(f"☹ Rất tiếc, không có tài xế nào trong bán kính {radius} km!")

            self.draw_ui()
        except ValueError:
            self.msg_var.set("⚠ Lỗi đầu vào. Vui lòng nhập lại!")
            self.draw_ui()

    def _step2_find_driver(self, parent):
        wrap = self._panel_wrap(parent, f"🚕 TÌM TÀI XẾ CHO: {self.temp_customer.name}")
        
        # 1. Tạo Container chính để chứa Canvas và Scrollbar
        container = tk.Frame(wrap, bg="#F3F9F8")
        container.pack(fill="both", expand=True, pady=5)

        # 2. Tạo Canvas
        canvas = tk.Canvas(container, bg="#F3F9F8", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # 3. Tạo Frame bên trong Canvas (đây mới là nơi chứa các Card tài xế)
        scrollable_frame = tk.Frame(canvas, bg="#F3F9F8")

        # Cấu hình Canvas để nhận diện Frame bên trong
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # QUAN TRỌNG: Lấy chiều rộng của panel để ép frame con giãn ra
        canvas_width = 450
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas_width)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Đóng gói Canvas và Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for drv, dist in self.potential_drivers:
            # Mỗi tài xế là một cái khung nhỏ
            card = tk.Frame(scrollable_frame, bg="white", bd=1, relief="groove")
            card.pack(fill="x", pady=2, padx=5)

            info = f"ID: {drv.id} - {drv.name} | 📍 {dist:.2f} km | ⭐ {drv.rating}"
            tk.Label(card, text=info, bg="white", font=("Segoe UI", 9), justify="left").pack(side="left", padx=10, pady=5)
            
            # Nút chọn tài xế này
            btn_select = tk.Button(card, text="Chọn", bg="#80D7CB", relief="flat",
                                   command=lambda d=drv, dst=dist: self._select_this_driver(d, dst))
            btn_select.pack(side="right", padx=5)

        # 5. Hỗ trợ cuộn bằng con lăn chuột (Mousewheel)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Nút Quay lại nếu muốn nhập lại bán kính
        tk.Button(wrap, text="⬅ Quay lại", command=lambda: self._set_step(1)).pack(side="left", pady=5)
        return wrap

    def _select_this_driver(self, driver, dist):
        self.temp_driver = driver
        self.temp_dist = dist
        self.booking_step = 2.5 # Bước trung gian để Xác nhận
        self.draw_ui()

    def _step2_5_confirm_booking(self, parent):
        wrap = self._panel_wrap(parent, "📑 XÁC NHẬN CHUYẾN ĐI")
        
        price = round(self.temp_dist_trip,2) * 12000
        summary = (f"Khách hàng: {self.temp_customer.name}\n"
                   f"Tài xế: {self.temp_driver.name}\n"
                   f"Quãng đường: {round(self.temp_dist_trip,2)} km\n"
                   f"Tổng tiền: {price:,.0f} VNĐ")
        self.result_var.set(summary)
        self._result_box(wrap)
        # NÚT QUAN TRỌNG NHẤT: Nhấn đây mới lưu Database
        # Tạo khung chứa 2 nút nằm ngang
        btn_frame = tk.Frame(wrap, bg="white")
        btn_frame.pack(fill="x", pady=10)

        # NÚT HỦY: Quay lại Bước 2 để chọn lại tài xế hoặc Bước 1
        btn_cancel = tk.Button(btn_frame, text="✖ HỦY BỎ", bg="#FF6B6B", fg="white",
                               font=("Segoe UI", 11, "bold"), height=2, width=15,
                               command=lambda: self._set_step(2)) # Quay lại danh sách tài xế
        btn_cancel.pack(side="left", padx=(0, 5), expand=True, fill="x")

        # NÚT XÁC NHẬN
        btn_confirm = tk.Button(btn_frame, text="✔ XÁC NHẬN", bg="#016B61", fg="white",
                                font=("Segoe UI", 11, "bold"), height=2, width=15,
                                command=self._logic_step2_to_3)
        btn_confirm.pack(side="right", padx=(5, 0), expand=True, fill="x")
        
        return wrap

    def _logic_step2_to_3(self):
        new_id = int(self.ride.generate_new_id())
        time_str = self.ride.generate_logical_time()
        price = int(round(self.temp_dist_trip,2) * 12000)

        new_trip = Ride(
            tripID=new_id,
            customerID=int(self.temp_customer.id),
            driverID=int(self.temp_driver.id),
            timestamp=time_str,
            distance=round(self.temp_dist_trip,2),
            fare=price,
            rate=0 # Tạm thời bằng 0
        )
        if self.ride.add_ride(new_trip):
            self.current_trip_id = new_id # Lưu lại ID để update rating ở bước sau
            self.msg_var.set(f"✅ Đặt thành công! Mã chuyến: {new_id}")
            self._set_step(3)
        else:
            self.msg_var.set("❌ Lỗi lưu dữ liệu!")
        self.draw_ui()

    def _step3_rating_trip(self, parent):
        wrap = self._panel_wrap(parent, "⭐ HOÀN THÀNH & ĐÁNH GIÁ")
        
        tk.Label(wrap, text="Chuyến đi đã kết thúc an toàn!", bg="white", font=("Segoe UI", 11, "bold")).pack(pady=10)
        self._field(wrap, "Nhập đánh giá:", self.rating_var)

        btn_finish = tk.Button(wrap, text="Lưu & Quay về Trang chủ", bg="#1C1C1C", fg="white",
                               font=("Segoe UI", 11, "bold"), relief="flat", command=self._logic_finish)
        btn_finish.pack(pady=20, fill="x")
        return wrap

    def _logic_finish(self):
        try:
            # 1. Cập nhật Rating cho chuyến vừa đi
            score = float(self.rating_var.get())
            if not score:
                self.msg_var.set("⚠ Vui lòng nhập số sao!")
                self.draw_ui()
                return
            
            if score < 0 or score > 5:
                self.msg_var.set("❌ Đánh giá không hợp lệ. Vui lòng nhập lại!")
                self.rating_var.set("") # Xóa input sai để khách nhập lại
                self.draw_ui()
                return

            self.ride.trips[-1].rate=score
            self.ride.save_all_to_csv()
            # 2. Cập nhật vị trí KHÁCH HÀNG -> Điểm đến (Số nguyên)
            nx, ny = float(self.dest_x.get()), float(self.dest_y.get())
            self.customer.update_customer_pos(self.temp_customer.id, nx, ny)

            # 3. CẬP NHẬT TÀI XẾ -> Random vị trí mới
            
            rx, ry = round(random.uniform(0, 10),1), round(random.uniform(0, 10),1)
            self.driver.update_driver_pos(self.temp_driver.id, rx, ry, score)

            # 4. Reset giao diện
            self.msg_var.set("✅ Đã cập nhật vị trí của khách hàng và tài xế!")
            self._set_step(1)
            self.cid_var.set("")
            self.radius_var.set("")
            self.rating_var.set("")
            self.dest_x.set("")
            self.dest_y.set("")
            self.draw_ui()
            
        except ValueError:
            self.msg_var.set("⚠ Lỗi cập nhập!")

    def _build_guide_panel(self, parent):
        # Tạo khung bao ngoài có tiêu đề
        wrap = self._panel_wrap(parent, "📖 Hướng dẫn sử dụng MinRide")
        
        # Nội dung hướng dẫn
        guide_text = (
            "Chào mừng bạn đến với hệ thống điều phối MinRide!\n"
            "------------------------------------------\n"
            "👉 BƯỚC 1: NHẬP THÔNG TIN KHÁCH HÀNG\n"
            "   - Tại mục 'Booking', hãy nhập ID của khách hàng.\n"
            "   - Nhập bán kính tìm kiếm và tọa độ điểm đến.\n"
            "   - Hệ thống sẽ tự động lấy tọa độ hiện tại của khách.\n\n"
            "👉 BƯỚC 2: TÌM KIẾM TÀI XẾ GẦN NHẤT\n"
            "   - Nhấn nút 'Find Driver'. Thuật toán sẽ quét toàn bộ\n"
            "     danh sách tài xế để chọn người có khoảng cách\n"
            "     (Euclidean) ngắn nhất tới khách hàng.\n\n"
            "👉 BƯỚC 3: XÁC NHẬN CHUYẾN ĐI\n"
            "   - Chọn tài xế theo nhu cầu của khách hàng.\n"
            "   - Kiểm tra Quãng đường và Giá tiền (12.000đ/km).\n"
            "   - Nhấn 'Confirm' để tạo mã TripID mới.\n\n"
            "👉 BƯỚC 4: ĐÁNH GIÁ (RATING)\n"
            "   - Sau mỗi chuyến, hãy nhập số sao (0-5).\n"
            "   - Hệ thống sẽ tự động tính lại điểm trung bình \n     cho tài xế.\n"
            "------------------------------------------\n"
            "💡 Lưu ý: Mọi dữ liệu sẽ được lưu tự động vào file CSV."
        )

        # Tận dụng result_var để hiển thị văn bản vào Text box
        self.result_var.set(guide_text)
        
        # Dùng lại result_box của bạn để có thanh cuộn (scrollbar) nếu text dài
        box = self._result_box(wrap)
        # Nút Đóng panel
        btn_close = tk.Button(wrap, text="Đã hiểu & Đóng", bg="#016B61", fg="white",
                              font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                              command=lambda: self._expand("Guide")) # Gọi lại hàm expand để toggle đóng
        btn_close.pack(pady=10, ipadx=20)
        
        return wrap

    def _build_about_panel(self, parent):
        wrap = self._panel_wrap(parent, "✨ Về dự án MinRide")
        about_text = (
            "MinRide Project - Phiên bản 1.0\n\n"
            "Hệ thống quản lý đặt xe thông minh tối ưu khoảng cách.\n"
            "Được hướng dẫn/ chỉ đạo bởi: ThS.Vũ Đình Bảo\n"
            "Phát triển bởi: Nhóm 9\n"
            "- Đỗ Thành Đạt (Nhóm trưởng)\n"
            "- Phan Nhật Vy\n"
            "- Trần Quyết Chiến\n"
            "- Lâm Huy Bách\n"
            "- Bùi Đức Duy\n"
            "- Lê Phạm Quang Khánh\n"
            "Công nghệ: Python, Tkinter, CSV Database.\n\n"
            "Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!"
        )
        self.result_var.set(about_text)
        self._result_box(wrap)

        # Nút Đóng panel
        btn_close = tk.Button(wrap, text="Đóng thông tin", bg="#1C1C1C", fg="white",
                              font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                              command=lambda: self._expand("About"))
        btn_close.pack(pady=10, ipadx=20)
        
        return wrap

    def draw_ui(self, event=None):
        cv = self.cv
        cv.delete("all")
        self.tile_items.clear()
        self.entry_window_id = None
        self.expand_window_id = None
        self.panel_frame = None

        w = cv.winfo_width()
        pad = 22

        TinhNang.Background(cv, "#80D7CB", "#C7E3DF") # #A1D6CF #FFFFFF

        cv.create_text(pad, 56, text="Booking",
                       anchor="w", font=("Segoe UI", 15, "bold"), fill="#1C1C1C")
        if self.logo_img:
            cv.create_image(w - pad, 56, image=self.logo_img, anchor="e")

        card_y1, card_y2 = 90, 230
        TinhNang.round_rect(cv, pad, card_y1, w - pad, card_y2, r=22, fill="white", outline="")
        # cv.tag_bind("<Button-1>", lambda e: self.entry.focus_set())\
        self.driver.load_from_csv()
        self.customer.load_from_csv()
        total_driver=self.driver.total_driver()
        total_customer=self.customer.total_customer()

        cv.create_text(pad + 20, card_y1,
                       text=(f'\n🚕 Tài xế đã sẵn sàng: {total_driver}\n📱 Tổng số khách hàng: {total_customer}\n💰 Đơn giá: 12.000 đồng/km'),
                       anchor="nw", font=("Segoe UI", 11, "bold"), fill="#1C1C1C")
        # tiles layout
        cols = 3
        gap = 12
        tile_h = 80
        start_y = card_y2 + 18
        tile_w = (w - 2*pad - gap*(cols-1)) // cols

        # panel sizing
        panel_h = 435
        panel_gap = 12
        
        # xác định tile nào đang expanded nằm ở row nào
        expanded_row = None
        if self.expanded_key:
            for i, (_, k) in enumerate(self.tiles):
                if k == self.expanded_key:
                    expanded_row = i // cols
                    break

        # vẽ tiles
        tile_positions = {}  # key -> (row, x1,y1,x2,y2)
        for i, (title, key) in enumerate(self.tiles):
            r = i // cols
            c = i % cols

            y_offset = 0
            if expanded_row is not None and r > expanded_row:
                y_offset = panel_h + panel_gap

            x1 = pad + c * (tile_w + gap)
            y1 = start_y + r * (tile_h + gap) + y_offset
            x2 = x1 + tile_w
            y2 = y1 + tile_h

            tile_positions[key] = (r, x1, y1, x2, y2)

            ttag = self._tile_tag(key)

            shadow_id = TinhNang.round_rect(
                cv, x1+2, y1+4, x2+2, y2+4,
                r=self.tile_radius,
                fill=self.tile_shadow_normal,
                outline="",
                tags=("tile", ttag)
            )
            rect_id = TinhNang.round_rect(
                cv, x1, y1, x2, y2,
                r=self.tile_radius,
                fill=self.tile_fill,
                outline="",
                tags=("tile", ttag)
            )
            text_id = cv.create_text((x1+x2)//2, (y1+y2)//2,
                                     text=title, font=("Segoe UI", 11),
                                     fill=self.tile_title_color,
                                     width=tile_w-20, tags=("tile", ttag))

            self.tile_items[key] = {
                "shadow_id": shadow_id, "rect_id": rect_id, "text_id": text_id,
                "all_ids": [shadow_id, rect_id, text_id], "pressed": False
            }

            cv.tag_bind(ttag, "<Enter>", lambda e, k=key: self._hover_in(k))
            cv.tag_bind(ttag, "<Leave>", lambda e, k=key: self._hover_out(k))
            cv.tag_bind(ttag, "<ButtonPress-1>", lambda e, k=key: self._press_in(k))
            cv.tag_bind(ttag, "<ButtonRelease-1>", lambda e, k=key: self._press_out(k))

        # vẽ panel ngay dưới hàng chứa tile expanded
        if self.expanded_key and expanded_row is not None:
            # panel nằm sau row expanded (ngay dưới hàng đó)
            panel_y1 = start_y + (expanded_row + 1) * (tile_h + gap)
            panel_y2 = panel_y1 + panel_h
            panel_x1, panel_x2 = pad, w - pad

            # card panel
            TinhNang.round_rect(cv, panel_x1, panel_y1, panel_x2, panel_y2,
                                r=22, fill="white", outline="", tags=("form",))

            # tạo frame nội dung panel theo key
            inner = tk.Frame(cv, bg="white")

            if self.expanded_key == "Book":
                content = self._build_list_panel(inner)
            elif self.expanded_key == "Guide":
                content = self._build_guide_panel(inner)
            elif self.expanded_key == "About":
                content = self._build_about_panel(inner)
            else:
                content = tk.Label(inner, text="(Chưa có panel)", bg="white")
                content.pack()
            
            content.pack(fill="both", expand=True)

            inner_pad = 16
            self.panel_frame = inner
            self.expand_window_id = cv.create_window(
                panel_x1 + inner_pad, panel_y1 + inner_pad,
                anchor="nw",
                window=inner,
                width=(panel_x2 - panel_x1) - 2*inner_pad,
                height=(panel_y2 - panel_y1) - 2*inner_pad,
                tags=("form",)
            )

    def refresh_data(self):
        """Hàm này sẽ được gọi mỗi khi người dùng nhấn vào tab Rides"""
        # 1. Bảo Manager đọc lại file CSV mới nhất
        self.customer.load_from_csv() 
        self.driver.load_from_csv()
        # 2. Vẽ lại toàn bộ giao diện với số liệu mới
        self.draw_ui() 