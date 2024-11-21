import customtkinter as ctk
from views.dashboard import DashboardView
from views.accounts import AccountsView
from views.transactions import TransactionsView
from views.loans import LoansView
from views.savings import SavingsView
from views.reports import ReportsView
from views.forecast_view import ForecastView
from config.colors import *

class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Quản Lý Tài Chính Cá Nhân")
        self.window.geometry("1600x900")
        
        self.window.minsize(1200, 700)
        
        self.setup_theme()
        self.create_main_container()
        self.create_sidebar()
        self.create_content_frame()
        
        # Initialize views
        self.dashboard = DashboardView(self.content_frame)
        self.accounts = AccountsView(self.content_frame)
        self.transactions = TransactionsView(self.content_frame)
        self.loans = LoansView(self.content_frame)
        self.savings = SavingsView(self.content_frame)
        self.reports = ReportsView(self.content_frame)
        self.forecast = ForecastView(self.content_frame)
        
        # Show dashboard by default
        self.show_dashboard()
        
    def setup_theme(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
    def create_main_container(self):
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.main_container, 
            width=250,
            fg_color=BACKGROUND['dark']
        )
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Logo
        logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Finance Manager",
            font=("Helvetica", 24, "bold"),
            text_color=TEXT['light']
        )
        logo_label.pack(pady=30)
        
        # Navigation buttons
        buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("💳 Tài Khoản", self.show_accounts), 
            ("💰 Giao Dịch", self.show_transactions),
            ("💸 Vay & Cho Vay", self.show_loans),
            ("🏦 Tiết Kiệm", self.show_savings),
            ("📊 Báo Cáo", self.show_reports),
            ("🔮 Dự Báo", self.show_forecast)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=220,
                height=40,
                font=("Helvetica", 14),
                anchor="w",
                fg_color=PRIMARY['main'],
                hover_color=PRIMARY['hover'],
                text_color=TEXT['light']
            )
            btn.pack(pady=10)
            
    def create_content_frame(self):
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
    def show_dashboard(self):
        self.clear_content()
        self.dashboard.show()
        
    def show_accounts(self):
        self.clear_content()
        self.accounts.show()
        
    def show_transactions(self):
        self.clear_content()
        self.transactions.show()
        
    def show_loans(self):
        self.clear_content()
        self.loans.show()
        
    def show_savings(self):
        self.clear_content()
        self.savings.show()
        
    def show_reports(self):
        self.clear_content()
        self.reports.show()
        
    def show_forecast(self):
        self.clear_content()
        self.forecast.show()
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def run(self):
        self.window.mainloop() 