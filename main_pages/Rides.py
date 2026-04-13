import tkinter as tk
import TinhNang
from services.ride_repo import RideManager

# ================== RIDES PAGE ==================
class RidesPage(tk.Frame):
    def __init__(self, parent, logo_img):
        super().__init__(parent, bg="#B5E3D0")
        self.logo_img = logo_img

        self.cv = tk.Canvas(self, highlightthickness=0, bg="#B5E3D0")
        self.cv.pack(fill="both", expand=True)
        self.cv.bind("<Configure>", self.draw_ui)


        # ===== Tiles =====
        self.tiles = [
            ("List of Trips", "List"),
            ("Trips of Driver", "TripsD"),
            ("Trips of Customer", "TripsC")
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
        self.repo1=RideManager("data/trips.csv")

        # ===== shared UI state for panels =====
        self.msg_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="")

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

        box = tk.Text(frame, height=50, font=("Consolas", 10), 
                      bd=0, bg="#F3F9F8", yscrollcommand=scrollbar.set)
        box.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=box.yview)

        box.insert("end", self.result_var.get())
        box.config(state="disable") # Chỉ cho đọc, không cho sửa
        return box

    def tien_ich_info(self):
        result = self.repo1.get_full_info()
        if result!="No trips yet.":
            return f"#{result.tripID} # {result.timestamp} # {result.distance} km"
        return "No trips yet"

    # --List--
    def _build_list_panel(self, parent):
        wrap = self._panel_wrap(parent, "Danh sách các chuyến xe")
        
        btnrow = tk.Frame(wrap, bg="white")
        btnrow.pack(fill="x", pady=(10, 0))
        tk.Button(btnrow, text="Xem", bg="#016B61", fg="white", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=self._list_show).pack(side="right")
        tk.Button(btnrow, text="Hủy", bg="#E7F1EF", fg="#1C1C1C", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=lambda: self._expand("List")).pack(side="right")
        # kết quả
        self._result_box(wrap)
        return wrap
    
    def _list_show(self):
        out = []
        for c in self.repo1.trips:
            out.append(f'TripID: {c.tripID} |CustomerID: {c.customerID} |DriverID: {c.driverID} |Rating: {c.rate}\nTime: {c.timestamp} |Distance: {c.distance} km\nFare: {c.fare} đồng\n')
        self.result_var.set("\n".join(out) if out else "trống")
        self.msg_var.set(f"Đâ hiển thị danh sách các chuyến xe.")
        self.draw_ui()

    # --Trips by ID--
    def _build_trips_panel(self, parent, key):
        if key=="d":
            wrap = self._panel_wrap(parent, "Hiển thị chuyến xe theo ID tài xế")
        else:
            wrap = self._panel_wrap(parent, "Hiển thị chuyến xe theo ID khách hàng")
        self.search_d_var = tk.StringVar()
        label_text="ID tài xế:" if key=="d" else "ID khách hàng:"
        self._field(wrap, label_text, self.search_d_var)
        
        btn_row = tk.Frame(wrap, bg="white")
        btn_row.pack(fill="x", pady=(10, 5))
        
        # SỬA LỖI 1: Thêm lambda vào đây
        tk.Button(btn_row, text="Hiển thị", bg="#016B61", fg="white", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=lambda: self._show_list_by_ID(key)).pack(side="right")
        
        tk.Button(btn_row, text="Hủy", bg="#E7F1EF", fg="#1C1C1C", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=lambda: self._expand("TripsD" if key == "d" else "TripsC")).pack(side="right", padx=5)

        self._result_box(wrap)
        return wrap

    def _show_list_by_ID(self, key):
        d = self.search_d_var.get().strip()
        if not d:
            self.msg_var.set("Nhập ID để hiển thị.")
            self.draw_ui()
            return

        out = []
        d=int(d)
        data=self.repo1.trips
        for c in data:
            if key=="d":
                if c.driverID == d:
                    out.append(f'TripID: {c.tripID} |CustomerID: {c.customerID} |DriverID: {c.driverID} |Rating: {c.rate}\nTime: {c.timestamp} |Distance: {c.distance} km\nFare: {c.fare} đồng\n')
            else:
                if c.customerID == d:
                    out.append(f'TripID: {c.tripID} |CustomerID: {c.customerID} |DriverID: {c.driverID} |Rating: {c.rate}\nTime: {c.timestamp} |Distance: {c.distance} km\nFare: {c.fare} đồng\n')
        self.result_var.set("\n".join(out) if out else "")
        self.msg_var.set(f"Đã hiển thị kết quả." if out else "Không có kết quả.")
        self.draw_ui()

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

        cv.create_text(pad, 56, text="Rides",
                       anchor="w", font=("Segoe UI", 15, "bold"), fill="#1C1C1C")
        if self.logo_img:
            cv.create_image(w - pad, 56, image=self.logo_img, anchor="e")

        card_y1, card_y2 = 90, 230
        TinhNang.round_rect(cv, pad, card_y1, w - pad, card_y2, r=22, fill="white", outline="")
        # cv.tag_bind("<Button-1>", lambda e: self.entry.focus_set())\
        self.repo1.load_from_csv()

        info_text=self.tien_ich_info()
        total=len(self.repo1.trips)
        total_distance=self.repo1.get_total_distance()

        cv.create_text(pad + 20, card_y1,
                       text=(f'\n📊 Total Trips: {total}\n🧮 Total Distance: {total_distance} km\n🕓 Latest Trip: {info_text}'),
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

            if self.expanded_key == "List":
                content = self._build_list_panel(inner)
            elif self.expanded_key == "TripsD":
                content = self._build_trips_panel(inner, "d")
            elif self.expanded_key == "TripsC":
                content = self._build_trips_panel(inner, "c")
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
        self.repo1.load_from_csv() 
        
        # 2. Vẽ lại toàn bộ giao diện với số liệu mới
        self.draw_ui() 