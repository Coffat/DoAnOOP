import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'finance.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database and create tables"""
    from ..models.loan import Loan
    from ..models.account import Account
    from ..models.loan_payment import LoanPayment
    
    # Create tables
    Loan.create_table()
    Account.create_table()
    LoanPayment.create_table() 