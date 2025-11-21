import sys
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QLineEdit, QTextEdit, QComboBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, 
                             QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox,
                             QDateEdit, QGroupBox, QSplitter, QListWidget,
                             QListWidgetItem, QCheckBox, QProgressBar, QFrame,
                             QScrollArea, QFileDialog, QMenuBar, QMenu, QStatusBar)
from PyQt6.QtCore import Qt, QTimer, QDate, pyqtSignal, QThread, pyqtSlot, QSettings
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor
from nutrition_charts import add_nutrition_charts_to_main_window

class RecipeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_base_url = "http://localhost:5000/api"
        self.current_user = None
        self.auth_token = None
        self.settings = QSettings("FamilyMealPlanner", "MealPlannerApp")
        self.init_ui()
        self.apply_styles()
        self.load_saved_session()
        
    def init_ui(self):
        self.setWindowTitle("家庭食谱与膳食规划应用")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("欢迎使用家庭食谱与膳食规划应用")
        
        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 创建登录界面
        self.login_widget = self.create_login_widget()
        layout.addWidget(self.login_widget)
        
        # 创建主界面（初始隐藏）
        self.main_widget = self.create_main_widget()
        self.main_widget.setVisible(False)
        layout.addWidget(self.main_widget)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        login_action = QAction('登录', self)
        login_action.triggered.connect(self.show_login)
        file_menu.addAction(login_action)
        
        logout_action = QAction('退出登录', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 标题
        title_label = QLabel("家庭食谱与膳食规划应用")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # 登录表单
        login_group = QGroupBox("用户登录")
        login_layout = QVBoxLayout(login_group)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        username_layout.addWidget(self.username_input)
        login_layout.addLayout(username_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入密码")
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)
        # 记住登录状态
        self.remember_checkbox = QCheckBox("记住登录状态")
        login_layout.addWidget(self.remember_checkbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.login)
        register_btn = QPushButton("注册")
        register_btn.clicked.connect(self.show_register_dialog)
        self.quick_login_btn = QPushButton("快速登录")
        self.quick_login_btn.clicked.connect(self.quick_login)
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        button_layout.addWidget(self.quick_login_btn)
        login_layout.addLayout(button_layout)
        
        layout.addWidget(login_group)
        
        return widget

    def load_saved_session(self):
        try:
            saved_username = self.settings.value("username", "")
            saved_token = self.settings.value("token", "")
            remember = self.settings.value("remember", False, type=bool)
            if saved_username:
                self.username_input.setText(str(saved_username))
            # 快速登录按钮根据是否有token决定可用性
            if hasattr(self, "quick_login_btn"):
                self.quick_login_btn.setEnabled(bool(saved_token))
            if remember and saved_token and saved_username:
                self.auth_token = str(saved_token)
                self.current_user = str(saved_username)
                self.welcome_label.setText(f"欢迎，{self.current_user}！")
                self.login_widget.setVisible(False)
                self.main_widget.setVisible(True)
                self.status_bar.showMessage("已恢复上次登录状态")
                self.load_initial_data()
        except Exception:
            pass
        
    def create_main_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 欢迎信息
        self.welcome_label = QLabel()
        self.welcome_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.welcome_label)
        
        # 创建标签页
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 添加各个功能标签页
        self.tabs.addTab(self.create_recipe_tab(), "食谱管理")
        self.tabs.addTab(self.create_meal_plan_tab(), "膳食规划")
        self.tabs.addTab(self.create_ingredient_tab(), "食材管理")
        self.tabs.addTab(self.create_shopping_list_tab(), "购物清单")
        self.tabs.addTab(self.create_nutrition_tab(), "营养分析")
        
        # 添加营养图表功能
        add_nutrition_charts_to_main_window(self)
        
        return widget
        
    def create_recipe_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 搜索栏
        search_layout = QHBoxLayout()
        self.recipe_search_input = QLineEdit()
        self.recipe_search_input.setPlaceholderText("搜索食谱...")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_recipes)
        recommend_btn = QPushButton("推荐")
        recommend_btn.clicked.connect(self.load_recommended_recipes)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_recipes)
        add_recipe_btn = QPushButton("添加食谱")
        add_recipe_btn.clicked.connect(self.show_add_recipe_dialog)
        
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.recipe_search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(recommend_btn)
        search_layout.addWidget(refresh_btn)
        search_layout.addWidget(add_recipe_btn)
        layout.addLayout(search_layout)
        
        # 食谱表格
        self.recipe_table = QTableWidget()
        self.recipe_table.setColumnCount(8)
        self.recipe_table.setHorizontalHeaderLabels([
            "ID", "名称", "分类", "难度", "准备时间", "烹饪时间", "评分", "操作"
        ])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recipe_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.recipe_table)
        
        return widget
        
    def create_meal_plan_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_layout = QHBoxLayout()
        
        # 日期选择
        control_layout.addWidget(QLabel("选择日期:"))
        self.meal_plan_date = QDateEdit()
        self.meal_plan_date.setDate(QDate.currentDate())
        self.meal_plan_date.dateChanged.connect(self.load_meal_plan)
        control_layout.addWidget(self.meal_plan_date)
        
        # 按钮
        generate_btn = QPushButton("智能生成")
        generate_btn.clicked.connect(self.generate_meal_plan)
        add_meal_btn = QPushButton("添加餐食")
        add_meal_btn.clicked.connect(self.show_add_meal_dialog)
        
        control_layout.addWidget(generate_btn)
        control_layout.addWidget(add_meal_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 餐食计划表格
        self.meal_plan_table = QTableWidget()
        self.meal_plan_table.setColumnCount(6)
        self.meal_plan_table.setHorizontalHeaderLabels([
            "餐次", "食谱名称", "份量", "卡路里", "营养信息", "操作"
        ])
        self.meal_plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.meal_plan_table)
        
        return widget
        
    def create_ingredient_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 搜索和控制
        control_layout = QHBoxLayout()
        self.ingredient_search_input = QLineEdit()
        self.ingredient_search_input.setPlaceholderText("搜索食材...")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_ingredients)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_ingredients)
        add_ingredient_btn = QPushButton("添加食材")
        add_ingredient_btn.clicked.connect(self.show_add_ingredient_dialog)
        
        control_layout.addWidget(QLabel("搜索:"))
        control_layout.addWidget(self.ingredient_search_input)
        control_layout.addWidget(search_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(add_ingredient_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 食材表格
        self.ingredient_table = QTableWidget()
        self.ingredient_table.setColumnCount(7)
        self.ingredient_table.setHorizontalHeaderLabels([
            "ID", "名称", "分类", "数量", "单位", "保质期", "操作"
        ])
        self.ingredient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.ingredient_table)
        
        return widget
        
    def create_shopping_list_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        generate_btn = QPushButton("从膳食计划生成")
        generate_btn.clicked.connect(self.generate_shopping_list)
        add_item_btn = QPushButton("添加物品")
        add_item_btn.clicked.connect(self.show_add_shopping_item_dialog)
        export_btn = QPushButton("导出清单")
        export_btn.clicked.connect(self.export_shopping_list)
        
        control_layout.addWidget(generate_btn)
        control_layout.addWidget(add_item_btn)
        control_layout.addWidget(export_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 购物清单表格
        self.shopping_table = QTableWidget()
        self.shopping_table.setColumnCount(5)
        self.shopping_table.setHorizontalHeaderLabels([
            "物品名称", "数量", "单位", "备注", "操作"
        ])
        self.shopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.shopping_table)
        
        return widget
        
    def create_nutrition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_layout = QHBoxLayout()
        analyze_btn = QPushButton("分析今日营养")
        analyze_btn.clicked.connect(self.analyze_today_nutrition)
        weekly_btn = QPushButton("周报告")
        weekly_btn.clicked.connect(self.show_weekly_report)
        
        control_layout.addWidget(analyze_btn)
        control_layout.addWidget(weekly_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 营养信息显示
        self.nutrition_info = QTextEdit()
        self.nutrition_info.setReadOnly(True)
        self.nutrition_info.setPlaceholderText("营养分析信息将在这里显示...")
        layout.addWidget(self.nutrition_info)
        
        return widget
        
    def apply_styles(self):
        self.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            border: 2px solid #ccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
            border-color: #4CAF50;
            outline: none;
        }
        QTableWidget {
            gridline-color: #ddd;
            background-color: white;
            alternate-background-color: #f9f9f9;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        QTabWidget::pane {
            border: 1px solid #ddd;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #4CAF50;
        }
        """)
        
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码")
            return
            
        try:
            response = requests.post(f"{self.api_base_url}/auth/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.current_user = username
                if self.remember_checkbox.isChecked() and self.auth_token:
                    # 仅保存用户名和令牌，不保存密码
                    self.settings.setValue("username", self.current_user)
                    self.settings.setValue("token", self.auth_token)
                    self.settings.setValue("remember", True)
                    if hasattr(self, "quick_login_btn"):
                        self.quick_login_btn.setEnabled(True)
                
                self.welcome_label.setText(f"欢迎，{username}！")
                self.login_widget.setVisible(False)
                self.main_widget.setVisible(True)
                
                self.status_bar.showMessage("登录成功！")
                self.load_initial_data()
            else:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录失败：{str(e)}")

    def quick_login(self):
        try:
            saved_username = self.settings.value("username", "")
            saved_token = self.settings.value("token", "")
            if saved_username and saved_token:
                self.current_user = str(saved_username)
                self.auth_token = str(saved_token)
                self.welcome_label.setText(f"欢迎，{self.current_user}！")
                self.login_widget.setVisible(False)
                self.main_widget.setVisible(True)
                self.status_bar.showMessage("快速登录成功")
                self.load_initial_data()
            else:
                QMessageBox.information(self, "提示", "暂无保存的登录信息，请先登录并勾选记住登录状态")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"快速登录失败：{str(e)}")
            
    def logout(self):
        self.current_user = None
        self.auth_token = None
        self.login_widget.setVisible(True)
        self.main_widget.setVisible(False)
        self.username_input.clear()
        self.password_input.clear()
        self.status_bar.showMessage("已退出登录")
        # 保留保存的登录信息以便快速登录，不清除设置
        
    def show_login(self):
        self.logout()
        
    def show_register_dialog(self):
        dialog = RegisterDialog(self)
        dialog.exec()
        
    def show_about(self):
        QMessageBox.about(self, "关于", 
                         "家庭食谱与膳食规划应用\n\n"
                         "一个功能完整的食谱管理和膳食规划工具。\n"
                         "支持食谱管理、膳食规划、食材管理、购物清单和营养分析。\n\n"
                         "版本：1.0.0")
        
    def load_initial_data(self):
        self.refresh_recipes()
        self.refresh_ingredients()
        self.load_meal_plan()
        
    def refresh_recipes(self):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/recipes", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    recipes = data.get("recipes") or data.get("data") or []
                elif isinstance(data, list):
                    recipes = data
                else:
                    recipes = []
                self.populate_recipe_table(recipes)
            else:
                QMessageBox.warning(self, "警告", "获取食谱列表失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取食谱列表失败：{str(e)}")
            
    def populate_recipe_table(self, recipes):
        self.recipe_table.setRowCount(len(recipes))
        
        for row, recipe in enumerate(recipes):
            name = recipe.get("name") or recipe.get("title", "")
            prep_time = recipe.get("prep_time") or recipe.get("cooking_time", "")
            cook_time = recipe.get("cook_time") or recipe.get("cooking_time", "")
            difficulty = recipe.get("difficulty", "")
            rating = recipe.get("rating", "")
            category = recipe.get("category", "")
            
            self.recipe_table.setItem(row, 0, QTableWidgetItem(str(recipe.get("id", ""))))
            self.recipe_table.setItem(row, 1, QTableWidgetItem(str(name)))
            self.recipe_table.setItem(row, 2, QTableWidgetItem(str(category)))
            self.recipe_table.setItem(row, 3, QTableWidgetItem(str(difficulty)))
            self.recipe_table.setItem(row, 4, QTableWidgetItem(str(prep_time)))
            self.recipe_table.setItem(row, 5, QTableWidgetItem(str(cook_time)))
            self.recipe_table.setItem(row, 6, QTableWidgetItem(str(rating)))
            
            view_btn = QPushButton("查看")
            view_btn.setFixedHeight(28)
            view_btn.setFixedWidth(68)
            view_btn.clicked.connect(lambda checked, r=recipe: self.view_recipe(r))
            edit_btn = QPushButton("编辑")
            edit_btn.setFixedHeight(28)
            edit_btn.setFixedWidth(68)
            edit_btn.clicked.connect(lambda checked, r=recipe: self.edit_recipe(r))
            del_btn = QPushButton("删除")
            del_btn.setFixedHeight(28)
            del_btn.setFixedWidth(68)
            del_btn.clicked.connect(lambda checked, r=recipe: self.delete_recipe(r))
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.setSpacing(8)
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            btn_container.setMinimumWidth(220)
            self.recipe_table.setCellWidget(row, 7, btn_container)
            self.recipe_table.setRowHeight(row, 40)
            
    def search_recipes(self):
        search_term = self.recipe_search_input.text().strip()
        if not search_term:
            self.refresh_recipes()
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/recipes", params={"search": search_term}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    recipes = data.get("recipes") or data.get("data") or []
                elif isinstance(data, list):
                    recipes = data
                else:
                    recipes = []
                self.populate_recipe_table(recipes)
            else:
                QMessageBox.warning(self, "警告", "搜索食谱失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索食谱失败：{str(e)}")

    def load_recommended_recipes(self):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            params = {"limit": 10}
            term = self.recipe_search_input.text().strip()
            if term:
                params["category"] = term
            response = requests.get(f"{self.api_base_url}/recipes/recommend", params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                recipes = data.get("recipes") or data
                self.populate_recipe_table(recipes)
            else:
                QMessageBox.warning(self, "警告", "获取推荐食谱失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取推荐食谱失败：{str(e)}")
            
    def view_recipe(self, recipe):
        try:
            rid = recipe.get('id')
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            if rid:
                resp = requests.get(f"{self.api_base_url}/recipes/{rid}", headers=headers)
                if resp.status_code == 200:
                    detail = resp.json().get('recipe') or {}
                    if isinstance(detail, dict):
                        recipe = {**recipe, **detail}
        except Exception:
            pass
        dialog = RecipeDetailDialog(recipe, self)
        dialog.exec()

    def edit_recipe(self, recipe):
        try:
            rid = recipe.get('id')
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            if rid:
                resp = requests.get(f"{self.api_base_url}/recipes/{rid}", headers=headers)
                if resp.status_code == 200:
                    detail = resp.json().get('recipe') or {}
                    if isinstance(detail, dict):
                        recipe = {**recipe, **detail}
            dialog = EditRecipeDialog(self, recipe)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_recipes()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"编辑食谱失败：{str(e)}")

    def delete_recipe(self, recipe):
        rid = recipe.get('id')
        if not rid:
            return
        confirm = QMessageBox.question(self, "确认删除", "确定删除该食谱吗？")
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            resp = requests.delete(f"{self.api_base_url}/recipes/{rid}", headers=headers)
            if resp.status_code == 200:
                self.status_bar.showMessage("已删除食谱")
                self.refresh_recipes()
            else:
                QMessageBox.warning(self, "失败", "删除食谱失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除食谱失败：{str(e)}")
        
    def show_add_recipe_dialog(self):
        dialog = AddRecipeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_recipes()
            
    def refresh_ingredients(self):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/ingredients", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    ingredients = data.get("ingredients") or data.get("data") or []
                elif isinstance(data, list):
                    ingredients = data
                else:
                    ingredients = []
                self.populate_ingredient_table(ingredients)
            else:
                QMessageBox.warning(self, "警告", "获取食材列表失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取食材列表失败：{str(e)}")
            
    def populate_ingredient_table(self, ingredients):
        self.ingredient_table.setRowCount(len(ingredients))
        
        for row, ingredient in enumerate(ingredients):
            if isinstance(ingredient, str):
                try:
                    ingredient = json.loads(ingredient)
                except Exception:
                    ingredient = {"name": ingredient}
            if not isinstance(ingredient, dict):
                ingredient = {}
            self.ingredient_table.setItem(row, 0, QTableWidgetItem(str(ingredient.get("id", ""))))
            self.ingredient_table.setItem(row, 1, QTableWidgetItem(str(ingredient.get("name", ""))))
            self.ingredient_table.setItem(row, 2, QTableWidgetItem(str(ingredient.get("category", ""))))
            self.ingredient_table.setItem(row, 3, QTableWidgetItem(str(ingredient.get("quantity", ""))))
            self.ingredient_table.setItem(row, 4, QTableWidgetItem(str(ingredient.get("unit", ""))))
            self.ingredient_table.setItem(row, 5, QTableWidgetItem(str(ingredient.get("expiry_date", ""))))
            
            # 操作按钮
            edit_btn = QPushButton("编辑")
            edit_btn.setFixedHeight(28)
            edit_btn.clicked.connect(lambda checked, i=ingredient: self.edit_ingredient(i))
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(edit_btn)
            self.ingredient_table.setCellWidget(row, 6, btn_container)
            self.ingredient_table.setRowHeight(row, 38)
            
    def search_ingredients(self):
        search_term = self.ingredient_search_input.text().strip()
        if not search_term:
            self.refresh_ingredients()
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/ingredients", params={"search": search_term}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                ingredients = data.get("ingredients", data)
                self.populate_ingredient_table(ingredients)
            else:
                QMessageBox.warning(self, "警告", "搜索食材失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索食材失败：{str(e)}")
            
    def edit_ingredient(self, ingredient):
        dialog = EditIngredientDialog(ingredient, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_ingredients()
            
    def show_add_ingredient_dialog(self):
        dialog = AddIngredientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_ingredients()
            
    def load_meal_plan(self):
        selected_date = self.meal_plan_date.date().toString("yyyy-MM-dd")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/meal-plans/date/{selected_date}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    meals = data.get("meals") or data.get("meal_plans") or data.get("data") or []
                elif isinstance(data, list):
                    meals = data
                else:
                    meals = []
                self.populate_meal_plan_table(meals)
            else:
                self.meal_plan_table.setRowCount(0)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取膳食计划失败：{str(e)}")
            
    def populate_meal_plan_table(self, meal_plans):
        self.meal_plan_table.setRowCount(len(meal_plans))
        
        for row, meal in enumerate(meal_plans):
            if isinstance(meal, str):
                try:
                    meal = json.loads(meal)
                except Exception:
                    meal = {"recipe_name": meal}
            if not isinstance(meal, dict):
                meal = {}
            nutrition = meal.get("nutrition_info") or meal.get("nutrition") or {}
            if isinstance(nutrition, dict):
                nutrition_text = json.dumps(nutrition, ensure_ascii=False)
            else:
                nutrition_text = str(nutrition or "")
            self.meal_plan_table.setItem(row, 0, QTableWidgetItem(str(meal.get("meal_type", ""))))
            self.meal_plan_table.setItem(row, 1, QTableWidgetItem(str(meal.get("recipe_name", ""))))
            self.meal_plan_table.setItem(row, 2, QTableWidgetItem(str(meal.get("servings", ""))))
            self.meal_plan_table.setItem(row, 3, QTableWidgetItem(str(meal.get("calories", ""))))
            self.meal_plan_table.setItem(row, 4, QTableWidgetItem(nutrition_text))
            
            # 操作按钮
            delete_btn = QPushButton("删除")
            delete_btn.setFixedHeight(28)
            delete_btn.clicked.connect(lambda checked, m=meal: self.delete_meal_plan(m))
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(delete_btn)
            self.meal_plan_table.setCellWidget(row, 5, btn_container)
            self.meal_plan_table.setRowHeight(row, 38)
            
    def generate_meal_plan(self):
        selected_date = self.meal_plan_date.date().toString("yyyy-MM-dd")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.post(f"{self.api_base_url}/meal-plans/generate", 
                                   json={"date": selected_date}, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "成功", "膳食计划生成成功！")
                self.load_meal_plan()
            else:
                QMessageBox.warning(self, "警告", "生成膳食计划失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成膳食计划失败：{str(e)}")
            
    def show_add_meal_dialog(self):
        dialog = AddMealDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_meal_plan()
            
    def delete_meal_plan(self, meal):
        reply = QMessageBox.question(self, "确认", "确定要删除这个餐食计划吗？")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
                # 兼容字符串或非字典输入
                if isinstance(meal, str):
                    try:
                        meal = json.loads(meal)
                    except Exception:
                        meal = {}
                if not isinstance(meal, dict):
                    meal = {}
                meal_id = meal.get('id')
                if not meal_id:
                    QMessageBox.warning(self, "警告", "当前条目缺少ID，无法删除")
                    return
                response = requests.delete(f"{self.api_base_url}/meal-plans/{meal_id}", headers=headers)
                
                if response.status_code == 200:
                    self.load_meal_plan()
                    QMessageBox.information(self, "成功", "餐食计划已删除")
                else:
                    QMessageBox.warning(self, "警告", "删除餐食计划失败")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除餐食计划失败：{str(e)}")
                
    def generate_shopping_list(self):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.post(f"{self.api_base_url}/shopping-lists/generate", headers=headers)
            
            if response.status_code == 201:
                shopping_list = response.json()
                self.populate_shopping_table(shopping_list)
                QMessageBox.information(self, "成功", "购物清单生成成功！")
            else:
                QMessageBox.warning(self, "警告", "生成购物清单失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成购物清单失败：{str(e)}")
            
    def populate_shopping_table(self, shopping_items):
        self.shopping_table.setRowCount(len(shopping_items))
        
        for row, item in enumerate(shopping_items):
            self.shopping_table.setItem(row, 0, QTableWidgetItem(item.get("item_name", "")))
            self.shopping_table.setItem(row, 1, QTableWidgetItem(str(item.get("quantity", ""))))
            self.shopping_table.setItem(row, 2, QTableWidgetItem(item.get("unit", "")))
            self.shopping_table.setItem(row, 3, QTableWidgetItem(item.get("notes", "")))
            
            # 操作按钮
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, i=item: self.delete_shopping_item(i))
            self.shopping_table.setCellWidget(row, 4, delete_btn)
            
    def show_add_shopping_item_dialog(self):
        dialog = AddShoppingItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_shopping_list()
            
    def refresh_shopping_list(self):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/shopping-lists", headers=headers)
            
            if response.status_code == 200:
                shopping_list = response.json()
                self.populate_shopping_table(shopping_list)
            else:
                QMessageBox.warning(self, "警告", "获取购物清单失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取购物清单失败：{str(e)}")
            
    def delete_shopping_item(self, item):
        reply = QMessageBox.question(self, "确认", "确定要删除这个物品吗？")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
                response = requests.delete(f"{self.api_base_url}/shopping-lists/{item['id']}", headers=headers)
                
                if response.status_code == 200:
                    self.refresh_shopping_list()
                    QMessageBox.information(self, "成功", "物品已删除")
                else:
                    QMessageBox.warning(self, "警告", "删除物品失败")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除物品失败：{str(e)}")
                
    def export_shopping_list(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出购物清单", "", "Text Files (*.txt)")
        if file_path:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
                response = requests.get(f"{self.api_base_url}/shopping-lists/export", headers=headers)
                
                if response.status_code == 200:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    QMessageBox.information(self, "成功", f"购物清单已导出到 {file_path}")
                else:
                    QMessageBox.warning(self, "警告", "导出购物清单失败")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出购物清单失败：{str(e)}")
                
    def analyze_today_nutrition(self):
        today = QDate.currentDate().toString("yyyy-MM-dd")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/nutrition/daily/{today}", headers=headers)
            
            if response.status_code == 200:
                nutrition_data = response.json()
                self.display_nutrition_info(nutrition_data)
            else:
                QMessageBox.warning(self, "警告", "获取营养分析失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取营养分析失败：{str(e)}")
            
    def display_nutrition_info(self, nutrition_data):
        info_text = f"""
今日营养分析报告
==================

总卡路里: {nutrition_data.get('total_calories', 0)} kcal
总蛋白质: {nutrition_data.get('total_protein', 0)} g
总脂肪: {nutrition_data.get('total_fat', 0)} g
总碳水化合物: {nutrition_data.get('total_carbs', 0)} g
总纤维: {nutrition_data.get('total_fiber', 0)} g
总糖: {nutrition_data.get('total_sugar', 0)} g

营养建议:
{nutrition_data.get('recommendations', '暂无建议')}
"""
        self.nutrition_info.setPlainText(info_text)
        
    def show_weekly_report(self):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            response = requests.get(f"{self.api_base_url}/nutrition/weekly", headers=headers)
            if response.status_code == 200:
                data = response.json()
                weekly = data.get("weekly", [])
                avg = data.get("average", {})
                lines = ["最近7天营养统计"]
                for day in weekly:
                    lines.append(f"{day.get('date','')}: {day.get('calories',0)} kcal, P {day.get('protein',0)}g, C {day.get('carbs',0)}g, F {day.get('fat',0)}g")
                lines.append("")
                lines.append(f"平均: {avg.get('avg_calories',0)} kcal, P {avg.get('avg_protein',0)}g, C {avg.get('avg_carbs',0)}g, F {avg.get('avg_fat',0)}g")
                self.nutrition_info.setPlainText("\n".join(lines))
            else:
                QMessageBox.warning(self, "警告", "获取周营养报告失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取周营养报告失败：{str(e)}")


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("用户注册")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 邮箱
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("邮箱:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入邮箱")
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入密码")
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("确认密码:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("请再次输入密码")
        confirm_layout.addWidget(self.confirm_password_input)
        layout.addLayout(confirm_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.register)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        if not all([username, email, password, confirm_password]):
            QMessageBox.warning(self, "警告", "请填写所有字段")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
            
        try:
            response = requests.post(f"{self.parent.api_base_url}/auth/register", json={
                "username": username,
                "email": email,
                "password": password
            })
            
            if response.status_code == 201:
                QMessageBox.information(self, "成功", "注册成功！请登录")
                self.accept()
            else:
                QMessageBox.warning(self, "注册失败", response.json().get("message", "注册失败"))
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注册失败：{str(e)}")


class RecipeDetailDialog(QDialog):
    def __init__(self, recipe, parent=None):
        super().__init__(parent)
        self.recipe = recipe
        self.parent = parent
        title = recipe.get('name') or recipe.get('title', '')
        self.setWindowTitle(f"食谱详情 - {title}")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 基本信息
        name = self.recipe.get('name') or self.recipe.get('title', '未知')
        category = self.recipe.get('category', '未知')
        difficulty = self.recipe.get('difficulty', '未知')
        prep_time = self.recipe.get('prep_time') or 0
        cook_time = self.recipe.get('cook_time') or self.recipe.get('cooking_time') or 0
        servings = self.recipe.get('servings', 0)
        rating = self.recipe.get('rating', 0)
        info_text = f"""
名称: {name}
分类: {category}
难度: {difficulty}
准备时间: {prep_time} 分钟
烹饪时间: {cook_time} 分钟
份量: {servings} 人份
评分: {rating}/5
        """.strip()
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # 食材列表
        ingredients_label = QLabel("食材:")
        ingredients_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(ingredients_label)
        
        ingredients_text = QTextEdit()
        ingredients_text.setReadOnly(True)
        ingredients_text.setMaximumHeight(150)
        ingredients = self.recipe.get('ingredients')
        if isinstance(ingredients, list):
            ingredients_str = "\n".join([f"• {ing.get('name', '')}: {ing.get('quantity', '')} {ing.get('unit', '')}" for ing in ingredients])
        elif isinstance(ingredients, str):
            ingredients_str = ingredients
        else:
            ingredients_str = ""
        ingredients_text.setPlainText(ingredients_str)
        layout.addWidget(ingredients_text)
        
        # 制作步骤
        steps_label = QLabel("制作步骤:")
        steps_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(steps_label)
        
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setPlainText(self.recipe.get('instructions') or self.recipe.get('description', '暂无制作步骤'))
        layout.addWidget(steps_text)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class AddRecipeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("添加食谱")
        self.setModal(True)
        self.resize(600, 700)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        
        # 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入食谱名称")
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)
        
        # 分类和难度
        cat_diff_layout = QHBoxLayout()
        
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("分类:"))
        self.category_input = QComboBox()
        self.category_input.addItems(["早餐", "午餐", "晚餐", "甜点", "小食", "汤品"])
        cat_layout.addWidget(self.category_input)
        
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("难度:"))
        self.difficulty_input = QComboBox()
        self.difficulty_input.addItems(["简单", "中等", "困难"])
        diff_layout.addWidget(self.difficulty_input)
        
        cat_diff_layout.addLayout(cat_layout)
        cat_diff_layout.addLayout(diff_layout)
        basic_layout.addLayout(cat_diff_layout)
        
        # 时间和份量
        time_serv_layout = QHBoxLayout()
        
        prep_layout = QHBoxLayout()
        prep_layout.addWidget(QLabel("准备时间(分钟):"))
        self.prep_time_input = QSpinBox()
        self.prep_time_input.setRange(1, 300)
        prep_layout.addWidget(self.prep_time_input)
        
        cook_layout = QHBoxLayout()
        cook_layout.addWidget(QLabel("烹饪时间(分钟):"))
        self.cook_time_input = QSpinBox()
        self.cook_time_input.setRange(1, 300)
        cook_layout.addWidget(self.cook_time_input)
        
        servings_layout = QHBoxLayout()
        servings_layout.addWidget(QLabel("份量(人):"))
        self.servings_input = QSpinBox()
        self.servings_input.setRange(1, 20)
        servings_layout.addWidget(self.servings_input)
        
        time_serv_layout.addLayout(prep_layout)
        time_serv_layout.addLayout(cook_layout)
        time_serv_layout.addLayout(servings_layout)
        basic_layout.addLayout(time_serv_layout)
        
        layout.addWidget(basic_group)
        
        # 食材
        ingredients_group = QGroupBox("食材")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        self.ingredients_text = QTextEdit()
        self.ingredients_text.setPlaceholderText("请输入食材，格式：食材名称,数量,单位\n例如：\n鸡蛋,2,个\n面粉,200,克")
        self.ingredients_text.setMaximumHeight(150)
        ingredients_layout.addWidget(self.ingredients_text)
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("食谱图片:"))
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        img_layout.addWidget(self.image_path_input)
        img_select_btn = QPushButton("选择图片")
        img_select_btn.clicked.connect(self.select_image)
        img_layout.addWidget(img_select_btn)
        ingredients_layout.addLayout(img_layout)
        
        layout.addWidget(ingredients_group)
        
        # 制作步骤
        steps_group = QGroupBox("制作步骤")
        steps_layout = QVBoxLayout(steps_group)
        
        self.steps_text = QTextEdit()
        self.steps_text.setPlaceholderText("请输入详细的制作步骤...")
        steps_layout.addWidget(self.steps_text)
        
        layout.addWidget(steps_group)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.add_recipe)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def add_recipe(self):
        name = self.name_input.text().strip()
        category = self.category_input.currentText()
        difficulty = self.difficulty_input.currentText()
        prep_time = self.prep_time_input.value()
        cook_time = self.cook_time_input.value()
        servings = self.servings_input.value()
        ingredients_text = self.ingredients_text.toPlainText().strip()
        steps = self.steps_text.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入食谱名称")
            return
            
        if not ingredients_text:
            QMessageBox.warning(self, "警告", "请输入食材信息")
            return
            
        if not steps:
            QMessageBox.warning(self, "警告", "请输入制作步骤")
            return
            
        # 解析食材
        ingredients = []
        for line in ingredients_text.split('\n'):
            if line.strip():
                parts = line.split(',')
                if len(parts) == 3:
                    ingredients.append({
                        "name": parts[0].strip(),
                        "quantity": float(parts[1].strip()),
                        "unit": parts[2].strip()
                    })
        
        recipe_data = {
            "name": name,
            "category": category,
            "difficulty": difficulty,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "servings": servings,
            "ingredients": ingredients,
            "instructions": steps
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            response = requests.post(f"{self.parent.api_base_url}/recipes", json=recipe_data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "成功", "食谱添加成功！")
                rid = response.json().get("recipe_id")
                if rid and getattr(self, "image_path", None):
                    try:
                        with open(self.image_path, "rb") as f:
                            files = {"image": (os.path.basename(self.image_path), f, "application/octet-stream")}
                            requests.post(f"{self.parent.api_base_url}/recipes/{rid}/image", files=files, headers=headers)
                    except Exception:
                        pass
                self.accept()
            else:
                QMessageBox.warning(self, "失败", "添加食谱失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加食谱失败：{str(e)}")
        
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            self.image_path_input.setText(file_path)

class EditRecipeDialog(QDialog):
    def __init__(self, parent=None, recipe=None):
        super().__init__(parent)
        self.parent = parent
        self.recipe = recipe or {}
        self.setWindowTitle("编辑食谱")
        self.setModal(True)
        self.resize(600, 700)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_input = QLineEdit()
        self.name_input.setText(str(self.recipe.get('name') or self.recipe.get('title', '')))
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)
        cat_diff_layout = QHBoxLayout()
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("分类:"))
        self.category_input = QComboBox()
        self.category_input.addItems(["早餐", "午餐", "晚餐", "甜点", "小食", "汤品"])
        cat_layout.addWidget(self.category_input)
        self.category_input.setCurrentText(str(self.recipe.get('category', '早餐')))
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("难度:"))
        self.difficulty_input = QComboBox()
        self.difficulty_input.addItems(["简单", "中等", "困难"])
        diff_layout.addWidget(self.difficulty_input)
        cat_diff_layout.addLayout(cat_layout)
        cat_diff_layout.addLayout(diff_layout)
        basic_layout.addLayout(cat_diff_layout)
        time_serv_layout = QHBoxLayout()
        prep_layout = QHBoxLayout()
        prep_layout.addWidget(QLabel("准备时间(分钟):"))
        self.prep_time_input = QSpinBox()
        self.prep_time_input.setRange(0, 300)
        self.prep_time_input.setValue(int(self.recipe.get('prep_time') or 0))
        prep_layout.addWidget(self.prep_time_input)
        cook_layout = QHBoxLayout()
        cook_layout.addWidget(QLabel("烹饪时间(分钟):"))
        self.cook_time_input = QSpinBox()
        self.cook_time_input.setRange(0, 300)
        self.cook_time_input.setValue(int(self.recipe.get('cook_time') or self.recipe.get('cooking_time') or 0))
        cook_layout.addWidget(self.cook_time_input)
        servings_layout = QHBoxLayout()
        servings_layout.addWidget(QLabel("份量(人):"))
        self.servings_input = QSpinBox()
        self.servings_input.setRange(1, 20)
        self.servings_input.setValue(int(self.recipe.get('servings') or 1))
        time_serv_layout.addLayout(prep_layout)
        time_serv_layout.addLayout(cook_layout)
        time_serv_layout.addLayout(servings_layout)
        basic_layout.addLayout(time_serv_layout)
        layout.addWidget(basic_group)
        ingredients_group = QGroupBox("食材")
        ingredients_layout = QVBoxLayout(ingredients_group)
        self.ingredients_text = QTextEdit()
        self.ingredients_text.setPlaceholderText("食材名称,数量,单位")
        self.ingredients_text.setMaximumHeight(150)
        if isinstance(self.recipe.get('ingredients'), list):
            lines = []
            for ing in self.recipe.get('ingredients'):
                lines.append(f"{ing.get('name','')},{ing.get('quantity','')},{ing.get('unit','')}")
            self.ingredients_text.setPlainText("\n".join(lines))
        elif isinstance(self.recipe.get('ingredients'), str):
            self.ingredients_text.setPlainText(self.recipe.get('ingredients'))
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("食谱图片:"))
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        img_layout.addWidget(self.image_path_input)
        img_select_btn = QPushButton("选择图片")
        img_select_btn.clicked.connect(self.select_image)
        img_layout.addWidget(img_select_btn)
        ingredients_layout.addLayout(img_layout)
        layout.addWidget(ingredients_group)
        steps_group = QGroupBox("制作步骤")
        steps_layout = QVBoxLayout(steps_group)
        self.steps_text = QTextEdit()
        self.steps_text.setPlaceholderText("请输入详细的制作步骤...")
        self.steps_text.setPlainText(str(self.recipe.get('instructions') or self.recipe.get('description', '')))
        steps_layout.addWidget(self.steps_text)
        layout.addWidget(steps_group)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.update_recipe)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def update_recipe(self):
        rid = self.recipe.get('id')
        if not rid:
            QMessageBox.warning(self, "警告", "缺少食谱ID")
            return
        name = self.name_input.text().strip()
        category = self.category_input.currentText()
        difficulty = self.difficulty_input.currentText()
        prep_time = self.prep_time_input.value()
        cook_time = self.cook_time_input.value()
        servings = self.servings_input.value()
        ingredients_text = self.ingredients_text.toPlainText().strip()
        steps = self.steps_text.toPlainText().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入食谱名称")
            return
        ingredients = []
        for line in ingredients_text.split('\n'):
            if line.strip():
                parts = line.split(',')
                if len(parts) == 3:
                    ingredients.append({
                        'name': parts[0].strip(),
                        'quantity': float(parts[1].strip()) if parts[1].strip() else '',
                        'unit': parts[2].strip()
                    })
        payload = {
            'title': name,
            'category': category,
            'difficulty': difficulty,
            'prep_time': prep_time,
            'cook_time': cook_time,
            'servings': servings,
            'instructions': steps,
            'ingredients': ingredients
        }
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            resp = requests.put(f"{self.parent.api_base_url}/recipes/{rid}", json=payload, headers=headers)
            if resp.status_code == 200:
                if getattr(self, 'image_path', None):
                    try:
                        with open(self.image_path, 'rb') as f:
                            files = {'image': (os.path.basename(self.image_path), f, 'application/octet-stream')}
                            requests.post(f"{self.parent.api_base_url}/recipes/{rid}/image", files=files, headers=headers)
                    except Exception:
                        pass
                QMessageBox.information(self, "成功", "食谱更新成功！")
                self.accept()
            else:
                QMessageBox.warning(self, "失败", "更新食谱失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新食谱失败：{str(e)}")
        
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            self.image_path_input.setText(file_path)


class AddIngredientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("添加食材")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入食材名称")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 分类
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.category_input = QComboBox()
        self.category_input.addItems(["蔬菜", "水果", "肉类", "海鲜", "谷物", "调料", "乳制品", "其他"])
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)
        
        # 数量和单位
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("数量:"))
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.1, 10000)
        self.quantity_input.setValue(1.0)
        quantity_layout.addWidget(self.quantity_input)
        
        quantity_layout.addWidget(QLabel("单位:"))
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("如：克、个、毫升")
        quantity_layout.addWidget(self.unit_input)
        layout.addLayout(quantity_layout)
        
        # 保质期
        expiry_layout = QHBoxLayout()
        expiry_layout.addWidget(QLabel("保质期:"))
        self.expiry_date = QDateEdit()
        self.expiry_date.setDate(QDate.currentDate().addDays(30))
        expiry_layout.addWidget(self.expiry_date)
        layout.addLayout(expiry_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.add_ingredient)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def add_ingredient(self):
        name = self.name_input.text().strip()
        category = self.category_input.currentText()
        quantity = self.quantity_input.value()
        unit = self.unit_input.text().strip()
        expiry_date = self.expiry_date.date().toString("yyyy-MM-dd")
        
        if not name or not unit:
            QMessageBox.warning(self, "警告", "请填写完整信息")
            return
            
        ingredient_data = {
            "name": name,
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "expiry_date": expiry_date
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            response = requests.post(f"{self.parent.api_base_url}/ingredients", json=ingredient_data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "成功", "食材添加成功！")
                self.accept()
            else:
                QMessageBox.warning(self, "失败", "添加食材失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加食材失败：{str(e)}")


class EditIngredientDialog(QDialog):
    def __init__(self, ingredient, parent=None):
        super().__init__(parent)
        self.ingredient = ingredient
        self.parent = parent
        self.setWindowTitle("编辑食材")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.ingredient.get('name', ''))
        self.name_input.setPlaceholderText("请输入食材名称")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 分类
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.category_input = QComboBox()
        self.category_input.addItems(["蔬菜", "水果", "肉类", "海鲜", "谷物", "调料", "乳制品", "其他"])
        current_category = self.ingredient.get('category', '其他')
        if current_category in ["蔬菜", "水果", "肉类", "海鲜", "谷物", "调料", "乳制品", "其他"]:
            self.category_input.setCurrentText(current_category)
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)
        
        # 数量和单位
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("数量:"))
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.1, 10000)
        self.quantity_input.setValue(self.ingredient.get('quantity', 1.0))
        quantity_layout.addWidget(self.quantity_input)
        
        quantity_layout.addWidget(QLabel("单位:"))
        self.unit_input = QLineEdit()
        self.unit_input.setText(self.ingredient.get('unit', ''))
        self.unit_input.setPlaceholderText("如：克、个、毫升")
        quantity_layout.addWidget(self.unit_input)
        layout.addLayout(quantity_layout)
        
        # 保质期
        expiry_layout = QHBoxLayout()
        expiry_layout.addWidget(QLabel("保质期:"))
        self.expiry_date = QDateEdit()
        expiry_str = self.ingredient.get('expiry_date', QDate.currentDate().addDays(30).toString("yyyy-MM-dd"))
        try:
            expiry_qdate = QDate.fromString(expiry_str, "yyyy-MM-dd")
            if expiry_qdate.isValid():
                self.expiry_date.setDate(expiry_qdate)
            else:
                self.expiry_date.setDate(QDate.currentDate().addDays(30))
        except:
            self.expiry_date.setDate(QDate.currentDate().addDays(30))
        expiry_layout.addWidget(self.expiry_date)
        layout.addLayout(expiry_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.edit_ingredient)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def edit_ingredient(self):
        name = self.name_input.text().strip()
        category = self.category_input.currentText()
        quantity = self.quantity_input.value()
        unit = self.unit_input.text().strip()
        expiry_date = self.expiry_date.date().toString("yyyy-MM-dd")
        
        if not name or not unit:
            QMessageBox.warning(self, "警告", "请填写完整信息")
            return
            
        ingredient_data = {
            "name": name,
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "expiry_date": expiry_date
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            response = requests.put(f"{self.parent.api_base_url}/ingredients/{self.ingredient['id']}", 
                                  json=ingredient_data, headers=headers)
            
            if response.status_code == 200:
                QMessageBox.information(self, "成功", "食材更新成功！")
                self.accept()
            else:
                QMessageBox.warning(self, "失败", "更新食材失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新食材失败：{str(e)}")


class AddMealDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("添加餐食")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 餐次
        meal_type_layout = QHBoxLayout()
        meal_type_layout.addWidget(QLabel("餐次:"))
        self.meal_type_input = QComboBox()
        self.meal_type_input.addItems(["早餐", "上午加餐", "午餐", "下午加餐", "晚餐", "夜宵"])
        meal_type_layout.addWidget(self.meal_type_input)
        layout.addLayout(meal_type_layout)
        
        # 日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日期:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)
        
        # 食谱名称
        recipe_layout = QHBoxLayout()
        recipe_layout.addWidget(QLabel("食谱:"))
        self.recipe_input = QLineEdit()
        self.recipe_input.setPlaceholderText("请输入食谱名称")
        recipe_layout.addWidget(self.recipe_input)
        layout.addLayout(recipe_layout)
        
        # 份量
        servings_layout = QHBoxLayout()
        servings_layout.addWidget(QLabel("份量:"))
        self.servings_input = QSpinBox()
        self.servings_input.setRange(1, 10)
        self.servings_input.setValue(1)
        servings_layout.addWidget(self.servings_input)
        layout.addLayout(servings_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.add_meal)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def add_meal(self):
        meal_type = self.meal_type_input.currentText()
        date = self.date_input.date().toString("yyyy-MM-dd")
        recipe_name = self.recipe_input.text().strip()
        servings = self.servings_input.value()
        
        if not recipe_name:
            QMessageBox.warning(self, "警告", "请输入食谱名称")
            return
            
        meal_data = {
            "meal_type": meal_type,
            "date": date,
            "recipe_name": recipe_name,
            "servings": servings
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            response = requests.post(f"{self.parent.api_base_url}/meal-plans", json=meal_data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "成功", "餐食添加成功！")
                self.accept()
            else:
                QMessageBox.warning(self, "失败", "添加餐食失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加餐食失败：{str(e)}")


class AddShoppingItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("添加购物物品")
        self.setModal(True)
        self.resize(400, 250)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 物品名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("物品名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入物品名称")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 数量和单位
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("数量:"))
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.1, 10000)
        self.quantity_input.setValue(1.0)
        quantity_layout.addWidget(self.quantity_input)
        
        quantity_layout.addWidget(QLabel("单位:"))
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("如：个、包、瓶")
        quantity_layout.addWidget(self.unit_input)
        layout.addLayout(quantity_layout)
        
        # 备注
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("备注:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("可选：添加备注信息")
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialog.ButtonBox.Ok | QDialog.ButtonBox.Cancel)
        button_box.accepted.connect(self.add_item)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def add_item(self):
        name = self.name_input.text().strip()
        quantity = self.quantity_input.value()
        unit = self.unit_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        
        if not name or not unit:
            QMessageBox.warning(self, "警告", "请填写物品名称和单位")
            return
            
        item_data = {
            "item_name": name,
            "quantity": quantity,
            "unit": unit,
            "notes": notes
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.parent.auth_token}"} if self.parent.auth_token else {}
            response = requests.post(f"{self.parent.api_base_url}/shopping-lists", json=item_data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(self, "成功", "物品添加成功！")
                self.accept()
            else:
                QMessageBox.warning(self, "失败", "添加物品失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加物品失败：{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecipeApp()
    window.show()
    sys.exit(app.exec())