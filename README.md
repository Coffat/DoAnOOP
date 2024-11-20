
# Finance Manager

Ứng dụng quản lý tài chính cá nhân được xây dựng bằng Python và CustomTkinter.

## Tính năng chính

### 1. Quản lý Tài khoản
- Thêm, sửa, xóa tài khoản
- Hỗ trợ nhiều loại tài khoản: Tiền mặt, Tài khoản ngân hàng, Ví điện tử
- Theo dõi số dư theo thời gian thực
- Kiểm tra trùng lặp tên tài khoản

### 2. Quản lý Giao dịch
- Ghi nhận các loại giao dịch: Thu nhập, Chi tiêu, Chuyển tiền, Gửi tiết kiệm
- Phân loại giao dịch theo danh mục
- Tự động cập nhật số dư tài khoản
- Hỗ trợ chỉnh sửa và xóa giao dịch với hoàn lại số dư

### 3. Báo cáo Tài chính
- Biểu đồ thu chi theo tháng
- Phân tích dòng tiền
- Thống kê theo danh mục
- Báo cáo tài sản

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/yourusername/finance-manager.git
cd finance-manager
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các thư viện:
```bash
pip install -r requirements.txt
```

## Cấu trúc thư mục

```
finance_manager/
├── models/              # Data models
│   ├── account.py
│   ├── transaction.py
│   └── saving.py
├── views/              # UI components
│   ├── accounts.py
│   ├── transactions.py
│   ├── dashboard.py
│   └── reports.py
├── utils/              # Helper functions
│   ├── database.py
│   └── helpers.py
├── config/            # Configuration files
│   └── settings.py
└── main.py           # Entry point
```

## Sử dụng

1. Khởi động ứng dụng:
```bash
python finance_manager/main.py
```

2. Các bước cơ bản:
- Tạo tài khoản mới trong phần Quản lý Tài khoản
- Thêm giao dịch thu/chi trong phần Quản lý Giao dịch
- Xem báo cáo tài chính trong phần Báo cáo

## Đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Yêu cầu hệ thống

- Python 3.8+
- CustomTkinter
- Pandas
- Matplotlib
- SQLite3

## Giấy phép

Phân phối theo giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## Liên hệ

Coffat - vut210225@gmail.com

Project Link: https://github.com/Coffat/DoAnOOP.git
```
