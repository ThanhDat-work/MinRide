HƯỚNG DẪN CHẠY CHƯƠNG TRÌNH - DỰ ÁN MINRIDE
Dự án MinRide là chương trình mô phỏng hệ thống đặt xe, cho phép quản lý tài xế, khách hàng và tính toán lộ trình/giá cước.

1. Thành phần hồ sơ nộp bài
Mã nguồn chính: App_Main.py.

File hỗ trợ: Các services xử lý (ví dụ: driver_repo.py, customer_repo.py, ride_repo.py), file dữ liệu đầu vào (customers.csv, drivers.csv, trips.csv).
README.md: File hướng dẫn này.

2. Yêu cầu môi trường
Để chạy được chương trình, máy tính cần cài đặt:
Ngôn ngữ: Python 3.9+ 
Thư viện: tkinter, PIL, os, csv, copy, pathlib, math, random

3. Hướng dẫn chạy chương trình
Bạn thực hiện theo các bước sau để khởi động bản demo:

Bước 1: Mở terminal (CMD hoặc PowerShell) tại thư mục chứa code. 
Bước 2: Nhập lệnh sau:
Đối với Python: python App_Main.py

4. Dữ liệu đầu vào mẫu (Sample Input)
Đã khởi tạo một vài khách hàng, tài xế và chuyến đi để thuận tiện cho việc thực hiện các chức năng của app.
Ngoài ra, người dùng có thể nhập dữ liệu đầu vào bằng các thao tác như thêm tài xế, thêm khách hàng hay đặt xe,..