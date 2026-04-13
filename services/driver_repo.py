from TinhNang import *
import csv
import copy
from pathlib import Path
import math

FILE = Path("data/drivers.csv")

def load_drivers():
    if not FILE.exists():
        return []
    with open(FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
    

class DriverManager:
    def __init__(self, csv_path="drivers.csv"):
        self.csv_path = csv_path
        self.drivers = []
        self.undo_stack = Stack()
        self.redo_stack = Stack()
        self.load_from_csv()  # ✅ đọc file khi mở app
    # ========= Sort Rating ===========
    # DECREASE
    def merge_arr_decrease(self, lst_drivers, l, m, r):
        # Tạo mảng con L và R bằng slicing
        # ds[l : m+1] lấy từ l đến m
        L = lst_drivers[l : m + 1]
        R = lst_drivers[m + 1 : r + 1]
        
        n1 = len(L)
        n2 = len(R)
        i = 0
        j = 0
        k = l
        
        while i < n1 and j < n2:
            # Sắp xếp giảm dần
            if L[i].rating >= R[j].rating:
                lst_drivers[k] = L[i]
                i += 1
            else:
                lst_drivers[k] = R[j]
                j += 1
            k += 1
            
        # Chép các phần tử còn lại (nếu có)
        while i < n1:
            lst_drivers[k] = L[i]
            i += 1
            k += 1
        while j < n2:
            lst_drivers[k] = R[j]
            j += 1
            k += 1

    def merge_sort_decrease(self, lst_drivers, l, r):
        if l < r:
            # Dùng // để chia lấy phần nguyên trong Python
            m = l + (r - l) // 2
            self.merge_sort_decrease(lst_drivers, l, m)
            self.merge_sort_decrease(lst_drivers, m + 1, r)
            self.merge_arr_decrease(lst_drivers, l, m, r)

        return lst_drivers

    def sort_lst_Rating_Decrease(self):
        result=self.merge_sort_decrease(self.drivers,0, len(self.drivers)-1)
        return result
    
    # INCREASE
    def merge_arr_increase(self, lst_drivers, l, m, r):
        # Tạo mảng con L và R bằng slicing
        # ds[l : m+1] lấy từ l đến m
        L = lst_drivers[l : m + 1]
        R = lst_drivers[m + 1 : r + 1]
        
        n1 = len(L)
        n2 = len(R)
        i = 0
        j = 0
        k = l
        
        while i < n1 and j < n2:
            # Sắp xếp tăng dần
            if L[i].rating <= R[j].rating:
                lst_drivers[k] = L[i]
                i += 1
            else:
                lst_drivers[k] = R[j]
                j += 1
            k += 1
            
        # Chép các phần tử còn lại (nếu có)
        while i < n1:
            lst_drivers[k] = L[i]
            i += 1
            k += 1
        while j < n2:
            lst_drivers[k] = R[j]
            j += 1
            k += 1

    def merge_sort_increase(self, lst_drivers, l, r):
        if l < r:
            # Dùng // để chia lấy phần nguyên trong Python
            m = l + (r - l) // 2
            self.merge_sort_increase(lst_drivers, l, m)
            self.merge_sort_increase(lst_drivers, m + 1, r)
            self.merge_arr_increase(lst_drivers, l, m, r)

        return lst_drivers

    def sort_lst_Rating_Increase(self):
        result=self.merge_sort_increase(self.drivers,0, len(self.drivers)-1)
        return result
    # ========= Sort ID ===========
    def sort_lst_ID(self):
        quick_sort_hoare(self.drivers, 0, len(self.drivers)-1)
        self.save_to_csv()
    # ========= CSV =========
    def load_from_csv(self):
        self.drivers = []
        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # đổi kiểu dữ liệu nếu cần
                    c = Driver(
                        id=int(row["id"]),
                        name=row["name"],
                        rating=float(row["rating"]),
                        tripCount=int(row["tripcount"]),
                        x=float(row["x"]),
                        y=float(row["y"]),
                    )
                    self.drivers.append(c)
            return self.drivers
        except FileNotFoundError:
            # chưa có file thì thôi
            pass
    
    def save_to_csv(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "rating", "tripcount", "x", "y"])
            writer.writeheader()
            for c in self.drivers:
                # Sửa đổi tất cả truy cập key-based (c["..."]) thành attribute-based (c.tên_thuộc_tính)
                # Dòng lỗi là do c không có key ["rating"], mà chỉ có thuộc tính .rating
                writer.writerow({
                    "id": c.id,          # SỬA: c["id"] -> c.id
                    "name": c.name,      # SỬA: c["name"] -> c.name
                    "rating": c.rating,  # SỬA: c["rating"] -> c.rating (Đây là dòng gây lỗi)
                    "tripcount": c.tripCount, # CHÚ Ý: Đã sửa c["rating"] -> c.tripCount (Bạn gán nhầm rating cho tripcount trong code cũ)
                    "x": c.x,            # SỬA: c["x"] -> c.x
                    "y": c.y             # SỬA: c["y"] -> c.y
                })
    # ========= CRUD =========
    def get_id_lastDriver(self):
        return self.drivers[-1].id
    def _add_driver(self, driver: Driver):
        # check trùng ID
        """for d in self.drivers:
            if d.id == driver.id:
                return False"""
        
        # lưu state trước khi thay đổi
        self.undo_stack.push(copy.deepcopy(self.drivers))
        self.redo_stack = Stack()
        #thêm tài xế
        self.drivers.append(driver)

        self.save_to_csv() #ghi file
        return True
    #ham cập nhật tài xế
    def _update_driver(self, upd_d:Driver):
        for d in self.drivers:
            if d.id == upd_d.id:
                # 2. Lưu trạng thái trước khi sửa (UNDO)
                self.undo_stack.push(copy.deepcopy(self.drivers))
                self.redo_stack = Stack()

                # 3. Update từng field
                d.name=upd_d.name
                d.rating=upd_d.rating
                d.tripCount=upd_d.tripCount
                d.x=upd_d.x
                d.y=upd_d.y

                self.save_to_csv()
                return 

    #xóa tài xế
    def _delete_driver(self, id):
        original_length = len(self.drivers)
        # Lưu trạng thái trước khi thay đổi
        self.undo_stack.push(copy.deepcopy(self.drivers))
        self.redo_stack = Stack()
        
        # Tạo danh sách mới chỉ bao gồm các driver có ID khác với ID cần xóa
        self.drivers = [d for d in self.drivers if d.id != id]

        # Kiểm tra xem có phần tử nào bị xóa không
        if len(self.drivers) < original_length:
            self.save_to_csv()
            return True
        else:
            # Nếu không tìm thấy, hủy bỏ thao tác undo vừa push
            self.undo_stack.pop() 
            return False
    
    # ========= UNDO / REDO =========
    def undo(self):
        try:
            self.redo_stack.push(copy.deepcopy(self.drivers))
            self.drivers = self.undo_stack.pop()
            self.save_to_csv()
            return True
        except NoActionToUndoException as e:
            print(e)
            return False
    
    def total_driver(self):
        if not self.drivers:
            return 0
        return len(self.drivers)
    
    import math

    def find_all_drivers_in_radius(self, cx, cy, R):
        available_drivers = []
        for drv in self.drivers:
            dist = math.sqrt((drv.x - cx)**2 + (drv.y - cy)**2)
            if dist <= R:
                # Lưu cả object tài xế và khoảng cách vào list
                available_drivers.append((drv, dist))
        
        # Sắp xếp danh sách theo khoảng cách tăng dần
        available_drivers.sort(key=lambda x: x[1])
        return available_drivers
    
    def save_all(self):
        try:
            with open(self.csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id", "name", "rating", "tripcount","x", "y"]) # Header
                for d in self.drivers:
                    writer.writerow([int(d.id), d.name, float(d.rating), int (d.tripCount),round(float(d.x),1), round(float(d.y),1)])
            return True
        except Exception as e:
            print(f"Lỗi cập nhật file: {e}")
            return False

    def update_driver_pos(self, did, nx, ny, rate):
        for d in self.drivers:
            if int(d.id) == int(did):
                d.x, d.y = float(nx), float(ny)
                d.rating=round((d.rating*d.tripCount+rate)/(d.tripCount + 1),2)
                d.tripCount+=1
                return self.save_all()
        return False