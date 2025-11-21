import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSplitter)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Any

class NutritionChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 控制面板
        control_layout = QHBoxLayout()
        
        # 时间范围选择
        control_layout.addWidget(QLabel("时间范围:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["今日", "本周", "本月", "自定义"])
        self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
        control_layout.addWidget(self.time_range_combo)
        
        # 图表类型选择
        control_layout.addWidget(QLabel("图表类型:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["营养分布饼图", "卡路里趋势图", "营养素对比图", "三餐分析图"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        control_layout.addWidget(self.chart_type_combo)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self.refresh_data)
        control_layout.addWidget(refresh_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 图表区域
        self.chart_group = QGroupBox("营养分析图表")
        chart_layout = QVBoxLayout(self.chart_group)
        
        # 创建matplotlib图表
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        layout.addWidget(self.chart_group)
        
        # 数据表格
        self.data_group = QGroupBox("详细数据")
        data_layout = QVBoxLayout(self.data_group)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels([
            "日期", "总卡路里", "蛋白质(g)", "脂肪(g)", "碳水化合物(g)", "纤维(g)"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        data_layout.addWidget(self.data_table)
        
        layout.addWidget(self.data_group)
        
        # 初始加载数据
        self.refresh_data()
        
    def on_time_range_changed(self, text):
        if text == "自定义":
            # 这里可以添加自定义日期范围选择对话框
            pass
        self.refresh_data()
        
    def refresh_data(self):
        """刷新营养数据"""
        try:
            time_range = self.time_range_combo.currentText()
            
            if time_range == "今日":
                date_str = QDate.currentDate().toString("yyyy-MM-dd")
                self.load_daily_data(date_str)
            elif time_range == "本周":
                self.load_weekly_data()
            elif time_range == "本月":
                self.load_monthly_data()
            else:
                self.load_daily_data(QDate.currentDate().toString("yyyy-MM-dd"))
                
        except Exception as e:
            print(f"刷新数据失败: {e}")
            
    def load_daily_data(self, date_str: str):
        """加载每日营养数据"""
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            response = requests.get(f"{self.parent.api_base_url}/nutrition/daily/{date_str}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.update_daily_table([data])
                self.update_chart()
            else:
                print(f"获取营养数据失败: {response.status_code}")
                
        except Exception as e:
            print(f"加载每日数据失败: {e}")
            
    def load_weekly_data(self):
        """加载本周营养数据"""
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            
            # 获取本周的日期范围
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            
            weekly_data = []
            for i in range(7):
                current_date = start_of_week + timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                
                response = requests.get(f"{self.parent.api_base_url}/nutrition/daily/{date_str}", headers=headers)
                if response.status_code == 200:
                    daily_data = response.json()
                    daily_data['date'] = date_str
                    weekly_data.append(daily_data)
                    
            self.update_weekly_table(weekly_data)
            self.update_chart()
            
        except Exception as e:
            print(f"加载周数据失败: {e}")
            
    def load_monthly_data(self):
        """加载本月营养数据"""
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            
            # 获取本月数据（简化版本，获取最近30天）
            monthly_data = []
            today = datetime.now()
            
            for i in range(30):
                current_date = today - timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                
                response = requests.get(f"{self.parent.api_base_url}/nutrition/daily/{date_str}", headers=headers)
                if response.status_code == 200:
                    daily_data = response.json()
                    daily_data['date'] = date_str
                    monthly_data.append(daily_data)
                    
            self.update_monthly_table(monthly_data)
            self.update_chart()
            
        except Exception as e:
            print(f"加载月数据失败: {e}")
            
    def update_daily_table(self, data: List[Dict[str, Any]]):
        """更新每日数据表格"""
        self.data_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.data_table.setItem(row, 0, QTableWidgetItem(item.get('date', '今日')))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(item.get('total_calories', 0))))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(item.get('total_protein', 0))))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(item.get('total_fat', 0))))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(item.get('total_carbs', 0))))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(item.get('total_fiber', 0))))
            
    def update_weekly_table(self, data: List[Dict[str, Any]]):
        """更新周数据表格"""
        self.data_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.data_table.setItem(row, 0, QTableWidgetItem(item.get('date', '')))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(item.get('total_calories', 0))))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(item.get('total_protein', 0))))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(item.get('total_fat', 0))))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(item.get('total_carbs', 0))))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(item.get('total_fiber', 0))))
            
    def update_monthly_table(self, data: List[Dict[str, Any]]):
        """更新月数据表格"""
        self.data_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.data_table.setItem(row, 0, QTableWidgetItem(item.get('date', '')))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(item.get('total_calories', 0))))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(item.get('total_protein', 0))))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(item.get('total_fat', 0))))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(item.get('total_carbs', 0))))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(item.get('total_fiber', 0))))
            
    def update_chart(self):
        """更新图表显示"""
        chart_type = self.chart_type_combo.currentText()
        
        try:
            if chart_type == "营养分布饼图":
                self.create_nutrition_pie_chart()
            elif chart_type == "卡路里趋势图":
                self.create_calories_trend_chart()
            elif chart_type == "营养素对比图":
                self.create_nutrition_comparison_chart()
            elif chart_type == "三餐分析图":
                self.create_meal_analysis_chart()
                
        except Exception as e:
            print(f"更新图表失败: {e}")
            
    def create_nutrition_pie_chart(self):
        """创建营养分布饼图"""
        self.ax.clear()
        
        # 获取当前数据
        if self.data_table.rowCount() == 0:
            return
            
        # 获取第一行数据（当前选择的时间范围）
        row = 0
        protein = float(self.data_table.item(row, 2).text())
        fat = float(self.data_table.item(row, 3).text())
        carbs = float(self.data_table.item(row, 4).text())
        fiber = float(self.data_table.item(row, 5).text())
        
        # 数据
        labels = ['蛋白质', '脂肪', '碳水化合物', '纤维']
        sizes = [protein, fat, carbs, fiber]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        # 创建饼图
        self.ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        self.ax.set_title('营养素分布图', fontsize=16, fontweight='bold')
        
        self.canvas.draw()
        
    def create_calories_trend_chart(self):
        """创建卡路里趋势图"""
        self.ax.clear()
        
        # 获取表格数据
        dates = []
        calories = []
        
        for row in range(self.data_table.rowCount()):
            date_item = self.data_table.item(row, 0)
            calorie_item = self.data_table.item(row, 1)
            
            if date_item and calorie_item:
                dates.append(date_item.text())
                calories.append(float(calorie_item.text()))
                
        if not dates:
            return
            
        # 创建折线图
        self.ax.plot(dates, calories, marker='o', linewidth=2, markersize=8, color='#4CAF50')
        self.ax.set_title('卡路里摄入趋势', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('日期', fontsize=12)
        self.ax.set_ylabel('卡路里 (kcal)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        self.ax.tick_params(axis='x', rotation=45)
        
        self.canvas.draw()
        
    def create_nutrition_comparison_chart(self):
        """创建营养素对比柱状图"""
        self.ax.clear()
        
        # 获取表格数据
        nutrients = ['蛋白质', '脂肪', '碳水化合物', '纤维']
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        # 获取最新数据
        if self.data_table.rowCount() == 0:
            return
            
        row = 0
        values = [
            float(self.data_table.item(row, 2).text()),  # 蛋白质
            float(self.data_table.item(row, 3).text()),  # 脂肪
            float(self.data_table.item(row, 4).text()),  # 碳水化合物
            float(self.data_table.item(row, 5).text())   # 纤维
        ]
        
        # 创建柱状图
        bars = self.ax.bar(nutrients, values, color=colors, alpha=0.8)
        self.ax.set_title('营养素含量对比', fontsize=16, fontweight='bold')
        self.ax.set_ylabel('含量 (g)', fontsize=12)
        
        # 在柱状图上添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        self.canvas.draw()
        
    def create_meal_analysis_chart(self):
        """创建三餐分析图"""
        self.ax.clear()
        
        # 模拟三餐数据（实际应用中应该从API获取）
        meals = ['早餐', '午餐', '晚餐']
        calories = [400, 600, 500]  # 模拟卡路里数据
        colors = ['#FFB6C1', '#87CEEB', '#98FB98']
        
        # 创建柱状图
        bars = self.ax.bar(meals, calories, color=colors, alpha=0.8)
        self.ax.set_title('三餐卡路里分布', fontsize=16, fontweight='bold')
        self.ax.set_ylabel('卡路里 (kcal)', fontsize=12)
        
        # 在柱状图上添加数值标签
        for bar, calorie in zip(bars, calories):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                        f'{calorie}', ha='center', va='bottom', fontweight='bold')
        
        self.canvas.draw()


class HealthReportWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("健康报告")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 报告内容
        self.report_text = QLabel()
        self.report_text.setStyleSheet("""
            QLabel {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.report_text.setWordWrap(True)
        self.report_text.setText(self.generate_health_report())
        
        layout.addWidget(self.report_text)
        
        # 更新按钮
        update_btn = QPushButton("更新报告")
        update_btn.clicked.connect(self.update_report)
        layout.addWidget(update_btn)
        
        layout.addStretch()
        
    def generate_health_report(self) -> str:
        """生成健康报告"""
        return """
        📊 营养健康分析报告
        
        🎯 总体评价：
        • 您的营养摄入基本均衡，继续保持！
        • 建议增加蔬菜摄入量
        • 注意控制糖分摄入
        
        📈 营养建议：
        • 蛋白质摄入充足，有助于肌肉维持
        • 碳水化合物摄入合理，为身体提供充足能量
        • 建议增加膳食纤维摄入，促进消化健康
        
        ⚠️ 注意事项：
        • 保持每日饮水量充足（8杯水）
        • 适量运动，建议每周150分钟中等强度运动
        • 定期监测体重和血压变化
        
        🥗 推荐食谱：
        • 早餐：燕麦粥配新鲜水果
        • 午餐：烤鸡胸肉配蔬菜沙拉
        • 晚餐：蒸鱼配糙米和蒸蔬菜
        
        报告生成时间：{}
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
    def update_report(self):
        """更新健康报告"""
        # 这里可以添加从API获取最新数据的逻辑
        self.report_text.setText(self.generate_health_report())


# 在主窗口中添加营养图表功能
def add_nutrition_charts_to_main_window(main_window):
    """向主窗口添加营养图表功能"""
    
    # 创建营养图表标签页
    nutrition_chart_widget = QWidget()
    nutrition_layout = QVBoxLayout(nutrition_chart_widget)
    
    # 创建分割器
    splitter = QSplitter(Qt.Orientation.Vertical)
    
    # 添加图表组件
    chart_widget = NutritionChartWidget(main_window)
    splitter.addWidget(chart_widget)
    
    # 添加健康报告组件
    report_widget = HealthReportWidget(main_window)
    splitter.addWidget(report_widget)
    
    # 设置分割器比例
    splitter.setSizes([400, 200])
    
    nutrition_layout.addWidget(splitter)
    
    # 添加到主窗口的标签页
    main_window.tabs.addTab(nutrition_chart_widget, "营养图表")