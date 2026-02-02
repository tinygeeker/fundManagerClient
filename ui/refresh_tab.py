#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刷新模块界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QListWidget, QListWidgetItem, QLabel, QMessageBox, QSplitter, QWidget as QWidge
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from api.fund_api import FundAPI
from database.db_manager import FundDB

class FundUpdateThread(QThread):
    """基金数据更新线程"""
    update_signal = pyqtSignal(list)
    
    def __init__(self, fund_codes):
        super().__init__()
        self.fund_codes = fund_codes
        self.api = FundAPI()
    
    def run(self):
        fund_data_list = []
        for code in self.fund_codes:
            fund_info = self.api.get_fund_info(code)
            fund_net_value = self.api.get_fund_net_value(code)
            if fund_info and fund_net_value:
                fund_data = {
                    'code': code,
                    'name': fund_info['name'],
                    'type': fund_info['type'],
                    'net_value': fund_net_value['net_value'],
                    'day_growth': fund_net_value['day_growth'],
                    'date': fund_net_value['date']
                }
                fund_data_list.append(fund_data)
        self.update_signal.emit(fund_data_list)

class RefreshTab(QWidget):
    """刷新模块界面"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_portfolios()
    
    def init_ui(self):
        """初始化界面"""
        self.layout = QVBoxLayout(self)
        # 移除主布局的边距
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建一个主分割器，包含顶部搜索栏和底部内容
        main_splitter = QSplitter(Qt.Vertical)
        # 设置分割器的手柄宽度为1，减少间距
        main_splitter.setHandleWidth(1)
        
        # 顶部搜索和操作栏
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        # 移除顶部widget的布局边距
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧组合名称搜索和添加（与底部左侧等宽）
        left_top_widget = QWidget()
        left_top_layout = QHBoxLayout(left_top_widget)
        # 移除左侧顶部widget的布局边距
        left_top_layout.setContentsMargins(0, 0, 0, 0)
        self.portfolio_name_input = QLineEdit()
        self.portfolio_name_input.setPlaceholderText('输入组合名称')
        left_top_layout.addWidget(self.portfolio_name_input)
        
        self.add_portfolio_btn = QPushButton('添加组合')
        self.add_portfolio_btn.clicked.connect(self.add_portfolio)
        left_top_layout.addWidget(self.add_portfolio_btn)
        
        # 右侧基金搜索和操作（与底部右侧等宽）
        right_top_widget = QWidget()
        right_top_layout = QHBoxLayout(right_top_widget)
        # 移除右侧顶部widget的布局边距
        right_top_layout.setContentsMargins(0, 0, 0, 0)
        self.fund_code_input = QLineEdit()
        self.fund_code_input.setPlaceholderText('输入基金代码')
        right_top_layout.addWidget(self.fund_code_input)
        
        self.add_fund_btn = QPushButton('添加基金')
        self.add_fund_btn.clicked.connect(self.add_fund_to_current_portfolio)
        right_top_layout.addWidget(self.add_fund_btn)
        
        self.refresh_btn = QPushButton('刷新数据')
        self.refresh_btn.clicked.connect(self.refresh_data)
        right_top_layout.addWidget(self.refresh_btn)
        
        # 设置布局比例，与底部保持一致
        top_layout.addWidget(left_top_widget, 1)
        top_layout.addWidget(right_top_widget, 3)
        
        main_splitter.addWidget(top_widget)
        
        # 底部内容区域
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        # 移除底部widget的布局边距
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧组合列表（占1/4宽度）
        self.portfolio_list = QListWidget()
        self.portfolio_list.itemClicked.connect(self.select_portfolio)
        bottom_layout.addWidget(self.portfolio_list, 1)
        
        # 右侧基金列表（占3/4宽度）
        self.fund_list = QListWidget()
        bottom_layout.addWidget(self.fund_list, 3)
        
        main_splitter.addWidget(bottom_widget)
        
        # 设置分割器比例
        main_splitter.setSizes([80, 600])
        
        self.layout.addWidget(main_splitter)
        
        # 当前选中的组合
        self.current_portfolio = None
    
    def load_portfolios(self):
        """加载基金组合"""
        self.portfolio_list.clear()
        db = FundDB()
        portfolios = db.get_portfolios()
        db.close()
        
        for portfolio in portfolios:
            item = QListWidgetItem(portfolio['name'])
            item.setData(Qt.UserRole, portfolio)
            self.portfolio_list.addItem(item)
    
    def select_portfolio(self, item):
        """选择组合"""
        self.current_portfolio = item.data(Qt.UserRole)
        self.load_portfolio_funds()
    
    def load_portfolio_funds(self):
        """加载组合中的基金"""
        if not self.current_portfolio:
            return
        
        self.fund_list.clear()
        fund_codes = self.current_portfolio['fund_codes']
        
        if fund_codes:
            # 启动线程更新基金数据
            self.update_thread = FundUpdateThread(fund_codes)
            self.update_thread.update_signal.connect(self.update_fund_list)
            self.update_thread.start()
    
    def update_fund_list(self, fund_data_list):
        """更新基金列表"""
        self.fund_list.clear()
        from utils.profit_prediction import ProfitPrediction
        from api.fund_api import FundAPI
        
        predictor = ProfitPrediction()
        api = FundAPI()
        market_data = api.get_market_index()
        
        for fund_data in fund_data_list:
            item = QListWidgetItem(f"{fund_data['name']} ({fund_data['code']})")
            item.setData(Qt.UserRole, fund_data)
            
            # 根据涨跌幅设置颜色
            day_growth = fund_data['day_growth']
            if day_growth.startswith('+'):
                item.setForeground(QColor('red'))
            elif day_growth.startswith('-'):
                item.setForeground(QColor('green'))
            
            # 预测收益
            predicted_profit = predictor.predict_daily_profit([fund_data], market_data)
            
            # 添加子项显示详细信息
            net_value_item = QListWidgetItem(f"单位净值: {fund_data['net_value']}")
            day_growth_item = QListWidgetItem(f"日涨跌幅: {fund_data['day_growth']}%")
            predicted_item = QListWidgetItem(f"预测收益: {predicted_profit:+.2f}%")
            date_item = QListWidgetItem(f"更新日期: {fund_data['date']}")
            
            # 设置预测收益颜色
            if predicted_profit > 0:
                predicted_item.setForeground(QColor('red'))
            elif predicted_profit < 0:
                predicted_item.setForeground(QColor('green'))
            
            item.addChild(net_value_item)
            item.addChild(day_growth_item)
            item.addChild(predicted_item)
            item.addChild(date_item)
            
            self.fund_list.addItem(item)
            item.setExpanded(True)
    
    def add_portfolio(self):
        """添加组合"""
        portfolio_name = self.portfolio_name_input.text().strip()
        if not portfolio_name:
            QMessageBox.warning(self, '提示', '请输入组合名称')
            return
        
        # 检查组合名称是否已存在
        db = FundDB()
        portfolios = db.get_portfolios()
        
        for portfolio in portfolios:
            if portfolio['name'] == portfolio_name:
                QMessageBox.warning(self, '提示', '组合名称已存在，请使用其他名称')
                db.close()
                return
        
        portfolio_id = db.add_portfolio(portfolio_name)
        db.close()
        
        if portfolio_id:
            QMessageBox.information(self, '成功', '组合添加成功')
            self.portfolio_name_input.clear()
            self.load_portfolios()
        else:
            QMessageBox.error(self, '错误', '组合添加失败')
    
    def add_fund_to_current_portfolio(self):
        """向当前组合添加基金"""
        if not self.current_portfolio:
            QMessageBox.warning(self, '提示', '请先选择一个组合')
            return
        
        fund_code = self.fund_code_input.text().strip()
        if not fund_code:
            QMessageBox.warning(self, '提示', '请输入基金代码')
            return
        
        # 验证基金代码是否有效
        api = FundAPI()
        fund_info = api.get_fund_info(fund_code)
        if not fund_info:
            QMessageBox.error(self, '错误', '基金不存在')
            return
        
        db = FundDB()
        success = db.add_fund_to_portfolio(self.current_portfolio['id'], fund_code)
        db.close()
        
        if success:
            QMessageBox.information(self, '成功', f'基金 {fund_info["name"]} 添加成功')
            self.fund_code_input.clear()
            self.load_portfolios()
            self.select_portfolio(self.portfolio_list.currentItem())
        else:
            QMessageBox.error(self, '错误', '基金添加失败')
    
    def refresh_data(self):
        """刷新数据"""
        if not self.current_portfolio:
            QMessageBox.warning(self, '提示', '请先选择一个组合')
            return
        
        self.load_portfolio_funds()
        QMessageBox.information(self, '成功', '数据刷新完成')
