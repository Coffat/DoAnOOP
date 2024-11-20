import csv
from datetime import datetime

def migrate_loans():
    """Chuyển đổi dữ liệu từ format cũ sang format mới"""
    old_loans = []
    with open('data/loans_old.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        old_loans = list(reader)

    with open('data/loans.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'type', 'lender', 'borrower', 'amount', 
            'interest_rate', 'start_date', 'due_date',
            'payment_period', 'is_compound', 'note',
            'is_completed', 'payment_history'
        ])

        for old_loan in old_loans:
            # Chuyển đổi dữ liệu và ghi vào file mới
            writer.writerow([
                old_loan['id'],
                'borrowing' if old_loan['type'] == 'Vay tiền' else 'lending',
                old_loan['lender'],
                old_loan['borrower'],
                float(old_loan['amount']),
                float(old_loan['interest_rate']),
                old_loan['start_date'],
                old_loan['due_date'],
                old_loan['payment_period'],
                old_loan['interest_type'] == 'Lãi kép',
                old_loan.get('note', ''),
                old_loan['status'] == 'Đã trả',
                '[]'  # Payment history trống, cần migrate riêng
            ]) 