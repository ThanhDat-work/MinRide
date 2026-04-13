from TinhNang import *
import csv
from pathlib import Path
import datetime
import random
import os

FILE = Path("data/trips.csv")

def load_trips():
    if not FILE.exists():
        return []
    with open(FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

class RideManager:
    def __init__(self, csv_path="trips.csv"):
        self.csv_path = csv_path
        self.trips = []
        self.load_from_csv()  # ✅ đọc file khi mở app

    # ========= CSV =========
    def load_from_csv(self):
        self.trips = []
        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # đổi kiểu dữ liệu nếu cần
                    c = Ride(
                        tripID=int(row["tripID"]),
                        customerID=int(row["customerID"]),
                        driverID=int(row["driverID"]),
                        timestamp=row["timestamp"],
                        distance=float(row["distance"]),
                        fare=float(row["fare"]),
                        rate=float(row["rate"])
                    )
                    self.trips.append(c)
            return self.trips
        except FileNotFoundError:
            # chưa có file thì thôi
            pass
    
    def save_all_to_csv(self):
        """Ghi đè toàn bộ danh sách trips hiện có trong RAM xuống file CSV"""
        try:
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                # Định nghĩa các cột (Header) đúng với file cũ của bạn
                fieldnames = ["tripID", "customerID", "driverID", "timestamp", "distance", "fare", "rate"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for t in self.trips:
                    writer.writerow({
                        "tripID": t.tripID,
                        "customerID": t.customerID,
                        "driverID": t.driverID,
                        "timestamp": t.timestamp,
                        "distance": t.distance,
                        "fare": t.fare,
                        "rate": t.rate
                    })
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False

    def get_full_info(self):
        if not self.trips:
            return "No trips yet."
        return self.trips[-1]
    
    def get_total_distance(self):
        if not self.trips:
            return 0
        sum=0
        for c in self.trips:
            sum+=c.distance
        return round(sum,2)

    def add_ride(self, ride_obj):
        """
        Tham số: ride_obj là một đối tượng của class Ride (từ TinhNang.py)
        """
        # 1. Thêm vào danh sách tạm thời trong bộ nhớ
        self.trips.append(ride_obj)
        
        # 2. Ghi thêm vào file CSV (Append mode)
        # Kiểm tra file có tồn tại chưa để ghi Header nếu cần
        file_exists = os.path.isfile(self.csv_path)
        
        try:
            with open(self.csv_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Nếu file mới hoàn toàn, ghi tiêu đề cột trước
                if not file_exists or os.stat(self.csv_path).st_size == 0:
                    writer.writerow(["tripID", "customerID", "driverID", "distance", "fare", "rate"])
                
                # Ghi dữ liệu chuyến đi
                writer.writerow([
                    int(ride_obj.tripID),
                    int(ride_obj.customerID),
                    int(ride_obj.driverID),
                    ride_obj.timestamp,
                    round(float(ride_obj.distance), 2),
                    int(ride_obj.fare),
                    int(ride_obj.rate)
                ])
            return True
        except Exception as e:
            print(f"Lỗi khi ghi file CSV: {e}")
            return False

    def generate_new_id(self):
        """Hàm hỗ trợ tạo mã chuyến đi tự động (Tùy chọn)"""
        if not self.trips:
            return 1001
        # Lấy ID lớn nhất hiện tại + 1
        return max(int(r.tripID) for r in self.trips) + 1
    
    def generate_logical_time(self):
        # Lấy thời gian chuyến cuối cùng trong danh sách
        if not self.trips:
            return datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        
        # Giả sử trong file CSV cột cuối là time
        try:
            last_time_str = self.trips[-1].timestamp
            last_time = datetime.datetime.strptime(last_time_str, "%d-%m-%Y %H:%M")
            new_time = last_time + datetime.timedelta(minutes=random.randint(0,1))
            return new_time.strftime("%d-%m-%Y %H:%M")
        except Exception as e:
            return datetime.datetime.now().strftime("%d-%m-%Y %H:%M")