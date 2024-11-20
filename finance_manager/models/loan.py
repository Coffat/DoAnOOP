from dataclasses import dataclass
import pandas as pd
from datetime import datetime, timedelta
from config.settings import LOANS_FILE, LOAN_PAYMENTS_FILE

@dataclass
class LoanPayment:
    payment_id: int
    loan_id: int
    payment_date: str
    amount: float
    principal_amount: float  # Tiền gốc
    interest_amount: float  # Tiền lãi
    note: str = ""

@dataclass
class Loan:
    loan_id: int
    type: str  # "Vay tiền" or "Cho vay"
    lender_name: str  # Tên người cho vay
    borrower_name: str  # Tên người vay
    amount: float  # Số tiền gốc
    interest_rate: float  # Lãi suất (%/năm)
    start_date: str
    due_date: str
    payment_period: str  # "Hàng tháng", "Hàng quý", "Một lần"
    interest_type: str  # "Lãi đơn", "Lãi kép"
    status: str = "Đang vay"  # "Đang vay", "Đã trả", "Quá hạn"
    remaining_principal: float = None  # Số tiền gốc còn lại
    total_paid_principal: float = 0  # Tổng tiền gốc đã trả
    total_paid_interest: float = 0  # Tổng tiền lãi đã trả
    note: str = ""
    
    def __post_init__(self):
        if self.remaining_principal is None:
            self.remaining_principal = self.amount
            
    @property
    def total_amount_due(self) -> float:
        """Tổng số tiền phải trả (gốc + lãi)"""
        interest_info = self.calculate_interest()
        return self.remaining_principal + interest_info['accrued_interest']
        
    @property
    def next_payment_date(self) -> str:
        """Ngày trả tiền tiếp theo"""
        interest_info = self.calculate_interest()
        return interest_info['next_payment_date']
        
    @property
    def days_overdue(self) -> int:
        """Số ngày quá hạn"""
        if self.status != "Quá hạn":
            return 0
        due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
        today = datetime.now()
        return (today - due_date).days
    
    @classmethod
    def get_all(cls):
        try:
            df = pd.read_csv(LOANS_FILE)
            return [cls(**row) for _, row in df.iterrows()]
        except FileNotFoundError:
            df = pd.DataFrame(columns=['loan_id', 'type', 'lender_name', 'borrower_name', 
                                     'amount', 'interest_rate', 'start_date', 'due_date',
                                     'payment_period', 'interest_type', 'status', 
                                     'remaining_principal', 'total_paid_principal',
                                     'total_paid_interest', 'note'])
            df.to_csv(LOANS_FILE, index=False)
            return []
            
    def save(self):
        try:
            df = pd.read_csv(LOANS_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['loan_id', 'type', 'lender_name', 'borrower_name', 
                                     'amount', 'interest_rate', 'start_date', 'due_date',
                                     'payment_period', 'interest_type', 'status', 
                                     'remaining_principal', 'total_paid_principal',
                                     'total_paid_interest', 'note'])
        
        new_data = pd.DataFrame([{
            'loan_id': self.loan_id,
            'type': self.type,
            'lender_name': self.lender_name,
            'borrower_name': self.borrower_name,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'start_date': self.start_date,
            'due_date': self.due_date,
            'payment_period': self.payment_period,
            'interest_type': self.interest_type,
            'status': self.status,
            'remaining_principal': self.remaining_principal,
            'total_paid_principal': self.total_paid_principal,
            'total_paid_interest': self.total_paid_interest,
            'note': self.note
        }])
        
        if self.loan_id in df['loan_id'].values:
            df = df[df['loan_id'] != self.loan_id]
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = pd.concat([df, new_data], ignore_index=True)
            
        df = df.sort_values('loan_id').reset_index(drop=True)
        df.to_csv(LOANS_FILE, index=False)
        
    def add_payment(self, amount: float, payment_date: str, principal_amount: float, 
                   interest_amount: float, note: str = ""):
        """Thêm một khoản thanh toán cho khoản vay"""
        try:
            df = pd.read_csv(LOAN_PAYMENTS_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['payment_id', 'loan_id', 'payment_date', 'amount',
                                     'principal_amount', 'interest_amount', 'note'])
        
        new_payment_id = len(df) + 1
        new_payment = pd.DataFrame([{
            'payment_id': new_payment_id,
            'loan_id': self.loan_id,
            'payment_date': payment_date,
            'amount': amount,
            'principal_amount': principal_amount,
            'interest_amount': interest_amount,
            'note': note
        }])
        
        df = pd.concat([df, new_payment], ignore_index=True)
        df.to_csv(LOAN_PAYMENTS_FILE, index=False)
        
        # Cập nhật thông tin khoản vay
        self.remaining_principal -= principal_amount
        self.total_paid_principal += principal_amount
        self.total_paid_interest += interest_amount
        
        if self.remaining_principal <= 0:
            self.status = "Đã trả"
            
        self.save()
        
    def get_payments(self):
        try:
            df = pd.read_csv(LOAN_PAYMENTS_FILE)
            payments_df = df[df['loan_id'] == self.loan_id]
            return [LoanPayment(**row) for _, row in payments_df.iterrows()]
        except FileNotFoundError:
            return []
            
    def calculate_interest(self, to_date: str = None) -> dict:
        """
        Tính toán lãi suất đến ngày chỉ định
        Trả về dict chứa:
        - accrued_interest: Tiền lãi phát sinh
        - daily_interest: Tiền lãi phát sinh mỗi ngày
        - days_elapsed: Số ngày đã trôi qua
        - next_payment_date: Ngày trả tiền tiếp theo
        """
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
            
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        days = (end - start).days
        
        # Tính lãi suất theo ngày (lãi suất năm / 365)
        daily_rate = self.interest_rate / 100 / 365
        
        if self.interest_type == "Lãi đơn":
            accrued_interest = self.remaining_principal * daily_rate * days
            daily_interest = self.remaining_principal * daily_rate
        else:  # Lãi kép
            periods = days/365  # Số năm
            accrued_interest = self.remaining_principal * ((1 + self.interest_rate/100) ** periods - 1)
            daily_interest = self.remaining_principal * daily_rate * (1 + self.interest_rate/100) ** (periods-1/365)
        
        # Tính ngày trả tiền tiếp theo dựa vào payment_period
        if self.payment_period == "Hàng tháng":
            next_payment = start + timedelta(days=30)
        elif self.payment_period == "Hàng quý":
            next_payment = start + timedelta(days=90)
        else:  # Một lần
            next_payment = datetime.strptime(self.due_date, "%Y-%m-%d")
            
        while next_payment <= end:
            if self.payment_period == "Hàng tháng":
                next_payment += timedelta(days=30)
            elif self.payment_period == "Hàng quý":
                next_payment += timedelta(days=90)
            else:
                break
                
        return {
            'accrued_interest': round(accrued_interest, 2),
            'daily_interest': round(daily_interest, 2),
            'days_elapsed': days,
            'next_payment_date': next_payment.strftime("%Y-%m-%d")
        }
        
    def check_due_status(self):
        today = datetime.now()
        due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
        
        if today > due_date and self.status == "Đang vay":
            self.status = "Quá hạn"
            self.save()
            return True
        return False
    
    @classmethod
    def delete(cls, loan_id: int):
        """Xóa khoản vay và tất cả lịch sử thanh toán của nó"""
        try:
            # Xóa khoản vay
            loans_df = pd.read_csv(LOANS_FILE)
            if loan_id in loans_df['loan_id'].values:
                # Xóa khoản vay
                loans_df = loans_df[loans_df['loan_id'] != loan_id]
                loans_df = loans_df.reset_index(drop=True)
                loans_df['loan_id'] = loans_df.index + 1
                loans_df.to_csv(LOANS_FILE, index=False)
                
                # Xóa tất cả lịch sử thanh toán của khoản vay này
                try:
                    payments_df = pd.read_csv(LOAN_PAYMENTS_FILE)
                    payments_df = payments_df[payments_df['loan_id'] != loan_id]
                    payments_df = payments_df.reset_index(drop=True)
                    payments_df['payment_id'] = payments_df.index + 1
                    payments_df.to_csv(LOAN_PAYMENTS_FILE, index=False)
                except FileNotFoundError:
                    # Nếu file thanh toán không tồn tại, bỏ qua
                    pass
                    
                return True
            return False
        except FileNotFoundError:
            return False