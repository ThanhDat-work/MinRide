from TinhNang import *
import csv
import copy

from pathlib import Path

FILE = Path("data/customers.csv")

def load_customers():
    if not FILE.exists():
        return []
    with open(FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
class CustomerManager:
    def __init__(self, csv_path="customers.csv"):
        self.csv_path = csv_path
        self.customers = []
        self.undo_stack = Stack()
        self.redo_stack = Stack()
        self.load_from_csv()  # ✅ đọc file khi mở app

    def sort_lst_ID(self):
        quick_sort_hoare(self.customers, 0, len(self.customers)-1)
        self.save_to_csv()
    # ========= CSV =========
    def load_from_csv(self):
        self.customers = []
        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # đổi kiểu dữ liệu nếu cần
                    c = Customer(
                        id=int(row["id"]),
                        name=row["name"],
                        district=row["district"],
                        x=float(row["x"]),
                        y=float(row["y"]),
                    )
                    self.customers.append(c)
            return self.customers
        except FileNotFoundError:
            # chưa có file thì thôi
            pass

    def save_to_csv(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "district", "x", "y"])
            writer.writeheader()
            for c in self.customers:
                writer.writerow({
                    "id": c.id,
                    "name": c.name,
                    "district": c.district,
                    "x": c.x,
                    "y": c.y
                })

    # ========= CRUD =========
    def get_id_lastCustomer(self):
        return self.customers[-1].id
    
    def add_customer(self, customer: Customer):
        """for c in self.customers:
            if c.id == customer.id:
                return False"""

        self.undo_stack.push(copy.deepcopy(self.customers))
        self.redo_stack = Stack()  # thao tác mới -> clear redo
        self.customers.append(customer)

        self.save_to_csv()  # ghi file
        return True

    def update_customer(self, upd_c:Customer):

        for c in self.customers:
            if c.id == upd_c.id:
                self.undo_stack.push(copy.deepcopy(self.customers))
                self.redo_stack = Stack()

                c.name=upd_c.name
                c.district=upd_c.district
                c.x=upd_c.x
                c.y=upd_c.y

                self.save_to_csv()
                return

    def delete_customer(self, id):
        original_length = len(self.customers)
        # Lưu trạng thái trước khi thay đổi
        self.undo_stack.push(copy.deepcopy(self.customers))
        self.redo_stack = Stack()
        
        # Tạo danh sách mới chỉ bao gồm các driver có ID khác với ID cần xóa
        self.customers = [d for d in self.customers if d.id != id]

        # Kiểm tra xem có phần tử nào bị xóa không
        if len(self.customers) < original_length:
            self.save_to_csv()
            return True
        else:
            # Nếu không tìm thấy, hủy bỏ thao tác undo vừa push
            self.undo_stack.pop() 
            return False

    # ========= UNDO / REDO =========
    def undo(self):
        try:
            self.redo_stack.push(copy.deepcopy(self.customers))
            self.customers = self.undo_stack.pop()
            self.save_to_csv()
            return True
        except NoActionToUndoException as e:
            print(e)
            return False

    def redo(self):
        try:
            self.undo_stack.push(copy.deepcopy(self.customers))
            self.customers = self.redo_stack.pop()
            self.save_to_csv()
            return True
        except Exception as e:
            print(e)
            return False

    def total_customer(self):
        if not self.customers:
            return 0
        return len(self.customers)
    
    def find_customer_by_ID(self, cid):
        for c in self.customers:
            if c.id==cid:
                return c
        return None
    
    # Ví dụ trong DriverManager (CustomerManager làm tương tự chỉ đổi tên list)
    def save_all(self):
        try:
            with open(self.csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id", "name", "district", "x", "y"]) # Header
                for d in self.customers:
                    writer.writerow([int(d.id), d.name, d.district, round(float(d.x),1), round(float(d.y),1)])
            return True
        except Exception as e:
            print(f"Lỗi cập nhật file: {e}")
            return False

    def update_customer_pos(self, did, nx, ny):
        for d in self.customers:
            if int(d.id) == int(did):
                d.x, d.y = round(float(nx),1), round(float(ny),1)
                return self.save_all()