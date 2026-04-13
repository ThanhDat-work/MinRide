import tkinter as tk
from services.driver_repo import DriverManager
import TinhNang
from TinhNang import Driver
# ================== DRIVERS PAGE ==================
class DriversPage(tk.Frame):
    def __init__(self, parent, logo_img, csv_path="data/drivers.csv"):
        super().__init__(parent, bg="#B5E3D0")
        self.logo_img = logo_img

        self.cv = tk.Canvas(self, highlightthickness=0, bg="#B5E3D0")
        self.cv.pack(fill="both", expand=True)
        # Khởi tạo sẵn các biến cho Update ở đây
        self.upd_id = tk.StringVar()
        self.upd_name = tk.StringVar()
        self.upd_x = tk.StringVar()
        self.upd_y = tk.StringVar()
        # ===== Search Entry (header search) =====
        self.search_bg = "#F3F9F8"
        self.is_focused = False
        self.border_active = "#016B61"
        self.tile_items = {}       
        self.expanded_key = None
        self.expand_window_id = None
        self.panel_frame = None
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.after(0, self.draw_ui))

        self.entry = tk.Entry(
            self.cv, textvariable=self.search_var,
            bd=0, relief="flat", highlightthickness=0,
            font=("Segoe UI", 11),
            fg="#1C1C1C", bg=self.search_bg,
            insertbackground="#016B61",
            selectbackground="#CFEDEA"
        )
        self.placeholder = "Bạn muốn tìm kiếm gì?"
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#7A9E9A")
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Return>", lambda e: self._do_header_search())

        self.entry_window_id = None

        # click ngoài form/search -> blur
        self.cv.bind("<Button-1>", self._click_outside, add=True)
        self.cv.bind("<Configure>", self.draw_ui)

        # ===== Tiles =====
        self.tiles = [
            ("Top Drivers", "TopK"),
            ("Add Drivers", "Add"),
            ("Update", "Update"),
            ("Delete", "Delete"),
            ("Search by ID", "Search"),
            ("Sort by Rating", "Rating"),
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
        self.repo1=DriverManager("data/drivers.csv")
        self.repo1.sort_lst_ID()
        try:
            self.next_id= self.repo1.get_id_lastDriver()+1
        except:
            self.next_id=1

        # ===== shared UI state for panels =====
        self.msg_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="")
    
    # ================= HEADER SEARCH =================
    def _on_focus_in(self, e=None):
        self.is_focused = True
        if self.entry.get().strip() == self.placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg="#1C1C1C")
        self.draw_ui()

    def _on_focus_out(self, e=None):
        self.is_focused = False
        if self.entry.get().strip() == "":
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#7A9E9A")
        self.draw_ui()

    def _do_header_search(self):
        q = self.entry.get().strip()
        if not q or q == self.placeholder:
            return
        # mở panel Search và điền q
        self._expand("Search")
        # nếu panel đang mở Search, set input của panel
        if hasattr(self, "search_q_var"):
            self.search_q_var.set(q)
            self._search_drivers()

    def _click_outside(self, event):
        current = self.cv.find_withtag("current")
        if current:
            tags = self.cv.gettags(current[0])
            if "searchbar" in tags or "tile" in tags or "form" in tags:
                return
        self.cv.focus_set()
        self.entry.selection_clear()

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
        self.temp=self.repo1.load_from_csv()
        for c in self.temp:
            if c.id == cid:
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

    # ---- TopK ----
    def _build_topk_panel(self, parent):
        wrap = self._panel_wrap(parent, "Top K tài xế (đầu/cuối)")
        self.topk_k_var = tk.StringVar(value="5")
        self.topk_pos_var = tk.StringVar(value="Top")  # Top / Bottom

        self._field(wrap, "K", self.topk_k_var)

        opt_row = tk.Frame(wrap, bg="white")
        opt_row.pack(fill="x", pady=6)
        tk.Label(opt_row, text="Vị trí", bg="white", fg="#4A4A4A",
                 font=("Segoe UI", 10)).pack(side="left")
        tk.OptionMenu(opt_row, self.topk_pos_var, "Top", "Bottom").pack(side="right")

        btn = tk.Button(wrap, text="Hiển thị", bg="#016B61", fg="white",
                        bd=0, font=("Segoe UI", 10, "bold"),
                        command=self._topk_show)
        btn.pack(anchor="e", pady=(10, 0))

        self._result_box(wrap)
        return wrap

    def _topk_show(self):
        data=self.repo1.load_from_csv()
        try:
            k = int(self.topk_k_var.get().strip())
            if k <= 0 or k > len(data): raise ValueError
        except ValueError:
            self.result_var.set("")
            self.msg_var.set("Error: Invalid Input Error/Index Out of Range Error).")
            self.draw_ui()
            return

        if self.topk_pos_var.get() == "Bottom":
            pick = data[-k:]
        else:
            pick = data[:k]

        out = []
        for c in pick:
            out.append(f'ID: {c.id} | Tên: {c.name} | Đánh giá: {c.rating} \nTrip Count: {c.tripCount} | Tọa độ: ({c.x},{c.y})\n')
        self.result_var.set("\n".join(out) if out else "(trống)")
        self.msg_var.set(f"Đã hiển thị {len(pick)} tài xế.")
        self.draw_ui()

    # ---- Add ----
    def _build_add_panel(self, parent):
        wrap = self._panel_wrap(parent, "Thêm tài xế")
        self.add_name = tk.StringVar()
        self.add_x = tk.StringVar()
        self.add_y = tk.StringVar()

        self._field(wrap, "Họ tên:", self.add_name)
        self._field(wrap, "Tọa độ x:", self.add_x)
        self._field(wrap, "Tọa độ y:", self.add_y)

        btnrow = tk.Frame(wrap, bg="white")
        btnrow.pack(fill="x", pady=(10, 0))
        tk.Button(btnrow, text="Lưu", bg="#016B61", fg="white", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=self._add_submit).pack(side="right", padx=(8, 0))
        # Nút Hoàn tác (Undo) - Mới thêm
        tk.Button(btnrow, text="Hoàn tác", bg="#016B61", fg="white", bd=0,
                font=("Segoe UI", 10,"bold"),
                command=self._undo_add).pack(side="right", padx=(8, 0))
        tk.Button(btnrow, text="Hủy", bg="#E7F1EF", fg="#1C1C1C", bd=0,
                  font=("Segoe UI", 10),
                  command=lambda: self._expand("Add")).pack(side="right")

        return wrap

    def _add_submit(self):
        name = self.add_name.get().strip()
        x = float(self.add_x.get().strip())
        y = float(self.add_y.get().strip())
        if not name or not x or not y:
            self.msg_var.set("Vui lòng nhập ít nhất: Họ tên, Tọa độ x, Tọa độ y.")
            self.draw_ui()
            return
       
        driver = Driver(
            id=self.next_id,
            name=name,
            rating=5,
            tripCount=0,
            x=x,
            y=y
        )

        self.repo1._add_driver(driver)
        self.next_id+=1
        self.msg_var.set(f"Đã thêm tài xế ID {self.next_id - 1}.")
        # reset form
        self.add_name.set("")
        self.add_x.set("")
        self.add_y.set("")
        
        self.draw_ui()

    def _undo_add(self):
        if self.repo1.undo():
            # Quan trọng: Giảm next_id xuống vì vừa xóa đi 1 người vừa thêm
            if self.next_id > 1:
                self.next_id -= 1
                
            self.msg_var.set("Đã hoàn tác!")
        else:
            self.msg_var.set("Không thể hoàn tác.")
        
        self.draw_ui()
    # ---- Update ----
    def _build_update_panel(self, parent):
        wrap = self._panel_wrap(parent, "Cập nhật tài xế theo ID")
        
        self._field(wrap, "ID", self.upd_id)
        btn_row = tk.Frame(wrap, bg="white")
        btn_row.pack(fill="x", pady=(10, 0))
        load_row = tk.Frame(wrap, bg="white")
        load_row.pack(fill="x", pady=(6, 0))
        tk.Button(load_row, text="Tải thông tin", bg="#E7F1EF", fg="#1C1C1C",
                  bd=0, font=("Segoe UI", 10),
                  command=self._update_load).pack(anchor="e")

        self._field(wrap, "Họ tên", self.upd_name)
        self._field(wrap, "Tọa độ x", self.upd_x)
        self._field(wrap, "Tọa độ y", self.upd_y)

        # Nút Hoàn tác
        tk.Button(btn_row, text="Hoàn tác", bg="#016B61", fg="white", bd=0,
          font=("Segoe UI", 10, "bold"),
          command=self._undo_action).pack(side="left")
        tk.Button(btn_row, text="Cập nhật", bg="#016B61", fg="white", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=self._update_submit).pack(side="right")
        return wrap

    def _update_load(self):
        try:
            cid = int(self.upd_id.get().strip())
        except:
            self.msg_var.set("ID không hợp lệ.")
            self.draw_ui()
            return
        c = self._find_by_id(cid)
        if not c:
            self.upd_name.set("")
            self.upd_x.set("")
            self.upd_y.set("")
            self.msg_var.set("Không tìm thấy tài xế.")
            self.draw_ui()
            return
        self.upd_name.set(c.name)
        self.upd_x.set(c.x)
        self.upd_y.set(c.y)
        self.msg_var.set(f"Đã tải thông tin ID {cid}.")

    def _update_submit(self):
        try:
            cid = int(self.upd_id.get().strip())
        except:
            self.msg_var.set("ID không hợp lệ.")
            self.draw_ui()
            return
        old_c = self._find_by_id(cid)
        if not old_c:
            self.msg_var.set("Không tìm thấy tài xế.")
            self.draw_ui()
            return
        # cập nhật (cho phép bỏ trống -> giữ nguyên)
        new_name = self.upd_name.get().strip() or old_c.name
        
        x_val = self.upd_x.get().strip()
        new_x = float(x_val) if x_val else old_c.x
        
        y_val = self.upd_y.get().strip()
        new_y = float(y_val) if y_val else old_c.y
        
        temp_driver = Driver(
            id=cid,
            name=new_name,
            rating=old_c.rating,
            tripCount=old_c.tripCount,
            x=new_x,
            y=new_y
        )
        self.repo1._update_driver(temp_driver)
        self.msg_var.set(f"Đã cập nhật ID {cid}.")
        self.draw_ui()

    def _undo_action(self):
        # Gọi hàm undo từ DriverManager
        if self.repo1.undo():
            self.msg_var.set("Đã hoàn tác!")
            # Sau khi hoàn tác, có thể cần tải lại thông tin lên ô nhập liệu
            self._update_load() 
        else:
            self.msg_var.set("Không thể hoàn tác.")
        self.draw_ui()
    # ---- Delete ----
    def _build_delete_panel(self, parent):
        wrap = self._panel_wrap(parent, "Xóa tài xế theo ID")
        self.del_id = tk.StringVar()
        self._field(wrap, "ID", self.del_id)

        # Hàng chứa các nút bấm
        btn_row = tk.Frame(wrap, bg="white")
        btn_row.pack(fill="x", pady=(10, 0))

        # Nút Hoàn tác (nằm bên trái)
        tk.Button(btn_row, text="Hoàn tác", bg="#016B61", fg="white", bd=0,
                font=("Segoe UI", 10, "bold"),
                command=self._undo_delete).pack(side="left")

        # Nút Xóa (nằm bên phải)
        tk.Button(btn_row, text="Xóa", bg="#D64545", fg="white", bd=0,
                font=("Segoe UI", 10, "bold"),
                command=self._delete_submit).pack(side="right")
        return wrap

    def _delete_submit(self):
        try:
            cid = int(self.del_id.get().strip())
        except:
            self.msg_var.set("ID không hợp lệ.")
            self.draw_ui()
            return
        
        ok=self.repo1._delete_driver(cid)
        if ok:
            self.msg_var.set(f"Đã xóa tài xế ID {cid}. Bạn có thể Hoàn tác.")
            self.del_id.set("") # Xóa sạch ô nhập sau khi xóa thành công
        else:
            self.msg_var.set("Không tìm thấy ID để xóa.")
            
        self.draw_ui()

    def _undo_delete(self):
        # Gọi lệnh hoàn tác từ DriverManager
        if self.repo1.undo():
            self.msg_var.set("Đã hoàn tác!")
        else:
            self.msg_var.set("Không thể hoàn tác.")
        
        self.draw_ui()

    # ---- Search ----
    def _build_search_panel(self, parent):
        wrap = self._panel_wrap(parent, "Tìm kiếm tài xế (Tên hoặc ID)")
        self.search_q_var = tk.StringVar()
        self._field(wrap, "Từ khóa (Tên/ID)", self.search_q_var)

        tk.Button(wrap, text="Tìm", bg="#016B61", fg="white", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=self._search_drivers).pack(anchor="e", pady=(10, 0))

        self._result_box(wrap)
        return wrap

    def _search_drivers(self):
        q = self.search_q_var.get().strip()
        if not q:
            self.msg_var.set("Nhập tên hoặc ID để tìm.")
            self.draw_ui()
            return

        out = []
        # thử parse ID
        cid = None
        try:
            cid = int(q)
        except:
            cid = None

        data=self.repo1.load_from_csv()
        for c in data:
            if cid is not None:
                if c.id == cid:
                    out.append(f'ID: {c.id} | Tên: {c.name} | Đánh giá: {c.rating} \nTrip Count: {c.tripCount} | Tọa độ: ({c.x},{c.y})\n')
            else:
                if q.lower() in c.name.lower():
                    out.append(f'ID: {c.id} | Tên: {c.name} | Đánh giá: {c.rating} \nTrip Count: {c.tripCount} | Tọa độ: ({c.x},{c.y})\n')

        self.result_var.set("\n".join(out) if out else "")
        self.msg_var.set(f"Tìm thấy {0 if out==[''] else len(out)} kết quả." if out else "Không có kết quả.")
        self.draw_ui()

    # ---- Rating ----
    def _build_rating_panel(self, parent):
        wrap = self._panel_wrap(parent, "Sắp xếp theo đánh giá")
        opt_row = tk.Frame(wrap, bg="white")
        opt_row.pack(fill="x", pady=6)
        tk.Label(opt_row, text="Theo:", bg="white", fg="#4A4A4A",
                 font=("Segoe UI", 10)).pack(side="left")
        self.rating_pos_var = tk.StringVar(value="Decrease")
        tk.OptionMenu(opt_row, self.rating_pos_var, "Decrease", "Increase").pack(side="right")
        btnrow = tk.Frame(wrap, bg="white")
        btnrow.pack(fill="x", pady=(10, 0))
        tk.Button(btnrow, text="Xem", bg="#016B61", fg="white", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  command=self._rating_show).pack(side="right")

        # kết quả
        self._result_box(wrap)
        return wrap

    def _rating_show(self):
        if self.rating_pos_var.get() == "Increase":
            res=self.repo1.sort_lst_Rating_Increase()
        else:
            res=self.repo1.sort_lst_Rating_Decrease()
        out = []
        for c in res:
            out.append(f'ID: {c.id} | Tên: {c.name} | Đánh giá: {c.rating} \nTrip Count: {c.tripCount} | Tọa độ: ({c.x},{c.y})\n')
        self.result_var.set("\n".join(out) if out else "trống")
        self.msg_var.set(f"Đâ hiển thị danh sách theo đánh giá.")
        self.draw_ui()

    # ================== DRAW UI ==================
    def draw_ui(self, event=None):
        cv = self.cv
        cv.delete("all")
        self.tile_items.clear()
        self.entry_window_id = None
        self.expand_window_id = None
        self.panel_frame = None

        w = cv.winfo_width()
        pad = 22

        # background
        TinhNang.Background(cv, "#80D7CB", "#C7E3DF") # #A1D6CF #FFFFFF

        # header
        cv.create_text(pad, 56, text="Drivers",
                       anchor="w", font=("Segoe UI", 15, "bold"), fill="#1C1C1C")
        if self.logo_img:
            cv.create_image(w - pad, 56, image=self.logo_img, anchor="e")

        # search card
        card_y1, card_y2 = 90, 230
        TinhNang.round_rect(cv, pad, card_y1, w - pad, card_y2, r=22, fill="white", outline="")

        # search bar
        search_x1 = pad + 16
        search_x2 = w - pad - 16
        search_y1 = 110
        search_y2 = search_y1 + 44
        radius = (search_y2 - search_y1) // 2

        TinhNang.round_rect(
            cv, search_x1, search_y1, search_x2, search_y2,
            r=radius,
            fill=self.search_bg,
            outline=self.border_active if self.is_focused else "",
            width=2 if self.is_focused else 0,
            tags=("searchbar",)
        )
        cv.create_text(search_x1 + 22, (search_y1 + search_y2)//2,
                       text="🔍", font=("Segoe UI Emoji", 14),
                       fill="#016B61", tags=("searchbar",))

        entry_x = search_x1 + 44
        entry_y = (search_y1 + search_y2)//2
        entry_w = (search_x2 - entry_x) - 18
        self.entry_window_id = cv.create_window(entry_x, entry_y, window=self.entry,
                                                anchor="w", width=entry_w, height=24)
        cv.tag_bind("searchbar", "<Button-1>", lambda e: self.entry.focus_set())

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

            if self.expanded_key == "TopK":
                content = self._build_topk_panel(inner)
            elif self.expanded_key == "Add":
                content = self._build_add_panel(inner)
            elif self.expanded_key == "Update":
                content = self._build_update_panel(inner)
            elif self.expanded_key == "Delete":
                content = self._build_delete_panel(inner)
            elif self.expanded_key == "Search":
                content = self._build_search_panel(inner)
            elif self.expanded_key == "Rating":
                content = self._build_rating_panel(inner)
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