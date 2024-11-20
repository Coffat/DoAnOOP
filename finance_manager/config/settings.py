import os

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# CSV file paths
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.csv')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.csv')
LOANS_FILE = os.path.join(DATA_DIR, 'loans.csv')
SAVINGS_FILE = os.path.join(DATA_DIR, 'savings.csv')
LOAN_PAYMENTS_FILE = os.path.join(DATA_DIR, 'loan_payments.csv')

# UI Settings
WINDOW_SIZE = "1200x700"
WINDOW_TITLE = "Quản Lý Tài Chính Cá Nhân"

# Categories
EXPENSE_CATEGORIES = ["Ăn uống", "Di chuyển", "Mua sắm", "Giải trí", "Khác"]
INCOME_CATEGORIES = ["Tiền lương", "Đầu tư", "Khác"]
ACCOUNT_TYPES = ["Tài khoản ngân hàng", "Tiền mặt", "Ví điện tử"]

# Thêm các cấu hình cho khoản vay
PAYMENT_PERIODS = ["Hàng tháng", "Hàng quý", "Một lần"]
INTEREST_TYPES = ["Lãi đơn", "Lãi kép"]
LOAN_STATUSES = ["Đang vay", "Đã trả", "Quá hạn"]