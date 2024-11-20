import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models.saving import Saving
from models.account import Account

class SavingsView:
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        
    def show(self):
        self.create_title()
        self.create_buttons()
        self.show_savings_list()
        
    def create_title(self):
        title = ctk.CTkLabel(
            self.parent,
            text="Quản Lý Tiết Kiệm",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(pady=10)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="🎯 Thêm Mục Tiêu Mới",
            command=self.show_add_dialog,
            font=("Helvetica", 13, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Chỉnh Sửa",
            command=self.edit_selected_goal,
            font=("Helvetica", 13, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Xóa",
            command=self.delete_selected_goal,
            font=("Helvetica", 13, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        delete_btn.pack(side="left", padx=5)
        
    def show_savings_list(self):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(fill="both", padx=20, pady=10, expand=True)
        
        # Tạo scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        # Tạo treeview với scrollbar
        columns = ('ID', 'Tên Mục Tiêu', 'Tài Khoản', 'Số Tiền Mục Tiêu', 
                  'Số Tiền Hiện Tại', 'Tiến Độ', 'Hạn Chót', 'Ghi Chú')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', 
                                yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)
        
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
        
        # Tags cho màu sắc dựa trên tiến độ
        self.tree.tag_configure('low', background='#e74c3c')      # Đỏ cho tiến độ thấp (<30%)
        self.tree.tag_configure('medium', background='#f39c12')   # Cam cho tiến độ trung bình (30-70%)
        self.tree.tag_configure('high', background='#27ae60')     # Xanh lá cho tiến độ cao (>70%)
        self.tree.tag_configure('completed', background='#2ecc71') # Xanh lá đậm cho hoàn thành (100%)
        
        # Cấu hình cột
        self.tree.column('ID', width=50)
        self.tree.column('Tên Mục Tiêu', width=200)
        self.tree.column('Tài Khoản', width=150)
        self.tree.column('Số Tiền Mục Tiêu', width=150)
        self.tree.column('Số Tiền Hiện Tại', width=150)
        self.tree.column('Tiến Độ', width=100)
        self.tree.column('Hạn Chót', width=100)
        self.tree.column('Ghi Chú', width=200)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.refresh_savings_list()
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
    def refresh_savings_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for saving in Saving.get_all():
            # Xác định icon và màu sắc dựa trên tiến độ
            progress = saving.progress
            if progress >= 100:
                tag = 'completed'
                progress_icon = "🎉"  # Icon ăn mừng
            elif progress > 70:
                tag = 'high'
                progress_icon = "🚀"  # Icon tên lửa
            elif progress > 30:
                tag = 'medium'
                progress_icon = "📈"  # Icon tăng trưởng
            else:
                tag = 'low'
                progress_icon = "🎯"  # Icon mục tiêu
            
            self.tree.insert('', 'end', values=(
                saving.goal_id,
                f"{progress_icon} {saving.name}",  # Thêm icon vào tên mục tiêu
                saving.account_name,
                f"{saving.target_amount:,.0f}",
                f"{saving.current_amount:,.0f}",
                f"{saving.progress:.1f}%",
                saving.deadline,
                saving.note
            ), tags=(tag,))
            
    def show_add_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Thêm Mục Tiêu Tiết Kiệm")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Goal Name
        ctk.CTkLabel(dialog, text="Tên Mục Tiêu:", font=("Helvetica", 14, "bold")).pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack(pady=5)
        
        # Account Selection
        ctk.CTkLabel(dialog, text="Tài Khoản:", font=("Helvetica", 14, "bold")).pack(pady=5)
        accounts = Account.get_all()
        account_names = [acc.name for acc in accounts]
        account_var = ctk.StringVar(value=account_names[0] if account_names else "")
        account_menu = ctk.CTkOptionMenu(
            dialog,
            values=account_names,
            variable=account_var,
            width=300
        )
        account_menu.pack(pady=5)
        
        # Target Amount
        ctk.CTkLabel(dialog, text="Số Tiền Mục Tiêu:", font=("Helvetica", 14, "bold")).pack(pady=5)
        target_entry = ctk.CTkEntry(dialog, width=300)
        target_entry.pack(pady=5)
        
        # Initial Amount
        ctk.CTkLabel(dialog, text="Số Tiền Ban Đầu:", font=("Helvetica", 14, "bold")).pack(pady=5)
        initial_entry = ctk.CTkEntry(dialog, width=300)
        initial_entry.pack(pady=5)
        
        # Deadline
        ctk.CTkLabel(dialog, text="Hạn Chót:", font=("Helvetica", 14, "bold")).pack(pady=5)
        deadline_entry = ctk.CTkEntry(dialog, width=300)
        deadline_entry.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        deadline_entry.pack(pady=5)
        
        # Note
        ctk.CTkLabel(dialog, text="Ghi Chú:", font=("Helvetica", 14, "bold")).pack(pady=5)
        note_entry = ctk.CTkEntry(dialog, width=300)
        note_entry.pack(pady=5)
        
        def save_goal():
            try:
                target_amount = float(target_entry.get())
                initial_amount = float(initial_entry.get())
                
                if target_amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền mục tiêu phải lớn hơn 0!")
                    return
                    
                if initial_amount < 0:
                    messagebox.showerror("Lỗi", "Số tiền ban đầu không thể âm!")
                    return
                    
                # Get selected account
                account = next(acc for acc in accounts if acc.name == account_var.get())
                
                # Check if account has enough balance
                if account.balance < initial_amount:
                    messagebox.showerror("Lỗi", "Số dư tài khoản không đủ!")
                    return
                
                # Create new saving goal
                savings = Saving.get_all()
                new_id = len(savings) + 1
                
                saving = Saving(
                    goal_id=new_id,
                    name=name_entry.get(),
                    target_amount=target_amount,
                    current_amount=initial_amount,
                    deadline=deadline_entry.get(),
                    account_id=account.account_id,
                    note=note_entry.get()
                )
                
                # Update account balance
                account.balance -= initial_amount
                account.save()
                
                # Save saving goal
                saving.save()
                
                dialog.destroy()
                self.refresh_savings_list()
                messagebox.showinfo("Thành công", "Đã thêm mục tiêu tiết kiệm mới!")
                
            except ValueError:
                messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ!")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
        save_btn = ctk.CTkButton(
            dialog,
            text="Lưu",
            command=save_goal,
            width=200,
            height=40,
            font=("Helvetica", 14, "bold")
        )
        save_btn.pack(pady=20)
        
    def edit_selected_goal(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn mục tiêu cần chỉnh sửa!")
            return
            
        item = selected_items[0]
        goal_id = int(self.tree.item(item)['values'][0])
        
        savings = Saving.get_all()
        saving = next((s for s in savings if s.goal_id == goal_id), None)
        
        if saving:
            self.show_edit_dialog(saving)
            
    def delete_selected_goal(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn mục tiêu cần xóa!")
            return
            
        item = selected_items[0]
        goal_id = int(self.tree.item(item)['values'][0])
        
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa mục tiêu này?"):
            return
            
        try:
            # Get saving goal info before deleting
            savings = Saving.get_all()
            saving = next((s for s in savings if s.goal_id == goal_id), None)
            
            if saving:
                # Return money to account
                account = Account.get_by_id(saving.account_id)
                if account:
                    account.balance += saving.current_amount
                    account.save()
                
                # Delete saving goal
                Saving.delete(goal_id)
                self.refresh_savings_list()
                messagebox.showinfo("Thành công", 
                                  f"Đã xóa mục tiêu và hoàn lại {saving.current_amount:,.0f} VND "
                                  f"vào tài khoản {account.name}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa mục tiêu: {str(e)}")