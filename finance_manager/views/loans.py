import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from models.loan import Loan, LoanPayment
from config.settings import PAYMENT_PERIODS, INTEREST_TYPES, LOAN_STATUSES
from .dialog import Dialog
from models.account import Account

class LoansView:
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        self.payments_tree = None
        
    def show(self):
        # Xóa nội dung cũ
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        self.create_title()
        self.create_buttons()
        self.show_loans_list()
        
    def create_title(self):
        title = ctk.CTkLabel(
            self.parent,
            text="Quản Lý Vay & Cho Vay",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(pady=10)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="💸 Thêm Khoản Vay Mới",
            command=self.show_add_dialog,
            font=("Helvetica", 13, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Chỉnh Sửa",
            command=self.edit_selected_loan,
            font=("Helvetica", 13, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        edit_btn.pack(side="left", padx=5)
        
        add_payment_btn = ctk.CTkButton(
            button_frame,
            text="💰 Thêm Thanh Toán",
            command=self.add_payment_to_selected,
            font=("Helvetica", 13, "bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        add_payment_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Xóa",
            command=self.delete_selected_loan,
            font=("Helvetica", 13, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        delete_btn.pack(side="left", padx=5)
        
    def show_loans_list(self):
        # Frame chính
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", padx=20, pady=10, expand=True)
        
        # Frame cho danh sách khoản vay
        loans_frame = ctk.CTkFrame(main_frame)
        loans_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tạo scrollbar cho danh sách khoản vay
        scrollbar = ttk.Scrollbar(loans_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Tạo treeview cho danh sách khoản vay
        columns = ('ID', 'Loại', 'Người Cho Vay', 'Người Vay', 'Số Tiền', 'Còn Lại', 
                  'Lãi Suất', 'Kỳ Hạn', 'Loại Lãi', 'Ngày Bắt Đầu', 'Ngày Đến Hạn', 
                  'Trạng Thái', 'Tiền Lãi', 'Tổng Phải Trả')
        self.tree = ttk.Treeview(loans_frame, columns=columns, show='headings', 
                                yscrollcommand=scrollbar.set)
        
        # Style cho Treeview
        style = ttk.Style()
        style.configure("Treeview",
                       font=('Helvetica', 11),
                       rowheight=35,
                       background="#2c3e50",
                       foreground="white",
                       fieldbackground="#2c3e50")
        
        style.configure("Treeview.Heading",
                       font=('Helvetica', 12, 'bold'),
                       background="#34495e",
                       foreground="white")
        
        # Tags cho màu sắc
        self.tree.tag_configure('borrow', background='#e74c3c')    # Đỏ cho khoản vay
        self.tree.tag_configure('lend', background='#2ecc71')      # Xanh lá cho cho vay
        self.tree.tag_configure('overdue', background='#c0392b')   # Đỏ đậm cho quá hạn
        self.tree.tag_configure('completed', background='#27ae60') # Xanh lá đậm cho đã trả
        
        self.refresh_loans_list()
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame cho lịch sử thanh toán
        payments_frame = ctk.CTkFrame(main_frame)
        payments_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Label cho phần lịch sử thanh toán
        payments_label = ctk.CTkLabel(
            payments_frame,
            text="Lịch Sử Thanh Toán",
            font=("Helvetica", 16, "bold")
        )
        payments_label.pack(pady=5)
        
        # Tạo scrollbar cho lịch sử thanh toán
        payments_scrollbar = ttk.Scrollbar(payments_frame)
        payments_scrollbar.pack(side="right", fill="y")
        
        # Tạo treeview cho lịch sử thanh toán
        payment_columns = ('ID', 'Ngày Thanh Toán', 'Số Tiền', 'Tiền Gốc', 'Tiền Lãi', 'Còn Nợ', 'Ghi Chú')
        self.payments_tree = ttk.Treeview(payments_frame, columns=payment_columns, 
                                        show='headings', yscrollcommand=payments_scrollbar.set)
        
        payments_scrollbar.config(command=self.payments_tree.yview)
        
        # Cấu hình các cột cho lịch sử thanh toán
        self.payments_tree.heading('ID', text='ID')
        self.payments_tree.heading('Ngày Thanh Toán', text='Ngày Thanh Toán')
        self.payments_tree.heading('Số Tiền', text='Số Tiền')
        self.payments_tree.heading('Tiền Gốc', text='Tiền Gốc')
        self.payments_tree.heading('Tiền Lãi', text='Tiền Lãi')
        self.payments_tree.heading('Còn Nợ', text='Còn Nợ')
        self.payments_tree.heading('Ghi Chú', text='Ghi Chú')
        
        self.payments_tree.column('ID', width=50)
        self.payments_tree.column('Ngày Thanh Toán', width=150)
        self.payments_tree.column('Số Tiền', width=150)
        self.payments_tree.column('Tiền Gốc', width=150)
        self.payments_tree.column('Tiền Lãi', width=150)
        self.payments_tree.column('Còn Nợ', width=150)
        self.payments_tree.column('Ghi Chú', width=200)
        
        self.payments_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
    def refresh_loans_list(self):
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Thêm dữ liệu mới
        loans = Loan.get_all()
        for loan in loans:
            # Kiểm tra trạng thái đến hạn
            loan.check_due_status()
            
            # Tính lãi hiện tại
            interest_info = loan.calculate_interest()
            accrued_interest = interest_info['accrued_interest']
            
            # Chọn icon và tag dựa vào loại và trạng thái
            if loan.type == "Vay tiền":
                icon = "💸"  # Icon tiền bay
                tag = 'borrow'
            else:  # Cho vay
                icon = "💰"  # Icon túi tiền
                tag = 'lend'
                
            # Thêm tag cho trạng thái
            if loan.status == "Quá hạn":
                tag = 'overdue'
                status_icon = "⚠️"  # Icon cảnh báo
            elif loan.status == "Đã trả":
                tag = 'completed'
                status_icon = "✅"  # Icon hoàn thành
            else:
                status_icon = "⏳"  # Icon đồng hồ cát
            
            self.tree.insert('', 'end', values=(
                loan.loan_id,
                f"{icon} {loan.type}",
                loan.lender_name,
                loan.borrower_name,
                f"{loan.amount:,.0f}",
                f"{loan.remaining_principal:,.0f}",
                f"{loan.interest_rate}%",
                loan.payment_period,
                loan.interest_type,
                loan.start_date,
                loan.due_date,
                f"{status_icon} {loan.status}",
                f"{accrued_interest:,.0f}",
                f"{loan.remaining_principal + accrued_interest:,.0f}"
            ), tags=(tag,))
            
    def refresh_payments_list(self, loan_id):
        # Xóa dữ liệu cũ
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
            
        # Style cho payments tree
        style = ttk.Style()
        style.configure("Payments.Treeview",
                       font=('Helvetica', 11),
                       rowheight=35,
                       background="#2c3e50",
                       foreground="white",
                       fieldbackground="#2c3e50")
        
        # Tags cho màu sắc thanh toán
        self.payments_tree.tag_configure('payment', background='#3498db')  # Xanh dương cho thanh toán
        
        # Lấy khoản vay
        loans = Loan.get_all()
        loan = next((l for l in loans if l.loan_id == loan_id), None)
        
        if loan:
            # Thêm dữ liệu thanh toán mới
            payments = loan.get_payments()
            remaining = loan.amount  # Số tiền ban đầu
            
            for payment in payments:
                remaining -= payment.principal_amount  # Trừ tiền gốc đã trả
                self.payments_tree.insert('', 'end', values=(
                    payment.payment_id,
                    payment.payment_date,
                    f"💵 {payment.amount:,.0f}",  # Icon tiền mặt
                    f"{payment.principal_amount:,.0f}",
                    f"{payment.interest_amount:,.0f}",
                    f"{remaining:,.0f}",
                    payment.note
                ), tags=('payment',))

    def on_loan_selected(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            loan_id = int(self.tree.item(selected_items[0])['values'][0])
            self.refresh_payments_list(loan_id)
        
    def show_add_dialog(self):
        dialog = Dialog(self.parent, "Thêm Khoản Vay Mới")
        
        # Loan Type
        type_frame = ctk.CTkFrame(dialog.main_frame)
        type_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(type_frame, text="Loại:").pack(pady=5)
        type_var = ctk.StringVar(value="Vay tiền")
        type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=["Vay tiền", "Cho vay"],
            variable=type_var
        )
        type_menu.pack(pady=5)
        
        # Lender Name
        lender_frame = ctk.CTkFrame(dialog.main_frame)
        lender_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(lender_frame, text="Người Cho Vay:").pack(pady=5)
        lender_entry = ctk.CTkEntry(lender_frame)
        lender_entry.pack(pady=5)
        
        # Borrower Name
        borrower_frame = ctk.CTkFrame(dialog.main_frame)
        borrower_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(borrower_frame, text="Người Vay:").pack(pady=5)
        borrower_entry = ctk.CTkEntry(borrower_frame)
        borrower_entry.pack(pady=5)
        
        # Amount
        amount_frame = ctk.CTkFrame(dialog.main_frame)
        amount_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(amount_frame, text="Số Tiền:").pack(pady=5)
        amount_entry = ctk.CTkEntry(amount_frame)
        amount_entry.pack(pady=5)
        
        # Interest Rate
        interest_frame = ctk.CTkFrame(dialog.main_frame)
        interest_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(interest_frame, text="Lãi Suất (%/năm):").pack(pady=5)
        interest_entry = ctk.CTkEntry(interest_frame)
        interest_entry.pack(pady=5)
        
        # Interest Type
        interest_type_frame = ctk.CTkFrame(dialog.main_frame)
        interest_type_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(interest_type_frame, text="Loại Lãi:").pack(pady=5)
        interest_type_var = ctk.StringVar(value=INTEREST_TYPES[0])
        interest_type_menu = ctk.CTkOptionMenu(
            interest_type_frame,
            values=INTEREST_TYPES,
            variable=interest_type_var
        )
        interest_type_menu.pack(pady=5)
        
        # Payment Period
        period_frame = ctk.CTkFrame(dialog.main_frame)
        period_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(period_frame, text="Kỳ Hạn:").pack(pady=5)
        period_var = ctk.StringVar(value=PAYMENT_PERIODS[0])
        period_menu = ctk.CTkOptionMenu(
            period_frame,
            values=PAYMENT_PERIODS,
            variable=period_var
        )
        period_menu.pack(pady=5)
        
        # Start Date
        start_date_frame = ctk.CTkFrame(dialog.main_frame)
        start_date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(start_date_frame, text="Ngày Bắt Đầu:").pack(pady=5)
        start_date_entry = ctk.CTkEntry(start_date_frame)
        start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        start_date_entry.pack(pady=5)
        
        # Due Date
        due_date_frame = ctk.CTkFrame(dialog.main_frame)
        due_date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(due_date_frame, text="Ngày Đến Hạn:").pack(pady=5)
        due_date_entry = ctk.CTkEntry(due_date_frame)
        due_date_entry.pack(pady=5)
        
        # Note
        note_frame = ctk.CTkFrame(dialog.main_frame)
        note_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(note_frame, text="Ghi Chú:").pack(pady=5)
        note_entry = ctk.CTkEntry(note_frame)
        note_entry.pack(pady=5)
        
        def save_loan():
            try:
                # Validate input
                amount = float(amount_entry.get())
                interest_rate = float(interest_entry.get())
                
                if amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                    return
                    
                if interest_rate < 0:
                    messagebox.showerror("Lỗi", "Lãi suất không thể âm!")
                    return
                
                # Create new loan
                loans = Loan.get_all()
                new_id = len(loans) + 1
                
                loan = Loan(
                    loan_id=new_id,
                    type=type_var.get(),
                    lender_name=lender_entry.get(),
                    borrower_name=borrower_entry.get(),
                    amount=amount,
                    interest_rate=interest_rate,
                    start_date=start_date_entry.get(),
                    due_date=due_date_entry.get(),
                    payment_period=period_var.get(),
                    interest_type=interest_type_var.get(),
                    note=note_entry.get()
                )
                
                loan.save()
                dialog.destroy()
                self.refresh_loans_list()
                messagebox.showinfo("Thành công", "Đã thêm khoản vay mới!")
                
            except ValueError:
                messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ!")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
        save_btn = ctk.CTkButton(
            dialog.main_frame,
            text="Lưu",
            command=save_loan
        )
        save_btn.pack(pady=20)
        
    def update_account_labels(self, loan_type: str, lender_label: ctk.CTkLabel, borrower_label: ctk.CTkLabel):
        """Cập nhật nhãn cho các tài khoản dựa trên loại khoản vay"""
        if loan_type == "Cho vay":
            lender_label.configure(text="Tài Khoản Cho Vay:")
            borrower_label.configure(text="Tài Khoản Nhận Tiền:")
        else:  # Vay tiền
            lender_label.configure(text="Tài Khoản Cho Vay:")
            borrower_label.configure(text="Tài Khoản Vay:")
        
    def show_add_payment_dialog(self, loan):
        dialog = Dialog(self.parent, "Thêm Thanh Toán")
        
        # Payment Amount
        amount_frame = ctk.CTkFrame(dialog.main_frame)
        amount_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(amount_frame, text="Số Tiền Thanh Toán:").pack(pady=5)
        amount_entry = ctk.CTkEntry(amount_frame)
        amount_entry.pack(pady=5)
        
        # Current Interest
        interest_info = loan.calculate_interest()
        accrued_interest = interest_info['accrued_interest']
        
        info_frame = ctk.CTkFrame(dialog.main_frame)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Tiền lãi hiện tại: {accrued_interest:,.0f} VND",
            font=("Helvetica", 12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Tiền gốc còn lại: {loan.remaining_principal:,.0f} VND",
            font=("Helvetica", 12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Tổng cần thanh toán: {(loan.remaining_principal + accrued_interest):,.0f} VND",
            font=("Helvetica", 12, "bold")
        ).pack(pady=5)
        
        # Payment Date
        date_frame = ctk.CTkFrame(dialog.main_frame)
        date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(date_frame, text="Ngày Thanh Toán:").pack(pady=5)
        date_entry = ctk.CTkEntry(date_frame)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)
        
        # Note
        note_frame = ctk.CTkFrame(dialog.main_frame)
        note_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(note_frame, text="Ghi Chú:").pack(pady=5)
        note_entry = ctk.CTkEntry(note_frame)
        note_entry.pack(pady=5)
        
        def save_payment():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền thanh toán phải lớn hơn 0!")
                    return
                    
                # Tính toán tiền lãi và tiền gốc
                interest_info = loan.calculate_interest(date_entry.get())
                accrued_interest = interest_info['accrued_interest']
                
                # Nếu số tiền thanh toán nhỏ hơn tiền lãi, tất cả đều trả cho lãi
                if amount <= accrued_interest:
                    interest_amount = amount
                    principal_amount = 0
                else:
                    # Trả hết tiền lãi trước, phần còn lại tr gốc
                    interest_amount = accrued_interest
                    principal_amount = amount - accrued_interest
                
                # Add payment
                loan.add_payment(
                    amount=amount,
                    payment_date=date_entry.get(),
                    principal_amount=principal_amount,
                    interest_amount=interest_amount,
                    note=note_entry.get()
                )
                
                dialog.destroy()
                self.refresh_loans_list()
                self.refresh_payments_list(loan.loan_id)
                messagebox.showinfo("Thành công", 
                                  f"Đã thanh toán:\n"
                                  f"- Tiền gốc: {principal_amount:,.0f} VND\n"
                                  f"- Tiền lãi: {interest_amount:,.0f} VND\n"
                                  f"- Tổng cộng: {amount:,.0f} VND\n"
                                  f"- Còn nợ: {loan.remaining_principal:,.0f} VND")
                
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
        # Save Button
        save_btn = ctk.CTkButton(
            dialog.main_frame,
            text="Thanh Toán",
            command=save_payment
        )
        save_btn.pack(pady=20)
        
    def add_payment_to_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoản vay cần thanh toán!")
            return
            
        item = selected_items[0]
        loan_id = int(self.tree.item(item)['values'][0])
        
        loans = Loan.get_all()
        loan = next((l for l in loans if l.loan_id == loan_id), None)
        
        if loan:
            if loan.status == "Đã trả":
                messagebox.showwarning("Cảnh báo", "Khoản vay này đã được thanh toán đầy đủ!")
                return
            self.show_add_payment_dialog(loan)
            
    def delete_selected_loan(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoản vay cần xóa!")
            return
            
        item = selected_items[0]
        loan_id = int(self.tree.item(item)['values'][0])
        loan_info = self.tree.item(item)['values']  # Lấy thông tin khoản vay từ tree
        
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa khoản vay này?\n\n"
                              f"Thông tin khoản vay:\n"
                              f"- Loại: {loan_info[1]}\n"
                              f"- Người cho vay: {loan_info[2]}\n"
                              f"- Người vay: {loan_info[3]}\n"
                              f"- Số tiền: {loan_info[4]}\n"
                              f"- Còn lại: {loan_info[5]}"):
            return
            
        try:
            # Xóa khoản vay và các thanh toán liên quan
            if Loan.delete(loan_id):
                # Refresh cả danh sách khoản vay và lịch sử thanh toán
                self.refresh_loans_list()
                # Clear lịch sử thanh toán bằng cách xóa tất cả items trong payments_tree
                if self.payments_tree:
                    for item in self.payments_tree.get_children():
                        self.payments_tree.delete(item)
                messagebox.showinfo("Thành công", "Đã xóa khoản vay và lịch sử thanh toán thành công!")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy khoản vay để xóa!")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa khoản vay: {str(e)}")
        
    def edit_selected_loan(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoản vay cần chỉnh sửa!")
            return
            
        item = selected_items[0]
        loan_id = int(self.tree.item(item)['values'][0])
        
        # Lấy thông tin khoản vay
        loans = Loan.get_all()
        loan = next((l for l in loans if l.loan_id == loan_id), None)
        
        if loan:
            self.show_edit_dialog(loan)
            
    def show_edit_dialog(self, loan):
        dialog = Dialog(self.parent, "Chỉnh Sửa Khoản Vay")
        
        # Loan Type (readonly)
        type_frame = ctk.CTkFrame(dialog.main_frame)
        type_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(type_frame, text="Loại:").pack(pady=5)
        ctk.CTkLabel(type_frame, text=loan.type).pack(pady=5)
        
        # Lender Name
        lender_frame = ctk.CTkFrame(dialog.main_frame)
        lender_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(lender_frame, text="Người Cho Vay:").pack(pady=5)
        lender_entry = ctk.CTkEntry(lender_frame)
        lender_entry.insert(0, loan.lender_name)
        lender_entry.pack(pady=5)
        
        # Borrower Name
        borrower_frame = ctk.CTkFrame(dialog.main_frame)
        borrower_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(borrower_frame, text="Người Vay:").pack(pady=5)
        borrower_entry = ctk.CTkEntry(borrower_frame)
        borrower_entry.insert(0, loan.borrower_name)
        borrower_entry.pack(pady=5)
        
        # Amount
        amount_frame = ctk.CTkFrame(dialog.main_frame)
        amount_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(amount_frame, text="Số Tiền:").pack(pady=5)
        amount_entry = ctk.CTkEntry(amount_frame)
        amount_entry.insert(0, str(loan.amount))
        amount_entry.pack(pady=5)
        
        # Interest Rate
        interest_frame = ctk.CTkFrame(dialog.main_frame)
        interest_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(interest_frame, text="Lãi Suất (%/năm):").pack(pady=5)
        interest_entry = ctk.CTkEntry(interest_frame)
        interest_entry.insert(0, str(loan.interest_rate))
        interest_entry.pack(pady=5)
        
        # Interest Type
        interest_type_frame = ctk.CTkFrame(dialog.main_frame)
        interest_type_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(interest_type_frame, text="Loại Lãi:").pack(pady=5)
        interest_type_var = ctk.StringVar(value=loan.interest_type)
        interest_type_menu = ctk.CTkOptionMenu(
            interest_type_frame,
            values=INTEREST_TYPES,
            variable=interest_type_var
        )
        interest_type_menu.pack(pady=5)
        
        # Payment Period
        period_frame = ctk.CTkFrame(dialog.main_frame)
        period_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(period_frame, text="Kỳ Hạn:").pack(pady=5)
        period_var = ctk.StringVar(value=loan.payment_period)
        period_menu = ctk.CTkOptionMenu(
            period_frame,
            values=PAYMENT_PERIODS,
            variable=period_var
        )
        period_menu.pack(pady=5)
        
        # Start Date
        start_date_frame = ctk.CTkFrame(dialog.main_frame)
        start_date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(start_date_frame, text="Ngày Bắt Đầu:").pack(pady=5)
        start_date_entry = ctk.CTkEntry(start_date_frame)
        start_date_entry.insert(0, loan.start_date)
        start_date_entry.pack(pady=5)
        
        # Due Date
        due_date_frame = ctk.CTkFrame(dialog.main_frame)
        due_date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(due_date_frame, text="Ngày Đến Hạn:").pack(pady=5)
        due_date_entry = ctk.CTkEntry(due_date_frame)
        due_date_entry.insert(0, loan.due_date)
        due_date_entry.pack(pady=5)
        
        # Status
        status_frame = ctk.CTkFrame(dialog.main_frame)
        status_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(status_frame, text="Trạng Thái:").pack(pady=5)
        status_var = ctk.StringVar(value=loan.status)
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            values=LOAN_STATUSES,
            variable=status_var
        )
        status_menu.pack(pady=5)
        
        # Note
        note_frame = ctk.CTkFrame(dialog.main_frame)
        note_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(note_frame, text="Ghi Chú:").pack(pady=5)
        note_entry = ctk.CTkEntry(note_frame)
        note_entry.insert(0, loan.note if loan.note else "")
        note_entry.pack(pady=5)
        
        def save_changes():
            try:
                # Validate input
                try:
                    amount = float(amount_entry.get())
                    if amount <= 0:
                        messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
                    return
                    
                try:
                    interest_rate = float(interest_entry.get())
                    if interest_rate < 0:
                        messagebox.showerror("Lỗi", "Lãi suất không thể âm!")
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Lãi suất không hợp lệ!")
                    return
                
                # Validate dates
                try:
                    start_date = datetime.strptime(start_date_entry.get(), "%Y-%m-%d")
                    due_date = datetime.strptime(due_date_entry.get(), "%Y-%m-%d")
                    if due_date <= start_date:
                        messagebox.showerror("Lỗi", "Ngày đến hạn phải sau ngày bắt đầu!")
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ (YYYY-MM-DD)!")
                    return
                
                # Update loan
                loan.lender_name = lender_entry.get()
                loan.borrower_name = borrower_entry.get()
                loan.amount = amount
                loan.interest_rate = interest_rate
                loan.interest_type = interest_type_var.get()
                loan.payment_period = period_var.get()
                loan.start_date = start_date_entry.get()
                loan.due_date = due_date_entry.get()
                loan.status = status_var.get()
                loan.note = note_entry.get()
                
                loan.save()
                
                dialog.destroy()
                self.refresh_loans_list()
                messagebox.showinfo("Thành công", "Đã cập nhật khoản vay thành công!")
                
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
        save_btn = ctk.CTkButton(
            dialog.main_frame,
            text="Lưu Thay Đổi",
            command=save_changes
        )
        save_btn.pack(pady=20)
        