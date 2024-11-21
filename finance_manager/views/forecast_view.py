import customtkinter as ctk
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import locale

class ForecastView:
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        
        # Màu sắc chủ đạo với độ tương phản cao hơn
        self.PRIMARY_COLOR = "#3498db"  # Xanh dương đậm hơn cho tiêu đề và nút chính
        self.HEADER_BG = "#2980b9"      # Màu nền header
        self.INPUT_BG = "#ecf0f1"       # Màu nền nhẹ cho khu vực input
        self.BUTTON_PRIMARY = "#27ae60"  # Xanh lá cho nút chính
        self.BUTTON_SECONDARY = "#7f8c8d" # Xám cho nút phụ
        self.ERROR_COLOR = "#c0392b"     # Đỏ đậm cho thông báo lỗi
        
        try:
            locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'vi_VN')
            except locale.Error:
                locale.setlocale(locale.LC_ALL, '')

    def show(self):
        if self.frame:
            self.frame.destroy()
            
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header với màu nền mới
        header_frame = ctk.CTkFrame(self.frame, fg_color=self.HEADER_BG)
        header_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame, 
            text="🔮 Dự Báo Tài Chính", 
            font=("Helvetica", 24, "bold"),
            text_color="white"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="Lập kế hoạch tài chính và theo dõi mục tiêu của bạn",
            font=("Helvetica", 14),
            text_color="#ecf0f1"  # Màu chữ sáng hơn trên nền tối
        ).pack(pady=(0, 10))

        # Content container với màu nền sáng
        content = ctk.CTkFrame(self.frame, fg_color="white")
        content.pack(fill="both", expand=True, padx=10)
        
        # Left panel với màu nền nhẹ
        left_panel = ctk.CTkFrame(content, width=350, fg_color=self.INPUT_BG)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=10)
        left_panel.pack_propagate(False)
        
        # Input section title với style mới
        input_header = ctk.CTkFrame(left_panel, fg_color=self.PRIMARY_COLOR, height=40)
        input_header.pack(fill="x", pady=(0, 15))
        input_header.pack_propagate(False)
        
        ctk.CTkLabel(
            input_header,
            text="📝 Thông Tin Dự Báo",
            font=("Helvetica", 16, "bold"),
            text_color="white"
        ).pack(expand=True)
        
        self.create_input_section(left_panel)
        
        # Right panel với layout cải tiến
        right_panel = ctk.CTkFrame(content)
        right_panel.pack(side="left", fill="both", expand=True, pady=10)
        
        # Chart area với border và shadow
        chart_container = ctk.CTkFrame(right_panel, fg_color="white")
        chart_container.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        self.chart_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Details area với style mới
        details_container = ctk.CTkFrame(right_panel, height=180, fg_color="#f8f9fa")
        details_container.pack(fill="x", padx=10, pady=(5, 0))
        details_container.pack_propagate(False)
        
        self.details_frame = ctk.CTkFrame(details_container, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def create_input_section(self, parent):
        # Container cho các input
        input_container = ctk.CTkFrame(parent, fg_color="transparent")
        input_container.pack(fill="x", padx=20, pady=10)
        
        # Style cho input fields
        label_font = ("Helvetica", 12)
        entry_width = 250
        
        # Thu nhập hiện tại với style mới
        income_frame = self.create_input_group(
            input_container, 
            "💰 Thu nhập hàng tháng:",
            "income_entry",
            "0",
            label_font,
            entry_width,
            self.PRIMARY_COLOR
        )
        
        # Chi tiêu hiện tại
        expense_frame = self.create_input_group(
            input_container,
            "💸 Chi tiêu hàng tháng:",
            "expense_entry",
            "0",
            label_font,
            entry_width,
            self.PRIMARY_COLOR
        )
        
        # Tăng trưởng dự kiến
        growth_frame = self.create_input_group(
            input_container,
            "📈 Tăng trưởng hàng năm (%):",
            "growth_entry",
            "5",
            label_font,
            entry_width,
            self.PRIMARY_COLOR
        )
        
        # Thời gian dự báo với style mới
        period_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        period_frame.pack(fill="x", pady=15)
        
        # Label với màu chữ đậm hơn
        period_label = ctk.CTkLabel(
            period_frame,
            text="⏳ Thời gian dự báo:",
            font=("Helvetica", 12, "bold"),
            text_color="#2c3e50"  # Màu chữ đậm để dễ nhìn
        )
        period_label.pack(anchor="w", pady=(0, 5))
        
        self.period_var = ctk.StringVar(value="12 tháng")
        periods = ["6 tháng", "12 tháng", "24 tháng", "36 tháng", "60 tháng"]
        
        # Dropdown với style mới
        self.period_option = ctk.CTkOptionMenu(
            period_frame,
            values=periods,
            variable=self.period_var,
            width=250,  # Tăng width cho phù hợp với các input khác
            height=35,  # Tăng height cho dễ nhìn
            fg_color=self.PRIMARY_COLOR,  # Màu nền của dropdown
            button_color=self.PRIMARY_COLOR,  # Màu nút dropdown
            button_hover_color="#2980b9",  # Màu hover của nút
            text_color="white",  # Màu chữ của giá trị được chọn
            dropdown_fg_color="white",  # Màu nền của dropdown menu
            dropdown_hover_color="#f5f6fa",  # Màu hover trong dropdown
            dropdown_text_color="#2c3e50",  # Màu chữ trong dropdown
            font=("Helvetica", 12),  # Font size phù hợp
            anchor="w"  # Căn lề trái cho text
        )
        self.period_option.pack(anchor="w")
        
        # Button frame với style mới
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Nút tạo dự báo với màu mới
        self.update_button = ctk.CTkButton(
            button_frame,
            text="🔮 Tạo Dự Báo",
            command=self.update_forecast,
            font=("Helvetica", 14, "bold"),
            height=45,
            fg_color=self.BUTTON_PRIMARY,
            hover_color="#219a52",  # Màu hover tối hơn
            corner_radius=8,
            text_color="white"
        )
        self.update_button.pack(fill="x", pady=(0, 10))
        
        # Nút làm mới với màu mới
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 Làm Mới",
            command=self.reset_inputs,
            font=("Helvetica", 14),
            height=45,
            fg_color=self.BUTTON_SECONDARY,
            hover_color="#6c7a89",  # Màu hover tối hơn
            corner_radius=8,
            text_color="white"
        )
        self.reset_button.pack(fill="x")

    def create_input_group(self, parent, label_text, entry_name, default_value, label_font, entry_width, accent_color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=label_font,
            text_color="#2c3e50"  # Màu chữ đậm hơn
        )
        label.pack(anchor="w", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            frame,
            width=entry_width,
            height=35,
            corner_radius=8,
            border_color=accent_color,
            fg_color="white",
            text_color="#2c3e50",  # Màu chữ đậm cho dễ đọc
            placeholder_text_color="#95a5a6"  # Màu placeholder nhạt hơn
        )
        entry.pack(anchor="w")
        entry.insert(0, default_value)
        
        setattr(self, entry_name, entry)
        return frame

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
        try:
            return f"{amount:,.0f} VND"
        except:
            return "0 VND"

    def show_error_dialog(self, message):
        error_window = ctk.CTkToplevel(self.frame)
        error_window.title("Lỗi")
        error_window.geometry("400x200")
        error_window.transient(self.frame)
        error_window.grab_set()
        
        # Style mới cho dialog
        error_frame = ctk.CTkFrame(error_window)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=("Helvetica", 48)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_frame,
            text=message,
            font=("Helvetica", 12),
            wraplength=300
        ).pack(pady=10)
        
        ctk.CTkButton(
            error_frame,
            text="Đóng",
            command=error_window.destroy,
            width=100,
            fg_color=self.ERROR_COLOR,
            hover_color="#c0392b"
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
            
            # Sửa cách lấy số tháng từ period_var
            period_str = self.period_var.get()  # Ví dụ: "12 tháng"
            months = int(period_str.split()[0])  # Lấy số từ chuỗi, ví dụ: 12

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

            # Vẽ biểu đồ
            fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
            
            ax.set_facecolor('#ffffff')
            fig.patch.set_facecolor('#ffffff')
            
            ax.grid(True, linestyle='--', alpha=0.15, color='#666666', which='major')
            ax.grid(False, which='minor')
            
            ax.fill_between(months_range, income_forecast, expense_forecast, 
                           alpha=0.08, color='#2ecc71')
            
            line_income = ax.plot(months_range, income_forecast, 
                                color='#2ecc71', label='Thu nhập', 
                                marker='o', linewidth=1.5, markersize=4,
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

            ax.set_xlabel('Thời gian (tháng)', fontsize=8, labelpad=6)
            ax.set_ylabel('Số tiền (VND)', fontsize=8, labelpad=6)
            ax.set_title('Biểu Đồ Dự Báo Tài Chính', fontsize=10, pad=10)

            def format_money(x, p):
                if x >= 1e9:
                    return f'{x/1e9:.1f}B'
                elif x >= 1e6:
                    return f'{x/1e6:.1f}M'
                else:
                    return f'{x:,.0f}'
            
            ax.yaxis.set_major_formatter(plt.FuncFormatter(format_money))
            
            x_labels = ['HT' if i == 0 else f'T{i}' for i in months_range]
            plt.xticks(months_range, x_labels, rotation=45, fontsize=7)
            plt.yticks(fontsize=7)
            
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
            
            plt.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.28)
            
            fig.text(0.95, 0.02, 'Finance Manager',
                    fontsize=6, color='#999999',
                    ha='right', va='bottom',
                    alpha=0.4, style='italic')
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#dddddd')
                spine.set_linewidth(0.3)
            
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
        details_container = ctk.CTkFrame(self.details_frame)
        details_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        total_savings = sum(savings)
        avg_monthly_savings = total_savings / months if months > 0 else 0
        final_monthly_income = income[-1]
        final_monthly_expense = expense[-1]
        savings_rate = (final_monthly_income - final_monthly_expense) / final_monthly_income * 100 if final_monthly_income > 0 else 0
        
        metrics = [
            ("💰 Thu nhập cuối kỳ:", self.format_currency(final_monthly_income)),
            ("💸 Chi tiêu cuối kỳ:", self.format_currency(final_monthly_expense)),
            ("💵 Tiết kiệm TB/tháng:", self.format_currency(avg_monthly_savings)),
            ("🏦 Tổng tiết kiệm:", self.format_currency(total_savings)),
            ("📊 Tỷ lệ tiết kiệm:", f"{savings_rate:.1f}%")
        ]
        
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

        details_container.grid_columnconfigure(0, weight=1)
        details_container.grid_columnconfigure(1, weight=1)