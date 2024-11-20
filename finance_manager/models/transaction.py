from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from config.settings import TRANSACTIONS_FILE

@dataclass
class Transaction:
    transaction_id: int
    date: str
    type: str  # "Thu nhập" or "Chi tiêu"
    amount: float
    category: str
    account_id: int
    note: str = ""
    
    @classmethod
    def get_all(cls):
        try:
            df = pd.read_csv(TRANSACTIONS_FILE)
            return [cls(**row) for _, row in df.iterrows()]
        except FileNotFoundError:
            return []
    
    @classmethod
    def get_recent(cls, limit=5):
        try:
            df = pd.read_csv(TRANSACTIONS_FILE)
            df = df.sort_values('date', ascending=False).head(limit)
            return [cls(**row) for _, row in df.iterrows()]
        except FileNotFoundError:
            return []
            
    def save(self):
        df = pd.read_csv(TRANSACTIONS_FILE)
        new_data = {
            'transaction_id': self.transaction_id,
            'date': self.date,
            'type': self.type,
            'amount': self.amount,
            'category': self.category,
            'account_id': self.account_id,
            'note': self.note
        }
        
        if self.transaction_id in df['transaction_id'].values:
            df.loc[df['transaction_id'] == self.transaction_id] = new_data
        else:
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            
        df.to_csv(TRANSACTIONS_FILE, index=False) 
    
    @classmethod
    def delete(cls, transaction_id: int):
        try:
            df = pd.read_csv(TRANSACTIONS_FILE)
            if transaction_id in df['transaction_id'].values:
                df = df[df['transaction_id'] != transaction_id]
                # Reset và cập nhật lại các transaction_id
                df = df.reset_index(drop=True)
                df['transaction_id'] = df.index + 1
                df.to_csv(TRANSACTIONS_FILE, index=False)
                return True
            return False
        except FileNotFoundError:
            return False 