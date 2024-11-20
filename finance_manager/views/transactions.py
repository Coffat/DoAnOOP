import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from finance_manager.models.transaction import Transaction
from finance_manager.models.account import Account
from finance_manager.config.settings import EXPENSE_CATEGORIES, INCOME_CATEGORIES
from finance_manager.models.saving import Saving
from .dialog import Dialog

class TransactionsView:
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        self.dialog = None
        
    def show(self):
        # Xóa nội dung cũ
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        self.create_title()
        self.create_add_button()
        self.show_transactions_list()
        
    def create_title(self):
        title = ctk.CTkLabel(
            self.parent,
            text="Quản Lý Giao Dịch",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
    def create_add_button(self):
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(pady=10)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="💰 Thêm Giao Dịch Mới",
            command=self.show_add_dialog,
            font=("Helvetica", 13, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Chỉnh Sửa",
            command=self.edit_selected_transaction,
            font=("Helvetica", 13, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Xóa",
            command=self.delete_selected_transaction,
            font=("Helvetica", 13, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        delete_btn.pack(side="left", padx=5)
        
    def show_transactions_list(self):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(fill="both", padx=20, pady=10, expand=True)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        # Tạo treeview với scrollbar
        columns = ('ID', 'Ngày', 'Loại', 'Số Tiền', 'Danh Mục', 'Tài Khoản', 'Ghi Chú')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', 
                                yscrollcommand=scrollbar.set, height=20)
        
        scrollbar.config(command=self.tree.yview)
        
        # Cấu hình các cột
        self.tree.heading('ID', text='ID')
        self.tree.heading('Ngày', text='Ngày')
        self.tree.heading('Loại', text='Loại')
        self.tree.heading('Số Tiền', text='Số Tiền')
        self.tree.heading('Danh Mục', text='Danh Mục')
        self.tree.heading('Tài Khoản', text='Tài Khoản')
        self.tree.heading('Ghi Chú', text='Ghi Chú')
        
        # Đặt độ rộng cột phù hợp
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Ngày', width=100, minwidth=100)
        self.tree.column('Loại', width=100, minwidth=100)
        self.tree.column('Số Tiền', width=150, minwidth=150)
        self.tree.column('Danh Mục', width=200, minwidth=200)
        self.tree.column('Tài Khoản', width=150, minwidth=150)
        self.tree.column('Ghi Chú', width=300, minwidth=300)
        
        # Tạo style cho Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                       font=('Helvetica', 11),
                       rowheight=30,
                       background="#2c3e50",  # Màu nền tối
                       foreground="white",     # Màu chữ trắng
                       fieldbackground="#2c3e50")  # Màu nền cho các ô
        
        style.configure("Treeview.Heading",
                       font=('Helvetica', 12, 'bold'),
                       background="#34495e",   # Màu nền tiêu đề
                       foreground="white")     # Màu chữ tiêu đề
        
        # Tạo tags cho màu sắc
        self.tree.tag_configure('income', background='#27ae60')    # Xanh lá cho thu nhập
        self.tree.tag_configure('expense', background='#c0392b')   # Đỏ cho chi tiêu  
        self.tree.tag_configure('transfer', background='#2980b9')  # Xanh dương cho chuyển khoản
        self.tree.tag_configure('saving', background='#f39c12')    # Cam cho tiết kiệm
        
        self.refresh_transactions_list()
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
    def refresh_transactions_list(self):
        """Cập nhật lại danh sách giao dịch"""
        # Xóa dữ liệu cũ
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Lấy mapping tài khoản
            accounts = {acc.account_id: acc.name for acc in Account.get_all()}
            
            # Thêm dữ liệu mới
            transactions = Transaction.get_all()
            transactions.sort(key=lambda x: x.transaction_id, reverse=True)
            
            for i, trans in enumerate(transactions):
                # Thêm icon cho từng loại giao dịch
                if trans.type == 'Thu nhập':
                    icon = "📈"  # Icon tăng
                    tag = 'income'
                elif trans.type == 'Chi tiêu':
                    icon = "📉"  # Icon giảm
                    tag = 'expense'
                elif trans.type == 'Chuyển tiền':
                    icon = "↔️"  # Icon 2 chiều
                    tag = 'transfer'
                else:  # Gửi tiết kiệm
                    icon = "🏦"  # Icon ngân hàng
                    tag = 'saving'
                
                item = self.tree.insert('', 'end', values=(
                    trans.transaction_id,
                    trans.date,
                    f"{icon} {trans.type}",  # Thêm icon vào loại giao dịch
                    f"{trans.amount:,.0f}",
                    trans.category,
                    accounts.get(trans.account_id, ""),
                    trans.note
                ))
                
                # Thêm tags cho màu sắc
                self.tree.item(item, tags=(tag,))
            
    def show_add_dialog(self):
        self.dialog = Dialog(self.parent, "Thêm Giao Dịch Mới", size="600x800")  # Lưu dialog vào instance
        
        # Title
        title_label = ctk.CTkLabel(
            self.dialog.main_frame,
            text="THÊM GIAO DỊCH MỚI",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Main Content Frame
        content_frame = ctk.CTkFrame(self.dialog.main_frame)
        content_frame.pack(fill="x", padx=20, pady=10)
        
        # 1. Transaction Type Section
        type_frame = self.create_section_frame(content_frame, "1. Loại Giao Dịch")
        self.type_var = ctk.StringVar(value="Chi tiêu")
        type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=["Chi tiêu", "Thu nhập", "Chuyển tiền", "Gửi tiết kiệm"],
            variable=self.type_var,
            width=300,
            command=self.on_transaction_type_change
        )
        type_menu.pack(pady=10)

        # 2. Amount Section
        amount_frame = self.create_section_frame(content_frame, "2. Số Tiền")
        self.amount_entry = ctk.CTkEntry(
            amount_frame, 
            width=300,
            placeholder_text="Nhập số tiền..."
        )
        self.amount_entry.pack(pady=10)

        # 3. Account Section
        account_frame = self.create_section_frame(content_frame, "3. Tài Khoản")
        accounts = Account.get_all()
        account_names = [acc.name for acc in accounts]
        
        self.source_account_var = ctk.StringVar(value=account_names[0] if account_names else "")
        self.source_account_menu = ctk.CTkOptionMenu(
            account_frame,
            values=account_names,
            variable=self.source_account_var,
            width=300,
            command=self.on_account_change
        )
        self.source_account_menu.pack(pady=10)

        # Target Account Frame (for transfers)
        self.target_account_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ctk.CTkLabel(
            self.target_account_frame, 
            text="Tài Khoản Nhận",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        
        self.target_account_var = ctk.StringVar(value=account_names[0] if account_names else "")
        self.target_account_menu = ctk.CTkOptionMenu(
            self.target_account_frame,
            values=account_names,
            variable=self.target_account_var,
            width=300
        )
        self.target_account_menu.pack(pady=10)

        # 4. Category Frame
        self.category_frame = self.create_section_frame(content_frame, "4. Danh Mục")
        self.category_var = ctk.StringVar(value=EXPENSE_CATEGORIES[0])
        self.category_menu = ctk.CTkOptionMenu(
            self.category_frame,
            values=EXPENSE_CATEGORIES,
            variable=self.category_var,
            width=300
        )
        self.category_menu.pack(pady=10)

        # 5. Savings Frame
        self.savings_frame = self.create_section_frame(content_frame, "4. Mục Tiêu Tiết Kiệm")
        self.savings_var = ctk.StringVar()
        self.savings_menu = ctk.CTkOptionMenu(
            self.savings_frame,
            values=[""],
            variable=self.savings_var,
            width=300
        )
        self.savings_menu.pack(pady=10)
        
        # Savings Info Label
        self.goal_info_label = ctk.CTkLabel(
            self.savings_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.goal_info_label.pack(pady=5)

        # 6. Note Section
        note_frame = self.create_section_frame(content_frame, "5. Ghi Chú")
        self.note_entry = ctk.CTkEntry(
            note_frame, 
            width=300,
            placeholder_text="Nhập ghi chú..."
        )
        self.note_entry.pack(pady=10)

        # Save Button
        save_btn = ctk.CTkButton(
            self.dialog.main_frame,
            text="Lưu Giao Dịch",
            command=self.save_transaction,
            width=200,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        save_btn.pack(pady=20)

        # Show initial frame based on transaction type
        self.on_transaction_type_change("Chi tiêu")

    def create_section_frame(self, parent, title):
        """Helper function để tạo section frame với tiêu đề"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        
        return frame

    def on_account_change(self, *args):
        """Cập nhật danh sách mục tiêu tiết kiệm khi thay đổi tài khoản"""
        if self.type_var.get() == "Gửi tiết kiệm":
            self.update_savings_goals()
            
    def update_savings_goals(self, *args):
        """Cập nhật danh sách mục tiêu tiết kiệm của tài khoản được chọn"""
        try:
            account = next(acc for acc in Account.get_all() 
                         if acc.name == self.source_account_var.get())
            
            # Lấy danh sách mục tiêu tiết kiệm của tài khoản
            savings = Saving.get_all()
            account_savings = [s for s in savings if s.account_id == account.account_id 
                             and s.current_amount < s.target_amount]
            
            if account_savings:
                goal_names = [s.name for s in account_savings]
                self.savings_menu.configure(values=goal_names)
                self.savings_menu.set(goal_names[0])
                
                # Hiển thị thông tin mục tiêu đầu tiên
                saving = account_savings[0]
                self.show_saving_info(saving)
            else:
                self.savings_menu.configure(values=["Không có mục tiêu chưa hoàn thành"])
                self.savings_menu.set("Không có mục tiêu chưa hoàn thành")
                self.goal_info_label.configure(text="")
                
        except Exception as e:
            print(f"Error in update_savings_goals: {str(e)}")
            
    def show_saving_info(self, saving):
        """Hiển thị thông tin chi tiết về mục tiêu tiết kiệm"""
        remaining = saving.target_amount - saving.current_amount
        self.goal_info_label.configure(
            text=f"Số tiền mục tiêu: {saving.target_amount:,.0f} VND\n"
                 f"Đã tiết kiệm: {saving.current_amount:,.0f} VND\n"
                 f"Còn cần tiết kiệm: {remaining:,.0f} VND\n"
                 f"Tiến độ hiện tại: {saving.progress:.1f}%\n"
                 f"Hạn chót: {saving.deadline}"
        )
            
    def on_savings_goal_change(self, goal_name):
        """Xử lý khi người dùng chọn mục tiêu tiết kiệm khác"""
        try:
            if goal_name not in ["Không có mục tiêu", "Không có mục tiêu chưa hoàn thành"]:
                account = next(acc for acc in Account.get_all() 
                             if acc.name == self.source_account_var.get())
                saving = next(s for s in Saving.get_all() 
                            if s.account_id == account.account_id and s.name == goal_name)
                self.show_saving_info(saving)
        except Exception as e:
            print(f"Error in on_savings_goal_change: {str(e)}")

    def save_transaction(self):
        try:
            # Validate amount
            if not self.amount_entry.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập số tiền!")
                return
                
            try:
                amount = float(self.amount_entry.get())
                if amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
                return
            
            trans_type = self.type_var.get()
            
            # Lấy thông tin tài khoản nguồn
            source_account = next(acc for acc in Account.get_all() 
                                if acc.name == self.source_account_var.get())
            
            # Xử lý theo loại giao dịch
            if trans_type == "Chuyển tiền":
                # Kiểm tra tài khoản nguồn và đích không được trùng nhau
                if self.source_account_var.get() == self.target_account_var.get():
                    messagebox.showerror("Lỗi", "Tài khoản nguồn và đích không được trùng nhau!")
                    return
                    
                # Lấy tài khoản đích
                target_account = next(acc for acc in Account.get_all() 
                                    if acc.name == self.target_account_var.get())
                
                # Kiểm tra nếu có tài khoản tiền mặt
                if source_account.type == "Tiền mặt" or target_account.type == "Tiền mặt":
                    # Tạo giao dịch với ghi chú error
                    transactions = Transaction.get_all()
                    new_id = len(transactions) + 1
                    
                    transaction = Transaction(
                        transaction_id=new_id,
                        date=datetime.now().strftime("%Y-%m-%d"),
                        type=trans_type,
                        amount=amount,
                        category=f"Chuyển tiền từ {source_account.name} đến {target_account.name}",
                        account_id=source_account.account_id,
                        note="error"
                    )
                    transaction.save()
                    
                    # Thông báo lỗi
                    messagebox.showerror(
                        "Thông báo",
                        "Giao dịch không thành công!\n\n"
                        "Lý do: Không thể chuyển khoản với tài khoản tiền mặt.\n"
                        "Giao dịch đã được lưu với ghi chú 'error'."
                    )
                    
                else:
                    # Kiểm tra số dư tài khoản nguồn
                    if source_account.balance < amount:
                        messagebox.showerror("Lỗi", "Số dư tài khoản không đủ!")
                        return
                        
                    # Cập nhật số dư các tài khoản
                    source_account.balance -= amount
                    target_account.balance += amount
                    
                    source_account.save()
                    target_account.save()
                    
                    # Tạo giao dịch chuyển tiền thành công
                    transactions = Transaction.get_all()
                    new_id = len(transactions) + 1
                    
                    transaction = Transaction(
                        transaction_id=new_id,
                        date=datetime.now().strftime("%Y-%m-%d"),
                        type=trans_type,
                        amount=amount,
                        category=f"Chuyển tiền từ {source_account.name} đến {target_account.name}",
                        account_id=source_account.account_id,
                        note=self.note_entry.get()
                    )
                    transaction.save()
                    
                    messagebox.showinfo("Thành công", "Đã chuyển tiền thành công!")
                
            elif trans_type == "Gửi tiết kiệm":
                # Kiểm tra có chọn mục tiêu tiết kiệm không
                if not hasattr(self, 'savings_var') or not self.savings_var.get():
                    messagebox.showerror("Lỗi", "Vui lòng chọn mục tiêu tiết kiệm!")
                    return
                
                # Kiểm tra số dư tài khoản
                if source_account.balance < amount:
                    messagebox.showerror("Lỗi", "Số dư tài khoản không đủ!")
                    return
                    
                # Lấy mục tiêu tiết kiệm
                saving = next((s for s in Saving.get_all() 
                             if s.name == self.savings_var.get()), None)
                
                if not saving:
                    messagebox.showerror("Lỗi", "Không tìm thấy mục tiêu tiết kiệm!")
                    return
                
                # Cập nhật số dư tài khoản và số tiền tiết kiệm
                source_account.balance -= amount
                saving.current_amount += amount
                
                source_account.save()
                saving.save()
                
                # Tạo giao dịch tiết kiệm
                transactions = Transaction.get_all()
                new_id = len(transactions) + 1
                
                transaction = Transaction(
                    transaction_id=new_id,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    type=trans_type,
                    amount=amount,
                    category=saving.name,
                    account_id=source_account.account_id,
                    note=self.note_entry.get()
                )
                transaction.save()
                
            else:  # Thu nhập hoặc Chi tiêu
                # Kiểm tra danh mục
                if not hasattr(self, 'category_var') or not self.category_var.get():
                    messagebox.showerror("Lỗi", "Vui lòng chọn danh mục!")
                    return
                
                # Kiểm tra số dư với giao dịch chi tiêu
                if trans_type == "Chi tiêu" and source_account.balance < amount:
                    messagebox.showerror("Lỗi", "Số dư tài khoản không đủ!")
                    return
                
                # Cập nhật số dư tài khoản
                if trans_type == "Chi tiêu":
                    source_account.balance -= amount
                else:  # Thu nhập
                    source_account.balance += amount
                    
                source_account.save()
                
                # Tạo giao dịch
                transactions = Transaction.get_all()
                new_id = len(transactions) + 1
                
                transaction = Transaction(
                    transaction_id=new_id,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    type=trans_type,
                    amount=amount,
                    category=self.category_var.get(),
                    account_id=source_account.account_id,
                    note=self.note_entry.get()
                )
                transaction.save()
            
            # Đóng dialog và refresh danh sách
            if self.dialog:
                self.dialog.withdraw()  # Ẩn dialog trước
                self.dialog.destroy()   # Sau đó hủy
                self.dialog = None      # Reset biến dialog
                
            # Refresh danh sách giao dịch
            self.refresh_transactions_list()
            
            # Hiển thị thông báo thành công
            messagebox.showinfo("Thành công", "Đã thêm giao dịch mới!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        
    def edit_selected_transaction(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cnh báo", "Vui lòng chọn giao dịch cần chỉnh sửa!")
            return
            
        item = selected_items[0]
        transaction_id = int(self.tree.item(item)['values'][0])
        
        # Lấy thông tin giao dịch
        transactions = Transaction.get_all()
        transaction = next((t for t in transactions if t.transaction_id == transaction_id), None)
        
        if transaction:
            self.show_edit_dialog(transaction)
            
    def show_edit_dialog(self, transaction):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Chỉnh Sửa Giao Dịch")
        dialog.geometry("500x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Transaction Type (disabled for editing)
        ctk.CTkLabel(dialog, text="Loại Giao Dịch:").pack(pady=5)
        type_var = ctk.StringVar(value=transaction.type)
        type_label = ctk.CTkLabel(dialog, text=transaction.type)
        type_label.pack(pady=5)
        
        # Amount
        ctk.CTkLabel(dialog, text="Số Tiền:").pack(pady=5)
        amount_entry = ctk.CTkEntry(dialog)
        amount_entry.insert(0, str(transaction.amount))
        amount_entry.pack(pady=5)
        
        # Account Frame
        account_frame = ctk.CTkFrame(dialog)
        account_frame.pack(pady=5, fill='x', padx=20)
        
        # Get accounts
        accounts = Account.get_all()
        account_names = [acc.name for acc in accounts]
        current_account = next(acc.name for acc in accounts if acc.account_id == transaction.account_id)
        
        if transaction.type == "Chuyển tiền":
            # Source Account (readonly for transfer)
            ctk.CTkLabel(account_frame, text="Tài Khoản Chuyển:").pack(pady=5)
            source_label = ctk.CTkLabel(account_frame, text=current_account)
            source_label.pack(pady=5)
            
            # Target Account (from category)
            target_account_name = transaction.category.split(" đến ")[1]
            ctk.CTkLabel(account_frame, text="Tài Khoản Nhận:").pack(pady=5)
            target_label = ctk.CTkLabel(account_frame, text=target_account_name)
            target_label.pack(pady=5)
            
        else:
            # Regular transaction account
            ctk.CTkLabel(account_frame, text="Tài Khoản:").pack(pady=5)
            account_var = ctk.StringVar(value=current_account)
            account_menu = ctk.CTkOptionMenu(
                account_frame,
                values=account_names,
                variable=account_var
            )
            account_menu.pack(pady=5)
            
            # Category for non-transfer transactions
            ctk.CTkLabel(dialog, text="Danh Mục:").pack(pady=5)
            categories = EXPENSE_CATEGORIES if transaction.type == "Chi tiêu" else INCOME_CATEGORIES
            category_var = ctk.StringVar(value=transaction.category)
            category_menu = ctk.CTkOptionMenu(
                dialog,
                values=categories,
                variable=category_var
            )
            category_menu.pack(pady=5)
        
        # Date
        ctk.CTkLabel(dialog, text="Ngày Giao Dịch:").pack(pady=5)
        date_entry = ctk.CTkEntry(dialog)
        date_entry.insert(0, transaction.date)
        date_entry.pack(pady=5)
        
        # Note
        ctk.CTkLabel(dialog, text="Ghi Chú:").pack(pady=5)
        note_entry = ctk.CTkEntry(dialog)
        note_entry.insert(0, transaction.note)
        note_entry.pack(pady=5)
        
        def save_changes():
            try:
                # Validate amount
                new_amount = float(amount_entry.get())
                if new_amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                    return
                
                if transaction.type == "Chuyển tiền":
                    # Handle transfer transaction
                    source_account = Account.get_by_id(transaction.account_id)
                    target_account_name = transaction.category.split(" đến ")[1]
                    target_account = next(acc for acc in accounts if acc.name == target_account_name)
                    
                    # Reverse old transfer
                    source_account.balance += transaction.amount
                    target_account.balance -= transaction.amount
                    
                    # Apply new transfer
                    if source_account.balance < new_amount:
                        messagebox.showerror("Lỗi", "Số dư tài khoản không đủ!")
                        return
                        
                    source_account.balance -= new_amount
                    target_account.balance += new_amount
                    
                    source_account.save()
                    target_account.save()
                    
                    # Update transaction
                    transaction.amount = new_amount
                    transaction.date = date_entry.get()
                    transaction.note = note_entry.get()
                    
                else:
                    # Handle regular transaction
                    old_account = Account.get_by_id(transaction.account_id)
                    new_account = next(acc for acc in accounts if acc.name == account_var.get())
                    
                    # Reverse old transaction
                    if transaction.type == "Chi tiêu":
                        old_account.balance += transaction.amount
                    else:  # Thu nhập
                        old_account.balance -= transaction.amount
                    
                    # Apply new transaction
                    if transaction.type == "Chi tiêu" and new_account.balance < new_amount:
                        messagebox.showerror("Lỗi", "Số dư tài khoản không đủ!")
                        return
                        
                    if transaction.type == "Chi tiêu":
                        new_account.balance -= new_amount
                    else:  # Thu nhập
                        new_account.balance += new_amount
                    
                    old_account.save()
                    if new_account.account_id != old_account.account_id:
                        new_account.save()
                    
                    # Update transaction
                    transaction.amount = new_amount
                    transaction.date = date_entry.get()
                    transaction.category = category_var.get()
                    transaction.account_id = new_account.account_id
                    transaction.note = note_entry.get()
                
                transaction.save()
                dialog.destroy()
                self.refresh_transactions_list()
                messagebox.showinfo("Thành công", "Đã cập nhật giao dịch thành công!")
                
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
        save_btn = ctk.CTkButton(dialog, text="Lưu Thay Đổi", command=save_changes)
        save_btn.pack(pady=20)
        
    def delete_selected_transaction(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giao dịch cần xóa!")
            return
            
        item = selected_items[0]
        transaction_id = int(self.tree.item(item)['values'][0])
        
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa giao dịch này?"):
            return
            
        try:
            # Lấy thông tin giao dịch trước khi xóa
            transactions = Transaction.get_all()
            transaction = next((t for t in transactions if t.transaction_id == transaction_id), None)
            
            if transaction:
                account = Account.get_by_id(transaction.account_id)
                
                if transaction.type == "Chi tiêu":
                    # Hoàn lại tiền cho tài khoản chi tiêu
                    account.balance += transaction.amount
                elif transaction.type == "Thu nhập":
                    # Trừ lại tiền thu nhập
                    account.balance -= transaction.amount
                elif transaction.type == "Chuyển tiền":
                    # Lấy thông tin tài khoản nguồn và đích từ category
                    source_account_name = transaction.category.split(" từ ")[1].split(" đến ")[0]
                    target_account_name = transaction.category.split(" đến ")[1]
                    
                    source_account = next(acc for acc in Account.get_all() if acc.name == source_account_name)
                    target_account = next(acc for acc in Account.get_all() if acc.name == target_account_name)
                    
                    # Hoàn lại tiền cho tài khoản nguồn và trừ tiền tài khoản đích
                    source_account.balance += transaction.amount
                    target_account.balance -= transaction.amount
                    
                    source_account.save()
                    target_account.save()
                
                # Lưu thay đổi số dư tài khoản
                if transaction.type != "Chuyển tiền":
                    account.save()
                
                # Xóa giao dịch
                Transaction.delete(transaction_id)
                self.refresh_transactions_list()
                
                # Hiển thị thông báo chi tiết
                if transaction.type == "Chuyển tiền":
                    messagebox.showinfo("Thành công", 
                                      f"Đã xóa giao dịch và hoàn lại tiền:\n"
                                      f"- Tài khoản {source_account_name}: +{transaction.amount:,.0f} VND\n"
                                      f"- Tài khoản {target_account_name}: -{transaction.amount:,.0f} VND")
                else:
                    messagebox.showinfo("Thành công", 
                                      f"Đã xóa giao dịch và {'hoàn lại' if transaction.type == 'Chi tiêu' else 'trừ'} "
                                      f"{transaction.amount:,.0f} VND cho tài khoản {account.name}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa giao dịch: {str(e)}") 

    def on_transaction_type_change(self, trans_type):
        """Cập nhật giao diện dựa trên loại giao dịch được chọn"""
        # Hide all optional frames first
        self.category_frame.pack_forget()
        self.target_account_frame.pack_forget()
        self.savings_frame.pack_forget()
        
        # Validate transfer if needed
        if trans_type == "Chuyển tiền":
            # Lấy thông tin tài khoản nguồn
            accounts = Account.get_all()
            source_account = next(acc for acc in accounts 
                                if acc.name == self.source_account_var.get())
            
            # Kiểm tra nếu là tài khoản tiền mặt
            if source_account.type == "Tiền mặt":
                messagebox.showerror(
                    "Thông báo",
                    "Không thể thực hiện chuyển khoản!\n\n"
                    "Lý do: Tài khoản tiền mặt không thể thực hiện chuyển khoản.\n"
                    "Vui lòng sử dụng tài khoản ngân hàng hoặc ví điện tử để thực hiện giao dịch này."
                )
                # Reset lại loại giao dịch
                self.type_var.set("Chi tiêu")
                return
            
            # Show target account frame
            self.target_account_frame.pack(pady=5, fill='x', padx=20)
            
        elif trans_type == "Chi tiêu":
            self.category_menu.configure(values=EXPENSE_CATEGORIES)
            self.category_var.set(EXPENSE_CATEGORIES[0])
            self.category_frame.pack(pady=5, fill='x', padx=20)
            
        elif trans_type == "Thu nhập":
            self.category_menu.configure(values=INCOME_CATEGORIES)
            self.category_var.set(INCOME_CATEGORIES[0])
            self.category_frame.pack(pady=5, fill='x', padx=20)
            
        else:  # Gửi tiết kiệm
            self.savings_frame.pack(pady=5, fill='x', padx=20)
            self.update_savings_goals() 