import os
import csv
from datetime import datetime
from typing import List, Optional
from models.loan import Loan, PaymentHistory

class LoanManager:
    def __init__(self, data_file: str = "data/loans.csv"):
        self.data_file = data_file
        self.ensure_data_file_exists()
        
    def ensure_data_file_exists(self):
        """Đảm bảo file CSV tồn tại với headers"""
        if not os.path.exists(os.path.dirname(self.data_file)):
            os.makedirs(os.path.dirname(self.data_file))
            
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'id', 'lender', 'borrower', 'amount', 'start_date', 
                    'due_date', 'interest_rate', 'is_compound', 'note',
                    'is_completed', 'type', 'payment_history'
                ])

    def load_loans(self) -> List[Loan]:
        """Đọc tất cả khoản vay từ file CSV"""
        loans = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Chuyển đổi payment_history từ string sang list
                payment_history = eval(row['payment_history']) if row['payment_history'] else []
                payment_history = [
                    PaymentHistory(
                        date=datetime.fromisoformat(p['date']),
                        amount=float(p['amount']),
                        note=p.get('note')
                    ) for p in payment_history
                ]
                
                loan = Loan(
                    id=row['id'],
                    lender=row['lender'],
                    borrower=row['borrower'],
                    amount=float(row['amount']),
                    start_date=datetime.fromisoformat(row['start_date']),
                    due_date=datetime.fromisoformat(row['due_date']),
                    interest_rate=float(row['interest_rate']),
                    is_compound=row['is_compound'].lower() == 'true',
                    note=row['note'],
                    is_completed=row['is_completed'].lower() == 'true',
                    type=row['type'],
                    payment_history=payment_history
                )
                loans.append(loan)
        return loans

    def save_loan(self, loan: Loan):
        """Lưu hoặc cập nhật một khoản vay"""
        loans = self.load_loans()
        
        # Chuyển đổi payment_history thành format có thể serialize
        payment_history = [
            {
                'date': payment.date.isoformat(),
                'amount': payment.amount,
                'note': payment.note
            } for payment in loan.payment_history
        ]
        
        # Tìm và cập nhật khoản vay nếu đã tồn tại
        updated = False
        for i, existing_loan in enumerate(loans):
            if existing_loan.id == loan.id:
                loans[i] = loan
                updated = True
                break
                
        if not updated:
            loans.append(loan)
            
        # Lưu tất cả vào file
        with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'lender', 'borrower', 'amount', 'start_date', 
                'due_date', 'interest_rate', 'is_compound', 'note',
                'is_completed', 'type', 'payment_history'
            ])
            
            for l in loans:
                writer.writerow([
                    l.id, l.lender, l.borrower, l.amount,
                    l.start_date.isoformat(), l.due_date.isoformat(),
                    l.interest_rate, l.is_compound, l.note,
                    l.is_completed, l.type, payment_history
                ])

    def delete_loan(self, loan_id: str):
        """Xóa một khoản vay"""
        loans = [loan for loan in self.load_loans() if loan.id != loan_id]
        
        with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'lender', 'borrower', 'amount', 'start_date', 
                'due_date', 'interest_rate', 'is_compound', 'note',
                'is_completed', 'type', 'payment_history'
            ])
            
            for loan in loans:
                payment_history = [
                    {
                        'date': payment.date.isoformat(),
                        'amount': payment.amount,
                        'note': payment.note
                    } for payment in loan.payment_history
                ]
                writer.writerow([
                    loan.id, loan.lender, loan.borrower, loan.amount,
                    loan.start_date.isoformat(), loan.due_date.isoformat(),
                    loan.interest_rate, loan.is_compound, loan.note,
                    loan.is_completed, loan.type, payment_history
                ])

    def get_due_loans(self, days_threshold: int = 7) -> List[Loan]:
        """Lấy danh sách các khoản vay sắp đến hạn"""
        return [loan for loan in self.load_loans() if loan.is_due_soon(days_threshold)] 