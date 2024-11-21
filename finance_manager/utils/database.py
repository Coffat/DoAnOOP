import os
import csv
from config.settings import (
    DATA_DIR,
    ACCOUNTS_FILE,
    TRANSACTIONS_FILE,
    LOANS_FILE,
    SAVINGS_FILE,
    LOAN_PAYMENTS_FILE
)

def initialize_database():
    """Initialize all required CSV files if they don't exist."""
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Initialize accounts.csv
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['account_id', 'name', 'balance', 'type'])

    # Initialize transactions.csv
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['transaction_id', 'date', 'type', 'amount', 
                           'category', 'account_id', 'note'])

    # Initialize loans.csv
    if not os.path.exists(LOANS_FILE):
        with open(LOANS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['loan_id', 'type', 'amount', 'interest_rate', 
                           'start_date', 'due_date', 'payment_period', 
                           'interest_type', 'from_account_id', 'to_account_id',
                           'status', 'remaining_principal', 'total_paid_principal',
                           'total_paid_interest', 'note'])

    # Initialize savings.csv
    if not os.path.exists(SAVINGS_FILE):
        with open(SAVINGS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['goal_id', 'name', 'target_amount', 
                           'current_amount', 'deadline'])

    # Initialize loan_payments.csv
    if not os.path.exists(LOAN_PAYMENTS_FILE):
        with open(LOAN_PAYMENTS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['payment_id', 'loan_id', 'payment_date', 'amount',
                           'principal_amount', 'interest_amount', 'note'])
 