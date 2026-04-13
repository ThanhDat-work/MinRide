import os, sys
from abc import ABC
# ABC, abstractmethod: dùng để tạo abstract class (OOP – Abstraction)

# ======= BACKGROUND ======= 
def Background(canvas, color_top, color_bottom):
    canvas.delete("gradient")

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    r1, g1, b1 = canvas.winfo_rgb(color_top)
    r2, g2, b2 = canvas.winfo_rgb(color_bottom)

    r_ratio = (r2 - r1) / h
    g_ratio = (g2 - g1) / h
    b_ratio = (b2 - b1) / h

    for i in range(h):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))

        color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"

        canvas.create_line(0, i, w, i, fill=color, tags=("gradient",))


# ================== PATH UTILS (fix lỗi file ảnh) ==================
def resource_path(rel_path: str) -> str:
    try:
        base = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel_path)

ASSET_NAME = "MR.png"          # icon cửa sổ + logo header
ASSET_PATH = resource_path(ASSET_NAME)
# ================== UTILS ==================
def round_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):
    points = [
        x1+r, y1, x2-r, y1, x2, y1,
        x2, y1+r, x2, y2-r, x2, y2,
        x2-r, y2, x1+r, y2, x1, y2,
        x1, y2-r, x1, y1+r, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class NoActionToUndoException(Exception):
    """Lỗi khi undo nhưng stack rỗng"""
    pass

# ================================
# ABSTRACT CLASS: ENTITY
# ================================

class Entity(ABC):
    """
    Lớp trừu tượng Entity.
    Mọi thực thể chính đều phải có id và name.
    """
    def __init__(self, id, name):
        self.id = id
        self.name = name

# ================================
# MIX-IN: LOCATION
# ================================

class Location:
    """
    Mix-in Location: cung cấp tọa độ (x, y).
    Thể hiện đa kế thừa.
    """
    def __init__(self, x, y):
        x=float(x)
        y=float(y)
        
        self.x = x
        self.y = y

class Driver(Entity, Location):
    """Driver kế thừa Entity và Location (đa kế thừa)"""

    def __init__(self, id, name, rating, tripCount, x, y):
        tripCount=int(tripCount)
        rating=float(rating)
        Entity.__init__(self, id, name)
        Location.__init__(self, x, y)
        self.rating = rating
        self.tripCount = tripCount

# ================================
# CUSTOMER
# ================================

class Customer(Entity, Location):
    """
    Customer kế thừa:
    - Entity (id, name)
    - Location (x, y)
    """
    def __init__(self, id, name, district, x, y):
        Entity.__init__(self, id, name)
        Location.__init__(self, x, y)
        self.district = district
# ================================
# RIDE
# ================================

class Ride:
    """
    Ride đại diện cho một chuyến đi.
    Không kế thừa Entity vì không phải thực thể chung.
    """
    def __init__(self, tripID, customerID, driverID, timestamp, distance, fare, rate):
        self.tripID = tripID
        self.customerID = customerID
        self.driverID = driverID
        self.timestamp=timestamp
        self.distance = distance
        self.fare = fare
        self.rate=rate

# ========= Sort ========
def hoare_partition(lst_customers, l, r):
    # Chọn pivot là giá trị giá của phần tử đầu tiên
    pivot_id = lst_customers[l].id
    i = l - 1
    j = r + 1
    
    while True:
        # Tương đương do { i++; } while (ds[i] > pivot)
        while True:
            i += 1
            if lst_customers[i].id >= pivot_id:
                break
        
        # Tương đương do { j--; } while (ds[j] < pivot)
        while True:
            j -= 1
            if lst_customers[j].id <= pivot_id:
                break
        
        if i >= j:
            return j
            
        # Sử dụng cách swap đặc trưng của Python
        lst_customers[i], lst_customers[j] = lst_customers[j], lst_customers[i]

def quick_sort_hoare(lst_customers, l, r):
    if l < r:
        p = hoare_partition(lst_customers, l, r)
        quick_sort_hoare(lst_customers, l, p)
        quick_sort_hoare(lst_customers, p + 1, r)

class Stack:
    #chứa state
    def __init__(self):
        self.stack = []
    #hàm thêm state vào stack
    def push(self, state):
        self.stack.append(state)
    #hàm lấy state cuối cùng ra khỏi stack
    def pop(self):
        if not self.stack:
            raise NoActionToUndoException
        return self.stack.pop()
