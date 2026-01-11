### 🛡️ Z-Shield: Security Operations Center (SOC) Simulation
Hệ thống giả lập Trung tâm Điều hành Bảo mật & Bảo vệ Quyền riêng tư

### Giới thiệu (Overview)
Z-Shield là một ứng dụng demo được xây dựng bằng Python và Streamlit, mô phỏng một lớp bảo mật trung gian (Middleware) giữa người dùng và các ứng dụng thứ ba (như Mạng xã hội, Ứng dụng ngân hàng, Thương mại điện tử).

Mục tiêu của Z-Shield là minh họa cách người dùng có thể bảo vệ dữ liệu nhạy cảm thông qua các công nghệ tiên tiến như Zero-Knowledge Proofs (ZKP) và Data Obfuscation (Làm mờ dữ liệu).

### Tính năng chính (Key Features)
Hệ thống bao gồm 3 phân hệ bảo vệ cốt lõi:

### 1. Z-FACE (Xác thực khuôn mặt ZKP)
Vấn đề: Các ứng dụng thường yêu cầu ảnh gốc (Raw Image) để KYC, gây nguy cơ lộ lọt dữ liệu sinh trắc học hoặc bị Deepfake.

Giải pháp Z-Shield:

Sử dụng mô phỏng giao thức Zero-Knowledge Proof.

Chỉ gửi bằng chứng toán học (Proof Hash) xác nhận danh tính.

Chặn hoàn toàn việc gửi ảnh gốc (Raw Image) đến ứng dụng đích.

### 2. Z-GEO (Làm nhiễu vị trí)
Vấn đề: Ứng dụng yêu cầu quyền GPS chính xác, làm lộ địa chỉ nhà riêng/cơ quan.

Giải pháp Z-Shield:

Tạo lớp vỏ bọc vị trí (Location Obfuscation).

Cung cấp tọa độ ảo lệch ngẫu nhiên trong bán kính cài đặt (ví dụ: 1500m).

Bảo vệ vị trí thực trong khi vẫn đảm bảo tính năng vùng của ứng dụng hoạt động.

### 3. Z-AGE (Xác thực độ tuổi ẩn danh)
Vấn đề: Phải cung cấp ngày sinh chính xác (DD/MM/YYYY) chỉ để chứng minh đủ 18 tuổi.

Giải pháp Z-Shield:

Cơ chế xác thực Boolean (Yes/No).

Ứng dụng chỉ biết người dùng "Đủ tuổi" hay "Chưa đủ tuổi", không biết ngày sinh cụ thể.

### 4. Đa ngôn ngữ & Giám sát
Hỗ trợ ngôn ngữ: Chuyển đổi tức thì giữa Tiếng Việt (VN) và Tiếng Anh (EN).

Dashboard thời gian thực: Biểu đồ giám sát các mối đe dọa, log sự kiện.

Audit Log: Xuất nhật ký hoạt động ra file CSV để kiểm toán.

### Công nghệ sử dụng (Tech Stack)
Ngôn ngữ: Python

Framework giao diện: Streamlit

Xử lý dữ liệu: Pandas, NumPy

Mã hóa (Mô phỏng): Hashlib (SHA-256, SHA3-512), AES-256-GCM simulation.

### Cài đặt & Triển khai (Installation)
Để chạy dự án trên máy cục bộ, hãy làm theo các bước sau:

### Bước 1: Clone dự án
Tải mã nguồn về máy tính của bạn.

### Bước 2: Cài đặt thư viện
Yêu cầu Python 3.8 trở lên. Mở terminal tại thư mục dự án và chạy:
pip install streamlit pandas numpy

Có file requirements.txt:
pip install -r requirements.txt

### Bước 3: Chạy ứng dụng
Khởi chạy Z-Shield bằng lệnh Streamlit:
streamlit run FINAL.py

Sau khi chạy, trình duyệt sẽ tự động mở tại địa chỉ: http://localhost:8501

### Hướng dẫn sử dụng (User Guide)
Giao diện được chia thành 2 phần chính:

Bảng điều khiển (Sidebar - Bên trái):

Preset: Chọn cấu hình nhanh (Nghiêm ngặt, Cân bằng, hoặc Dev).

Z-Age: Nhập ngày sinh giả lập để kiểm tra logic 18+.

Z-Face: Bật/Tắt lớp ZKP và chọn cấp độ mã hóa.

Z-Geo: Bật/Tắt làm nhiễu và chỉnh bán kính (mét).

Quản lý App: Chọn ứng dụng đích (Shopee, Bank, Facebook) hoặc ngắt kết nối (Kill Switch).

Màn hình giám sát (Main - Bên phải):

Tab 1 - Giám sát trực tiếp: Nơi bạn thao tác (chụp ảnh, cập nhật GPS) và xem log thời gian thực.

Tab 2 - Góc nhìn ứng dụng: Mô phỏng những gì Server của ứng dụng nhận được (để chứng minh Z-Shield đã chặn dữ liệu gốc thành công).

📂 Cấu trúc dự án (Project Structure)
Finnovative_Project_AA/
├── FINAL.py             # Mã nguồn chính của ứng dụng
├── README.md            # Tài liệu hướng dẫn (File này)
└── requirements.txt     # Danh sách thư viện phụ thuộc
