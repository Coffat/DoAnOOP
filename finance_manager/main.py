import os
import sys

# Thêm thư mục gốc vào PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import customtkinter as ctk
from finance_manager.views.main_window import MainWindow
from finance_manager.utils.database import initialize_database

def main():
        
    # Initialize database
    initialize_database()
    
    # Start application
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()