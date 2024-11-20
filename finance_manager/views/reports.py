import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta
from models.transaction import Transaction
from models.account import Account
from models.loan import Loan
from models.saving import Saving
import xlsxwriter
import io
import os

class ReportsView:
    def __init__(self, parent):
        self.parent = parent
        
    def show(self):
        self.create_title()
        self.create_tabs()
        
    def create_title(self):
        title = ctk.CTkLabel(
            self.parent,
            text="Báo Cáo Tài Chính",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
    def create_tabs(self):
        # Control Frame cho lựa chọn tài khoản và xuất báo cáo
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Left side - Account Selection
        account_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        account_frame.pack(side="left", fill="x", expand=True)
        
        account_label = ctk.CTkLabel(
            account_frame, 
            text="🏦 Chọn Tài Khoản:",
            font=("Helvetica", 14, "bold")
        )
        account_label.pack(side="left", padx=10)
        
        accounts = Account.get_all()
        account_names = ["Tất cả tài khoản"] + [acc.name for acc in accounts]
        self.account_var = ctk.StringVar(value=account_names[0])
        self.account_menu = ctk.CTkOptionMenu(
            account_frame,
            values=account_names,
            variable=self.account_var,
            width=250,
            height=35,
            font=("Helvetica", 12),
            command=self.on_account_change
        )
        self.account_menu.pack(side="left", padx=10)
        
        # Right side - Export Button
        export_btn = ctk.CTkButton(
            control_frame,
            text="📊 Xuất Báo Cáo Excel",
            command=self.export_to_excel,
            width=180,
            height=35,
            font=("Helvetica", 12, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        export_btn.pack(side="right", padx=20)
        
        # Tabview with custom style
        self.tabview = ctk.CTkTabview(self.parent)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add tabs with icons
        self.tab_income_expense = self.tabview.add("💰 Thu Chi")
        self.tab_cashflow = self.tabview.add("📈 Dòng Tiền")
        self.tab_category = self.tabview.add("📊 Chi Tiêu Theo Danh Mục")
        self.tab_assets = self.tabview.add("💎 Tài Sản")
        
        # Style the tabs
        for tab in [self.tab_income_expense, self.tab_cashflow, 
                   self.tab_category, self.tab_assets]:
            tab.configure(fg_color=("gray95", "gray10"))
        
        # Create content for each tab
        self.create_income_expense_report(self.tab_income_expense)
        self.create_cashflow_report(self.tab_cashflow)
        self.create_category_report(self.tab_category)
        self.create_assets_report(self.tab_assets)
        
    def on_account_change(self, account_name):
        """Cập nhật tất cả các báo cáo khi thay đổi tài khoản"""
        # Xóa nội dung cũ của các tab
        for widget in self.tab_income_expense.winfo_children():
            widget.destroy()
        for widget in self.tab_cashflow.winfo_children():
            widget.destroy()
        for widget in self.tab_category.winfo_children():
            widget.destroy()
        for widget in self.tab_assets.winfo_children():
            widget.destroy()
            
        # Tạo lại nội dung mới với tài khoản đã chọn
        self.create_income_expense_report(self.tab_income_expense)
        self.create_cashflow_report(self.tab_cashflow)
        self.create_category_report(self.tab_category)
        self.create_assets_report(self.tab_assets)
        
    def get_filtered_transactions(self):
        """Lấy danh sách giao dịch theo tài khoản được chọn"""
        transactions = Transaction.get_all()
        
        if self.account_var.get() != "Tất cả tài khoản":
            account = next(acc for acc in Account.get_all() 
                         if acc.name == self.account_var.get())
            transactions = [t for t in transactions if t.account_id == account.account_id]
            
        # Sắp xếp theo ngày mới nhất
        transactions.sort(key=lambda x: x.date, reverse=True)
        return transactions
        
    def create_chart_frame(self, parent, title):
        """Helper function to create consistent chart frames"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)
        
        # Title with background
        title_frame = ctk.CTkFrame(frame)
        title_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=("Helvetica", 16, "bold")
        ).pack(pady=5)
        
        return frame

    def create_summary_frame(self, parent, title, content):
        """Helper function to create consistent summary frames"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            frame,
            text=content,
            font=("Helvetica", 12),
            justify="left"
        ).pack(pady=5)
        
        return frame

    def create_income_expense_report(self, parent):
        transactions = self.get_filtered_transactions()
        if not transactions:
            # Hiển thị thông báo nếu không có dữ liệu
            ctk.CTkLabel(
                parent,
                text=f"Không có dữ liệu giao dịch cho {self.account_var.get()}",
                font=("Helvetica", 14)
            ).pack(pady=20)
            return
            
        # Lấy mapping tài khoản trước khi xử lý dữ liệu
        accounts = {acc.account_id: acc.name for acc in Account.get_all()}
            
        # Tính toán thu chi theo tháng
        df = pd.DataFrame([{
            'date': pd.to_datetime(t.date),
            'type': t.type,
            'amount': t.amount
        } for t in transactions])
        
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly_stats = df.pivot_table(
            index='month',
            columns='type',
            values='amount',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Tạo biểu đồ với kích thước nhỏ hơn
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Biểu đồ cột thu chi theo tháng
        months = monthly_stats['month'].tolist()
        
        # Lấy dữ liệu thu chi từ pivot table
        income_data = monthly_stats['Thu nhập'].tolist() if 'Thu nhập' in monthly_stats.columns else [0] * len(months)
        expense_data = monthly_stats['Chi tiêu'].tolist() if 'Chi tiêu' in monthly_stats.columns else [0] * len(months)
        savings_data = monthly_stats['Gửi tiết kiệm'].tolist() if 'Gửi tiết kiệm' in monthly_stats.columns else [0] * len(months)
        
        x = range(len(months))
        width = 0.25
        
        # Điều chỉnh font size và các thông số khác
        ax1.bar([i - width for i in x], income_data, width, label='Thu nhập', color='green')
        ax1.bar([i for i in x], expense_data, width, label='Chi tiêu', color='red')
        ax1.bar([i + width for i in x], savings_data, width, label='Tiết kiệm', color='blue')
        
        ax1.set_title(f'Thu Chi Theo Tháng ({self.account_var.get()})', fontsize=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, rotation=45, fontsize=8)
        ax1.tick_params(axis='y', labelsize=8)
        ax1.legend(fontsize=8)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x/1000000), ',') + 'M'))
        
        # Tính tổng thu chi
        total_income = sum(income_data)
        total_expense = sum(expense_data)
        total_savings = sum(savings_data)
        
        # Biểu đồ tròn tổng thu chi
        if total_income + total_expense + total_savings > 0:
            ax2.pie(
                [total_income, total_expense, total_savings],
                labels=['Thu nhập', 'Chi tiêu', 'Tiết kiệm'],
                autopct='%1.1f%%',
                colors=['green', 'red', 'blue']
            )
            ax2.set_title('Tỷ Lệ Thu Chi')
        
        plt.tight_layout()
        # Thêm biểu đồ vào frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Thêm summary với style mới
        summary_text = (
            f"💵 Tổng thu nhập: {total_income:,.0f} VND\n"
            f"💸 Tổng chi tiêu: {total_expense:,.0f} VND\n"
            f"💰 Tổng tiết kiệm: {total_savings:,.0f} VND\n"
            f"📈 Chênh lệch: {(total_income - total_expense - total_savings):,.0f} VND"
        )
        self.create_summary_frame(parent, "📑 Tổng Kết", summary_text)
        
        # Tạo bảng giao dịch
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="x", padx=10, pady=5)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Tạo treeview
        columns = ('Ngày', 'Loại', 'Số Tiền', 'Danh Mục', 'Tài Khoản', 'Ghi Chú')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                           height=8, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        # Cấu hình cột
        tree.column('Ngày', width=100, minwidth=100)
        tree.column('Loại', width=100, minwidth=100)
        tree.column('Số Tiền', width=150, minwidth=150)
        tree.column('Danh Mục', width=150, minwidth=150)
        tree.column('Tài Khoản', width=150, minwidth=150)
        tree.column('Ghi Chú', width=200, minwidth=200)
        
        # Đặt tiêu đề cột
        for col in columns:
            tree.heading(col, text=col)
        
        # Tạo style cho từng loại giao dịch
        tree.tag_configure('income', foreground='#27ae60')  # Xanh lá đậm
        tree.tag_configure('expense', foreground='#c0392b')  # Đỏ đậm
        tree.tag_configure('saving', foreground='#2980b9')  # Xanh dương đậm
        tree.tag_configure('even_row', background='#f5f5f5')  # Màu nền cho dòng chẵn
        tree.tag_configure('odd_row', background='#ffffff')  # Màu nền cho dòng lẻ
        
        # Thêm dữ liệu vào bảng
        for i, trans in enumerate(transactions):
            values = (
                trans.date,
                trans.type,
                f"{trans.amount:,.0f}",
                trans.category,
                accounts.get(trans.account_id, ""),
                trans.note
            )
            
            # Xác định tags cho từng dòng
            tags = []
            if trans.type == 'Thu nhập':
                tags.append('income')
            elif trans.type == 'Chi tiêu':
                tags.append('expense')
            elif trans.type == 'Gửi tiết kiệm':
                tags.append('saving')
                
            # Thêm tag cho dòng chẵn/lẻ
            tags.append('even_row' if i % 2 == 0 else 'odd_row')
            
            # Thêm dòng vào bảng với tags
            tree.insert('', 'end', values=values, tags=tags)
        
        tree.pack(fill="x", expand=True)
        
        # Thêm chú thích màu
        legend_frame = ctk.CTkFrame(parent)
        legend_frame.pack(fill="x", padx=10, pady=5)
        
        # Thu nhập
        income_label = ctk.CTkLabel(
            legend_frame,
            text="● Thu nhập",
            text_color="#27ae60",
            font=("Helvetica", 12, "bold")
        )
        income_label.pack(side="left", padx=10)
        
        # Chi tiêu
        expense_label = ctk.CTkLabel(
            legend_frame,
            text="● Chi tiêu",
            text_color="#c0392b",
            font=("Helvetica", 12, "bold")
        )
        expense_label.pack(side="left", padx=10)
        
        # Tiết kiệm
        saving_label = ctk.CTkLabel(
            legend_frame,
            text="● Tiết kiệm",
            text_color="#2980b9",
            font=("Helvetica", 12, "bold")
        )
        saving_label.pack(side="left", padx=10)
        
    def create_cashflow_report(self, parent):
        transactions = self.get_filtered_transactions()
        if not transactions:
            return
            
        # Calculate cumulative cash flow
        df = pd.DataFrame([{
            'date': t.date,
            'amount': t.amount if t.type == 'Thu nhập' else 
                     (-t.amount if t.type == 'Chi tiêu' else 
                     -t.amount if t.type == 'Gửi tiết kiệm' else 0)
        } for t in transactions])
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['cumulative'] = df['amount'].cumsum()
        
        # Tạo biểu đồ với kích thước nhỏ hơn
        fig, ax = plt.subplots(figsize=(10, 4))  # Giảm kích thước
        
        ax.plot(df['date'], df['cumulative'], marker='o', markersize=4)  # Giảm kích thước marker
        ax.set_title(f'Dòng Tiền Tích Lũy ({self.account_var.get()})', fontsize=10)
        ax.set_xlabel('Ngày', fontsize=9)
        ax.set_ylabel('VND', fontsize=9)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x/1000000), ',') + 'M'))
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add summary text
        summary_text = (
            f"🏦 Số dư ban đầu: {df['cumulative'].iloc[0]:,.0f} VND\n"
            f"💰 Số dư cuối kỳ: {df['cumulative'].iloc[-1]:,.0f} VND\n"
            f"📊 Thay đổi: {(df['cumulative'].iloc[-1] - df['cumulative'].iloc[0]):,.0f} VND"
        )
        self.create_summary_frame(parent, "📑 Tổng Kết", summary_text)
        
    def create_category_report(self, parent):
        transactions = self.get_filtered_transactions()
        if not transactions:
            return
            
        # Calculate totals by category
        expense_by_category = {}
        income_by_category = {}
        savings_by_category = {}
        
        for t in transactions:
            if t.type == 'Chi tiêu':
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
            elif t.type == 'Thu nhập':
                income_by_category[t.category] = income_by_category.get(t.category, 0) + t.amount
            elif t.type == 'Gửi tiết kiệm':
                savings_by_category[t.category] = savings_by_category.get(t.category, 0) + t.amount
                
        # Tạo biểu đồ với kích thước nhỏ hơn
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))  # Giảm kích thước
        
        # Chi tiêu theo danh mục
        if expense_by_category:
            categories = list(expense_by_category.keys())
            amounts = list(expense_by_category.values())
            total = sum(amounts)
            ax1.pie(amounts, labels=categories, autopct='%1.1f%%', 
                   textprops={'fontsize': 8})  # Giảm font size
            ax1.set_title('Chi Tiêu Theo Danh Mục', fontsize=10)
            
        # Thu nhập theo danh mục
        if income_by_category:
            categories = list(income_by_category.keys())
            amounts = list(income_by_category.values())
            total = sum(amounts)
            ax2.pie(amounts, labels=categories, autopct='%1.1f%%',
                   textprops={'fontsize': 8})  # Giảm font size
            ax2.set_title('Thu Nhập Theo Danh Mục', fontsize=10)
            
        # Tiết kiệm theo mục tiêu
        if savings_by_category:
            categories = list(savings_by_category.keys())
            amounts = list(savings_by_category.values())
            total = sum(amounts)
            ax3.pie(amounts, labels=categories, autopct='%1.1f%%',
                   textprops={'fontsize': 8})  # Giảm font size
            ax3.set_title('Tiết Kiệm Theo Mục Tiêu', fontsize=10)
            
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add summary text
        total_expense = sum(expense_by_category.values())
        total_income = sum(income_by_category.values())
        total_savings = sum(savings_by_category.values())
        
        summary_text = (
            f"Tổng chi tiêu: {total_expense:,.0f} VND\n"
            f"Tổng thu nhập: {total_income:,.0f} VND\n"
            f"Tổng tiết kiệm: {total_savings:,.0f} VND"
        )
        
        summary_label = ctk.CTkLabel(
            parent,
            text=summary_text,
            font=("Helvetica", 14)
        )
        summary_label.pack(pady=10)
        
    def create_assets_report(self, parent):
        # Get data for selected account
        if self.account_var.get() == "Tất cả tài khoản":
            accounts = Account.get_all()
        else:
            accounts = [next(acc for acc in Account.get_all() 
                           if acc.name == self.account_var.get())]
            
        loans = Loan.get_all()
        savings = Saving.get_all()
        
        # Filter loans and savings for selected account
        if self.account_var.get() != "Tất cả tài khoản":
            account = accounts[0]
            loans = [loan for loan in loans 
                    if loan.from_account_id == account.account_id 
                    or loan.to_account_id == account.account_id]
            savings = [saving for saving in savings 
                      if saving.account_id == account.account_id]
        
        # Calculate totals
        total_assets = sum(acc.balance for acc in accounts)
        total_loans = sum(loan.remaining_principal for loan in loans if loan.type == 'Cho vay')
        total_debts = sum(loan.remaining_principal for loan in loans if loan.type == 'Vay tiền')
        total_savings = sum(saving.current_amount for saving in savings)
        
        net_worth = total_assets + total_loans - total_debts + total_savings
        
        # Tạo biểu đồ với kích thước nhỏ hơn
        fig, ax = plt.subplots(figsize=(8, 4))  # Giảm kích thước
        
        labels = ['Tài khoản', 'Cho vay', 'Tiết kiệm']
        sizes = [total_assets, total_loans, total_savings]
        colors = ['lightblue', 'lightgreen', 'orange']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               textprops={'fontsize': 8})  # Giảm font size
        ax.set_title(f'Phân Bổ Tài Sản ({self.account_var.get()})', fontsize=10)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add summary text
        summary_text = (
            f"Số dư tài khoản: {total_assets:,.0f} VND\n"
            f"Cho vay: {total_loans:,.0f} VND\n"
            f"Nợ: {total_debts:,.0f} VND\n"
            f"Tiết kiệm: {total_savings:,.0f} VND\n"
            f"Giá trị ròng: {net_worth:,.0f} VND"
        )
        
        summary_label = ctk.CTkLabel(
            parent,
            text=summary_text,
            font=("Helvetica", 14)
        )
        summary_label.pack(pady=10)
        
    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(pady=10)
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="Xuất Excel",
            command=self.export_to_excel,
            width=120
        )
        export_btn.pack(side="right", padx=10)
        
    def export_to_excel(self):
        try:
            # Chọn nơi lưu file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Lưu báo cáo Excel"
            )
            
            if not file_path:
                return

            # Tạo workbook Excel
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Định dạng chung
                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'bg_color': '#D3D3D3'
                })
                
                money_format = workbook.add_format({
                    'num_format': '#,##0',
                    'align': 'right'
                })

                # 1. Sheet Giao Dịch
                transactions = self.get_filtered_transactions()
                account_map = {acc.account_id: acc.name for acc in Account.get_all()}
                
                trans_data = []
                for trans in transactions:
                    trans_data.append({
                        'Ngày': trans.date,
                        'Loại': trans.type,
                        'Số Tiền': trans.amount,
                        'Danh Mục': trans.category,
                        'Tài Khoản': account_map.get(trans.account_id, ""),
                        'Ghi Chú': trans.note
                    })
                
                df_trans = pd.DataFrame(trans_data)
                df_trans.to_excel(writer, sheet_name='Giao Dịch', index=False)
                
                # Định dạng Sheet Giao Dịch
                worksheet = writer.sheets['Giao Dịch']
                for col_num, value in enumerate(df_trans.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('C:C', 15, money_format)
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('D:D', 20)
                worksheet.set_column('E:E', 20)
                worksheet.set_column('F:F', 30)

                # 2. Sheet Thống Kê Thu Chi
                total_income = sum(t.amount for t in transactions if t.type == 'Thu nhập')
                total_expense = sum(t.amount for t in transactions if t.type == 'Chi tiêu')
                total_savings = sum(t.amount for t in transactions if t.type == 'Gửi tiết kiệm')
                
                summary_data = {
                    'Chỉ số': ['Tổng thu nhập', 'Tổng chi tiêu', 'Tổng tiết kiệm', 'Chênh lệch'],
                    'Số tiền (VND)': [
                        total_income,
                        total_expense,
                        total_savings,
                        total_income - total_expense - total_savings
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Thống Kê Thu Chi', index=False)
                
                # Định dạng Sheet Thống Kê Thu Chi
                worksheet = writer.sheets['Thống Kê Thu Chi']
                for col_num, value in enumerate(df_summary.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('B:B', 20, money_format)
                worksheet.set_column('A:A', 20)

                # 3. Sheet Chi Tiêu Theo Danh Mục
                expense_by_category = {}
                income_by_category = {}
                savings_by_category = {}
                
                for t in transactions:
                    if t.type == 'Chi tiêu':
                        expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
                    elif t.type == 'Thu nhập':
                        income_by_category[t.category] = income_by_category.get(t.category, 0) + t.amount
                    elif t.type == 'Gửi tiết kiệm':
                        savings_by_category[t.category] = savings_by_category.get(t.category, 0) + t.amount
                
                category_data = []
                # Chi tiêu theo danh mục
                for category, amount in expense_by_category.items():
                    category_data.append({
                        'Loại': 'Chi tiêu',
                        'Danh Mục': category,
                        'Số Tiền': amount,
                        'Tỷ Lệ': amount/total_expense*100 if total_expense > 0 else 0
                    })
                # Thu nhập theo danh mục
                for category, amount in income_by_category.items():
                    category_data.append({
                        'Loại': 'Thu nhập',
                        'Danh Mục': category,
                        'Số Tiền': amount,
                        'Tỷ Lệ': amount/total_income*100 if total_income > 0 else 0
                    })
                # Tiết kiệm theo mục tiêu
                for category, amount in savings_by_category.items():
                    category_data.append({
                        'Loại': 'Tiết kiệm',
                        'Danh Mục': category,
                        'Số Tiền': amount,
                        'Tỷ Lệ': amount/total_savings*100 if total_savings > 0 else 0
                    })
                
                df_category = pd.DataFrame(category_data)
                df_category.to_excel(writer, sheet_name='Chi Tiêu Theo Danh Mục', index=False)
                
                # Định dạng Sheet Chi Tiêu Theo Danh Mục
                worksheet = writer.sheets['Chi Tiêu Theo Danh Mục']
                for col_num, value in enumerate(df_category.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('C:C', 15, money_format)
                worksheet.set_column('D:D', 10)
                worksheet.set_column('A:B', 20)

                # 4. Sheet Tài Sản
                if self.account_var.get() == "Tất cả tài khoản":
                    accounts = Account.get_all()
                else:
                    accounts = [next(acc for acc in Account.get_all() 
                               if acc.name == self.account_var.get())]
                
                loans = Loan.get_all()
                savings = Saving.get_all()
                
                # Filter loans and savings for selected account
                if self.account_var.get() != "Tất cả tài khoản":
                    account = accounts[0]
                    loans = [loan for loan in loans 
                            if loan.from_account_id == account.account_id 
                            or loan.to_account_id == account.account_id]
                    savings = [saving for saving in savings 
                             if saving.account_id == account.account_id]
                
                # Tài khoản
                account_data = [{
                    'Loại': 'Tài khoản',
                    'Tên': acc.name,
                    'Số Dư': acc.balance
                } for acc in accounts]
                
                # Khoản vay
                loan_data = [{
                    'Loại': loan.type,
                    'Tên': f"{loan.lender_name} -> {loan.borrower_name}",
                    'Số Dư': loan.remaining_principal
                } for loan in loans]
                
                # Tiết kiệm
                saving_data = [{
                    'Loại': 'Tiết kiệm',
                    'Tên': saving.name,
                    'Số Dư': saving.current_amount
                } for saving in savings]
                
                df_assets = pd.DataFrame(account_data + loan_data + saving_data)
                df_assets.to_excel(writer, sheet_name='Tài Sản', index=False)
                
                # Định dạng Sheet Tài Sản
                worksheet = writer.sheets['Tài Sản']
                for col_num, value in enumerate(df_assets.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('C:C', 15, money_format)
                worksheet.set_column('A:B', 30)

            # Thông báo thành công
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo Excel thành công!\nĐường dẫn: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất Excel: {str(e)}")