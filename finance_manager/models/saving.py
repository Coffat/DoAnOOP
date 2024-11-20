from dataclasses import dataclass
import pandas as pd
from config.settings import SAVINGS_FILE

@dataclass
class Saving:
    goal_id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: str
    account_id: int
    note: str = ""
    
    @property
    def progress(self) -> float:
        return (self.current_amount / self.target_amount) * 100
    
    @property
    def account_name(self) -> str:
        """Trả về tên tài khoản tiết kiệm"""
        from models.account import Account
        account = Account.get_by_id(self.account_id)
        return account.name if account else "Unknown"
    
    @classmethod
    def get_all(cls):
        try:
            df = pd.read_csv(SAVINGS_FILE)
            return [cls(**row) for _, row in df.iterrows()]
        except FileNotFoundError:
            return []
            
    def save(self):
        try:
            df = pd.read_csv(SAVINGS_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['goal_id', 'name', 'target_amount', 
                                     'current_amount', 'deadline', 'account_id', 'note'])
        
        new_data = pd.DataFrame([{
            'goal_id': self.goal_id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'deadline': self.deadline,
            'account_id': self.account_id,
            'note': self.note
        }])
        
        if self.goal_id in df['goal_id'].values:
            df = df[df['goal_id'] != self.goal_id]
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = pd.concat([df, new_data], ignore_index=True)
            
        df = df.sort_values('goal_id').reset_index(drop=True)
        df.to_csv(SAVINGS_FILE, index=False)
        
    @classmethod
    def delete(cls, goal_id: int):
        try:
            df = pd.read_csv(SAVINGS_FILE)
            if goal_id in df['goal_id'].values:
                df = df[df['goal_id'] != goal_id]
                df = df.reset_index(drop=True)
                df['goal_id'] = df.index + 1
                df.to_csv(SAVINGS_FILE, index=False)
                return True
            return False
        except FileNotFoundError:
            return False 