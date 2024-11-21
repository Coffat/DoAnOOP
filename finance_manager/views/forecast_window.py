import customtkinter as ctk
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import locale

class ForecastWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Dự báo tài chính")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # Thiết lập style cơ bản cho matplotlib
        plt.style.use('default')
        
        try:
            locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'vi_VN')
            except locale.Error:
                locale.setlocale(locale.LC_ALL, '')
        
        # Tạo các widget cho giao diện
        self.create_widgets()
        
    def create_widgets(self):
        # Frame chính
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Label tiêu đề với icon
        self.title_label = ctk.CTkLabel(
            header_frame, 
            text="🔮 Dự Báo Tài Chính Tương Lai", 
            font=("Helvetica", 28, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Lập kế hoạch tài chính và theo dõi mục tiêu của bạn",
            font=("Helvetica", 14)
        )
        self.subtitle_label.pack()

        # Content frame
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10)
        
        # Left panel for inputs (30% width)
        left_panel = ctk.CTkFrame(content_frame, width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=10)
        left_panel.pack_propagate(False)
        
        # Input section title
        input_title = ctk.CTkLabel(
            left_panel,
            text="📝 Thông Tin Dự Báo",
            font=("Helvetica", 18, "bold")
        )
        input_title.pack(pady=10)
        
        # Create input fields
        self.create_input_fields(left_panel)
        
        # Right panel for results (70% width)
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="left", fill="both", expand=True, pady=10)
        
        # Tạo frame container cho chart và details
        right_container = ctk.CTkFrame(right_panel)
        right_container.pack(fill="both", expand=True)
        
        # Chart frame (chiếm 70% chiều cao)
        self.chart_frame = ctk.CTkFrame(right_container)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Details frame (chiếm 30% chiều cao)
        details_container = ctk.CTkFrame(right_container, height=200)  # Set height cho frame
        details_container.pack(fill="x", padx=10, pady=(5, 0))
        details_container.pack_propagate(False)  # Ngăn frame co lại
        
        # Frame cho nội dung chi tiết
        self.details_frame = ctk.CTkFrame(details_container)
        self.details_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def create_input_fields(self, parent):
        # Frame cho các trường nhập liệu
        input_container = ctk.CTkFrame(parent)
        input_container.pack(fill="x", padx=20, pady=10)
        
        # Style cho labels và entries
        label_font = ("Helvetica", 12)
        entry_width = 200
        
        # Thu nhập hiện tại
        self.create_input_group(input_container, "💰 Thu nhập hàng tháng:", "income_entry", "0", label_font, entry_width)
        
        # Chi tiêu hiện tại
        self.create_input_group(input_container, "💸 Chi tiêu hàng tháng:", "expense_entry", "0", label_font, entry_width)
        
        # Tăng trưởng dự kiến
        self.create_input_group(input_container, "📈 Tăng trưởng hàng năm (%):", "growth_entry", "5", label_font, entry_width)
        
        # Thời gian dự báo
        period_frame = ctk.CTkFrame(input_container)
        period_frame.pack(fill="x", pady=10)
        
        period_label = ctk.CTkLabel(period_frame, text="⏳ Thời gian dự báo (tháng):", font=label_font)
        period_label.pack(anchor="w", pady=(0, 5))
        
        self.period_var = ctk.StringVar(value="12")
        periods = ["6", "12", "24", "36", "60"]
        self.period_option = ctk.CTkOptionMenu(
            period_frame,
            values=periods,
            variable=self.period_var,
            width=entry_width
        )
        self.period_option.pack(anchor="w")
        
        # Button frame
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Nút tạo dự báo
        self.update_button = ctk.CTkButton(
            button_frame,
            text="🔮 Tạo Dự Báo",
            command=self.update_forecast,
            font=("Helvetica", 14, "bold"),
            height=45,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.update_button.pack(fill="x", pady=(0, 10))
        
        # Nút làm mới
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 Làm Mới",
            command=self.reset_inputs,
            font=("Helvetica", 14),
            height=45,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        )
        self.reset_button.pack(fill="x")

    def create_input_group(self, parent, label_text, entry_name, default_value, label_font, entry_width):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(frame, text=label_text, font=label_font)
        label.pack(anchor="w", pady=(0, 5))
        
        entry = ctk.CTkEntry(frame, width=entry_width)
        entry.pack(anchor="w")
        entry.insert(0, default_value)
        
        setattr(self, entry_name, entry)

    def reset_inputs(self):
        self.income_entry.delete(0, 'end')
        self.income_entry.insert(0, "0")
        self.expense_entry.delete(0, 'end')
        self.expense_entry.insert(0, "0")
        self.growth_entry.delete(0, 'end')
        self.growth_entry.insert(0, "5")
        self.period_var.set("12")
        
        # Xóa biểu đồ và thông tin chi tiết
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        for widget in self.details_frame.winfo_children():
            widget.destroy()

    def format_currency(self, amount):
        """Format số tiền theo định dạng tiền tệ"""
        try:
            return locale.currency(amount, grouping=True, symbol='VND')
        except locale.Error:
            # Fallback nếu locale không hỗ trợ currency
            return f"{amount:,.0f} VND"

    def show_error_dialog(self, message):
        """Hiển thị dialog lỗi tự tạo thay vì dùng CTkMessagebox"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Lỗi")
        error_window.geometry("400x200")
        
        # Đặt cửa sổ lỗi ở giữa cửa sổ chính
        error_window.transient(self)
        error_window.grab_set()
        
        # Icon và message
        ctk.CTkLabel(
            error_window,
            text="⚠️",
            font=("Helvetica", 48)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_window,
            text=message,
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        # Nút OK
        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=100
        ).pack(pady=10)

    def update_forecast(self):
        try:
            # Xóa nội dung cũ
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            for widget in self.details_frame.winfo_children():
                widget.destroy()

            # Lấy và kiểm tra giá trị đầu vào
            monthly_income = float(self.income_entry.get().replace(',', ''))
            monthly_expense = float(self.expense_entry.get().replace(',', ''))
            annual_growth = float(self.growth_entry.get().replace(',', ''))
            months = int(self.period_var.get())

            if monthly_income <= 0:
                raise ValueError("Thu nhập phải lớn hơn 0")
            if monthly_expense < 0:
                raise ValueError("Chi tiêu không được âm")
            if annual_growth < -100:
                raise ValueError("Tăng trưởng không được nhỏ hơn -100%")

            # Tạo dữ liệu dự báo
            months_range = list(range(months + 1))
            monthly_growth = annual_growth / 100 / 12

            # Tính toán dự báo
            income_forecast = [monthly_income * (1 + monthly_growth) ** i for i in months_range]
            expense_forecast = [monthly_expense * (1 + monthly_growth/2) ** i for i in months_range]
            savings_forecast = [i - e for i, e in zip(income_forecast, expense_forecast)]

            # Điều chỉnh kích thước biểu đồ nhỏ hơn nữa
            fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)  # Giảm kích thước xuống (6, 3.5)
            
            # Thiết lập style cho biểu đồ
            ax.set_facecolor('#ffffff')
            fig.patch.set_facecolor('#ffffff')
            
            # Thêm lưới đơn giản
            ax.grid(True, linestyle='--', alpha=0.15, color='#666666', which='major')
            ax.grid(False, which='minor')
            
            # Vẽ vùng tiết kiệm
            ax.fill_between(months_range, income_forecast, expense_forecast, 
                           alpha=0.08, color='#2ecc71')
            
            # Vẽ các đường chính với kích thước nhỏ hơn
            line_income = ax.plot(months_range, income_forecast, 
                                color='#2ecc71', label='Thu nhập', 
                                marker='o', linewidth=1.5, markersize=4,  # Giảm kích thước marker
                                markerfacecolor='white', markeredgewidth=1)[0]
            
            line_expense = ax.plot(months_range, expense_forecast, 
                                 color='#e74c3c', label='Chi tiêu', 
                                 marker='s', linewidth=1.5, markersize=4,
                                 markerfacecolor='white', markeredgewidth=1)[0]
            
            line_savings = ax.plot(months_range, savings_forecast, 
                                 color='#3498db', label='Tiết kiệm', 
                                 marker='^', linewidth=1.5, markersize=4,
                                 markerfacecolor='white', markeredgewidth=1)[0]

            # Thêm nhãn với font size nhỏ hơn
            for i in [0, len(months_range)-1]:
                if income_forecast[i] > 0:
                    ax.annotate(f'{income_forecast[i]/1e6:.1f}M', 
                               (months_range[i], income_forecast[i]),
                               textcoords="offset points", xytext=(0,6),
                               ha='center', va='bottom',
                               bbox=dict(boxstyle='round,pad=0.2', 
                                        fc='#2ecc71', ec='none', alpha=0.2),
                               fontsize=7)
                
                if expense_forecast[i] > 0:
                    ax.annotate(f'{expense_forecast[i]/1e6:.1f}M',
                               (months_range[i], expense_forecast[i]),
                               textcoords="offset points", xytext=(0,-10),
                               ha='center', va='top',
                               bbox=dict(boxstyle='round,pad=0.2', 
                                        fc='#e74c3c', ec='none', alpha=0.2),
                               fontsize=7)

            # Tùy chỉnh trục và tiêu đề với font size nhỏ hơn
            ax.set_xlabel('Thời gian (tháng)', fontsize=8, labelpad=6)
            ax.set_ylabel('Số tiền (VND)', fontsize=8, labelpad=6)
            ax.set_title('Biểu Đồ Dự Báo Tài Chính', fontsize=10, pad=10)

            # Format trục y
            def format_money(x, p):
                if x >= 1e9:
                    return f'{x/1e9:.1f}B'
                elif x >= 1e6:
                    return f'{x/1e6:.1f}M'
                else:
                    return f'{x:,.0f}'
            
            ax.yaxis.set_major_formatter(plt.FuncFormatter(format_money))
            
            # Tùy chỉnh nhãn trục x
            x_labels = ['HT' if i == 0 else f'T{i}' for i in months_range]
            plt.xticks(months_range, x_labels, rotation=45, fontsize=7)
            plt.yticks(fontsize=7)
            
            # Tùy chỉnh legend nhỏ gọn hơn
            legend = ax.legend(
                loc='upper center',
                bbox_to_anchor=(0.5, -0.25),
                ncol=3,
                fancybox=True,
                shadow=True,
                framealpha=0.9,
                edgecolor='#dddddd',
                fontsize=7,
                handlelength=1,
                handleheight=0.8,
                handletextpad=0.4,
                columnspacing=0.8
            )
            
            # Điều chỉnh layout
            plt.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.28)
            
            # Thêm watermark nhỏ hơn
            fig.text(0.95, 0.02, 'Finance Manager',
                    fontsize=6, color='#999999',
                    ha='right', va='bottom',
                    alpha=0.4, style='italic')
            
            # Thêm viền mỏng cho biểu đồ
            for spine in ax.spines.values():
                spine.set_edgecolor('#dddddd')
                spine.set_linewidth(0.3)
            
            # Hiển thị biểu đồ trong frame với padding nhỏ hơn
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True, padx=8, pady=8)

            # Hiển thị thông tin chi tiết
            self.show_forecast_details(months, income_forecast, expense_forecast, savings_forecast)

        except ValueError as e:
            self.show_error_dialog(f"Vui lòng kiểm tra lại các giá trị nhập vào!\n{str(e)}")
        except Exception as e:
            self.show_error_dialog(f"Có lỗi xảy ra: {str(e)}")

    def show_forecast_details(self, months, income, expense, savings):
        # Tạo frame cho thông tin chi tiết
        details_container = ctk.CTkFrame(self.details_frame)
        details_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tính toán các chỉ số
        total_savings = sum(savings)
        avg_monthly_savings = total_savings / months if months > 0 else 0
        final_monthly_income = income[-1]
        final_monthly_expense = expense[-1]
        savings_rate = (final_monthly_income - final_monthly_expense) / final_monthly_income * 100 if final_monthly_income > 0 else 0
        
        # Hiển thị các chỉ số
        metrics = [
            ("💰 Thu nhập cuối kỳ:", self.format_currency(final_monthly_income)),
            ("💸 Chi tiêu cuối kỳ:", self.format_currency(final_monthly_expense)),
            ("💵 Tiết kiệm TB/tháng:", self.format_currency(avg_monthly_savings)),
            ("🏦 Tổng tiết kiệm:", self.format_currency(total_savings)),
            ("📊 Tỷ lệ tiết kiệm:", f"{savings_rate:.1f}%")
        ]
        
        # Tạo grid 2x3 cho metrics
        for i, (label, value) in enumerate(metrics):
            frame = ctk.CTkFrame(details_container)
            frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="nsew")
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=("Helvetica", 12)
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                frame,
                text=value,
                font=("Helvetica", 14, "bold")
            ).pack(side="right", padx=10, pady=5)

        # Cấu hình grid
        details_container.grid_columnconfigure(0, weight=1)
        details_container.grid_columnconfigure(1, weight=1)

    def format_currency(self, amount):
        try:
            return f"{amount:,.0f} VND"
        except:
            return "0 VND"