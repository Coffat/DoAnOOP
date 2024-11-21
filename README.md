# Finance Manager - Ứng Dụng Quản Lý Tài Chính Cá Nhân

## Giới thiệu
Finance Manager là một ứng dụng desktop giúp người dùng quản lý tài chính cá nhân một cách hiệu quả. Ứng dụng được phát triển bằng Python với giao diện người dùng hiện đại sử dụng CustomTkinter.

## Tính năng chính
- 🏠 **Dashboard**: Tổng quan về tình hình tài chính
- 💳 **Quản lý tài khoản**: Theo dõi số dư các tài khoản
- 💰 **Quản lý giao dịch**: Ghi chép thu chi
- 💸 **Quản lý khoản vay**: Theo dõi các khoản vay và cho vay
- 🏦 **Quản lý tiết kiệm**: Theo dõi các khoản tiết kiệm
- 📊 **Báo cáo**: Phân tích và thống kê tài chính
- 🔮 **Dự báo**: Dự báo tài chính tương lai

## Yêu cầu hệ thống
- Python 3.8 trở lên
- Các thư viện được liệt kê trong file requirements.txt

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
