import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
import uuid
from models.loan import Loan, PaymentHistory
from utils.loan_manager import LoanManager

class LoanView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.loan_manager = LoanManager()
        self.setup_ui()
        self.load_loans()

    def setup_ui(self):
        # Tạo tabs cho Khoản vay và Khoản cho vay
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.borrowed_tab = self.tab_view.add("Khoản vay")
        self.lent_tab = self.tab_view.add("Khoản cho vay")
        
        # Setup UI cho mỗi tab
        self.setup_borrowed_tab()
        self.setup_lent_tab()

    def setup_borrowed_tab(self):
        # Frame cho form thêm khoản vay
        input_frame = ctk.CTkFrame(self.borrowed_tab)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Các trường nhập liệu
        ctk.CTkLabel(input_frame, text="Người cho vay:").grid(row=0, column=0, padx=5, pady=5)
        self.lender_entry = ctk.CTkEntry(input_frame)
        self.lender_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Số tiền:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ctk.CTkEntry(input_frame)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Lãi suất (%/năm):").grid(row=2, column=0, padx=5, pady=5)
        self.interest_entry = ctk.CTkEntry(input_frame)
        self.interest_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.is_compound = tk.BooleanVar()
        ctk.CTkCheckBox(input_frame, text="Lãi kép", variable=self.is_compound).grid(row=2, column=2, padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Ngày vay:").grid(row=3, column=0, padx=5, pady=5)
        self.start_date_entry = ctk.CTkEntry(input_frame)
        self.start_date_entry.grid(row=3, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ctk.CTkLabel(input_frame, text="Ngày đến hạn:").grid(row=4, column=0, padx=5, pady=5)
        self.due_date_entry = ctk.CTkEntry(input_frame)
        self.due_date_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Ghi chú:").grid(row=5, column=0, padx=5, pady=5)
        self.note_entry = ctk.CTkEntry(input_frame)
        self.note_entry.grid(row=5, column=1, padx=5, pady=5)
        
        # Nút thêm khoản vay
        ctk.CTkButton(
            input_frame, 
            text="Thêm khoản vay", 
            command=lambda: self.add_loan("borrowed")
        ).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Bảng hiển thị khoản vay
        self.borrowed_tree = ttk.Treeview(
            self.borrowed_tab,
            columns=("Người cho vay", "Số tiền", "Ngày vay", "Ngày đến hạn", "Còn lại", "Trạng thái"),
            show="headings"
        )
        
        for col in self.borrowed_tree["columns"]:
            self.borrowed_tree.heading(col, text=col)
            self.borrowed_tree.column(col, width=100)
            
        self.borrowed_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Nút chức năng
        button_frame = ctk.CTkFrame(self.borrowed_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Thêm thanh toán",
            command=self.add_payment_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Xóa khoản vay",
            command=self.delete_loan
        ).pack(side=tk.LEFT, padx=5)

    def setup_lent_tab(self):
        # Tương tự như setup_borrowed_tab nhưng cho khoản cho vay
        pass

    def add_loan(self, loan_type: str):
        try:
            loan = Loan(
                id=str(uuid.uuid4()),
                lender=self.lender_entry.get(),
                borrower="self" if loan_type == "borrowed" else self.borrower_entry.get(),
                amount=float(self.amount_entry.get()),
                start_date=datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d"),
                due_date=datetime.strptime(self.due_date_entry.get(), "%Y-%m-%d"),
                interest_rate=float(self.interest_entry.get()),
                is_compound=self.is_compound.get(),
                note=self.note_entry.get(),
                is_completed=False,
                type=loan_type,
                payment_history=[]
            )
            
            self.loan_manager.save_loan(loan)
            self.load_loans()
            self.clear_inputs()
            messagebox.showinfo("Thành công", "Đã thêm khoản vay mới!")
            
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def add_payment_dialog(self):
        selected_item = self.borrowed_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khoản vay!")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm thanh toán")
        dialog.geometry("300x200")
        
        ctk.CTkLabel(dialog, text="Số tiền:").pack(pady=5)
        amount_entry = ctk.CTkEntry(dialog)
        amount_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Ghi chú:").pack(pady=5)
        note_entry = ctk.CTkEntry(dialog)
        note_entry.pack(pady=5)
        
        def submit():
            try:
                loan_id = self.borrowed_tree.item(selected_item[0])["values"][0]
                loans = self.loan_manager.load_loans()
                loan = next(loan for loan in loans if loan.id == loan_id)
                
                loan.add_payment(
                    amount=float(amount_entry.get()),
                    date=datetime.now(),
                    note=note_entry.get()
                )
                
                self.loan_manager.save_loan(loan)
                self.load_loans()
                dialog.destroy()
                messagebox.showinfo("Thành công", "Đã thêm thanh toán!")
                
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e))
                
        ctk.CTkButton(dialog, text="Xác nhận", command=submit).pack(pady=10)

    def delete_loan(self):
        selected_item = self.borrowed_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khoản vay!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa khoản vay này?"):
            loan_id = self.borrowed_tree.item(selected_item[0])["values"][0]
            self.loan_manager.delete_loan(loan_id)
            self.load_loans()

    def load_loans(self):
        # Xóa dữ liệu cũ
        for item in self.borrowed_tree.get_children():
            self.borrowed_tree.delete(item)
            
        # Load và hiển thị dữ liệu mới
        loans = self.loan_manager.load_loans()
        
        for loan in loans:
            if loan.type == "borrowed":
                self.borrowed_tree.insert(
                    "",
                    tk.END,
                    values=(
                        loan.lender,
                        f"{loan.amount:,.0f}",
                        loan.start_date.strftime("%Y-%m-%d"),
                        loan.due_date.strftime("%Y-%m-%d"),
                        f"{loan.calculate_remaining_amount():,.0f}",
                        "Đã hoàn thành" if loan.is_completed else "Đang vay"
                    )
                )

    def clear_inputs(self):
        """Xóa nội dung các trường nhập liệu"""
        self.lender_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.interest_entry.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.due_date_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.is_compound.set(False) 