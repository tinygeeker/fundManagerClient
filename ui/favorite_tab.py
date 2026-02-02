#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自选模块界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QListWidget, QListWidgetItem, QMessageBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from api.fund_api import FundAPI
from database.db_manager import FundDB

class FavoriteFundUpdateThread(QThread):
    """自选基金数据更新线程"""
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

class FavoriteTab(QWidget):
    """自选模块界面"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_favorite_funds()
    
    def init_ui(self):
        """初始化界面"""
        self.layout = QVBoxLayout(self)
        
        # 顶部搜索和操作栏
        top_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入基金代码或名称')
        top_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton('搜索')
        self.search_btn.clicked.connect(self.search_funds)
        top_layout.addWidget(self.search_btn)
        
        self.add_favorite_btn = QPushButton('添加到自选')
        self.add_favorite_btn.clicked.connect(self.add_favorite_fund)
        top_layout.addWidget(self.add_favorite_btn)
        
        self.refresh_btn = QPushButton('刷新数据')
        self.refresh_btn.clicked.connect(self.refresh_data)
        top_layout.addWidget(self.refresh_btn)
        
        self.layout.addLayout(top_layout)
        
        # 中间分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧搜索结果区域
        self.search_result_table = QTableWidget()
        self.search_result_table.setColumnCount(4)
        self.search_result_table.setHorizontalHeaderLabels(['选择', '基金名称', '基金代码', '基金类型'])
        # 设置列宽，选择列宽度改小
        self.search_result_table.setColumnWidth(0, 60)
        self.search_result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.search_result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.search_result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.search_result_table.setSelectionBehavior(QTableWidget.SelectRows)
        splitter.addWidget(self.search_result_table)
        
        # 右侧自选基金区域
        self.fund_table = QTableWidget()
        self.fund_table.setColumnCount(6)
        self.fund_table.setHorizontalHeaderLabels(['基金名称', '基金代码', '基金类型', '单位净值', '日涨跌幅', '更新日期'])
        self.fund_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fund_table.setSelectionBehavior(QTableWidget.SelectRows)
        splitter.addWidget(self.fund_table)
        
        # 设置分割器比例，左右高度对齐
        splitter.setSizes([500, 500])
        
        self.layout.addWidget(splitter)
    
    def load_favorite_funds(self):
        """加载自选基金"""
        db = FundDB()
        favorite_funds = db.get_favorite_funds()
        db.close()
        
        fund_codes = [fund['code'] for fund in favorite_funds]
        if fund_codes:
            # 启动线程更新基金数据
            self.update_thread = FavoriteFundUpdateThread(fund_codes)
            self.update_thread.update_signal.connect(self.update_fund_table)
            self.update_thread.start()
        else:
            self.fund_table.setRowCount(0)
    
    def update_fund_table(self, fund_data_list):
        """更新基金表格"""
        from utils.profit_prediction import ProfitPrediction
        from api.fund_api import FundAPI
        
        predictor = ProfitPrediction()
        api = FundAPI()
        market_data = api.get_market_index()
        
        # 添加预测收益列
        if self.fund_table.columnCount() == 6:
            self.fund_table.setColumnCount(7)
            headers = ['基金名称', '基金代码', '基金类型', '单位净值', '日涨跌幅', '预测收益', '更新日期']
            self.fund_table.setHorizontalHeaderLabels(headers)
        
        self.fund_table.setRowCount(len(fund_data_list))
        
        for row, fund_data in enumerate(fund_data_list):
            # 基金名称
            name_item = QTableWidgetItem(fund_data['name'])
            self.fund_table.setItem(row, 0, name_item)
            
            # 基金代码
            code_item = QTableWidgetItem(fund_data['code'])
            self.fund_table.setItem(row, 1, code_item)
            
            # 基金类型
            type_item = QTableWidgetItem(fund_data['type'])
            self.fund_table.setItem(row, 2, type_item)
            
            # 单位净值
            net_value_item = QTableWidgetItem(fund_data['net_value'])
            self.fund_table.setItem(row, 3, net_value_item)
            
            # 日涨跌幅
            day_growth_item = QTableWidgetItem(fund_data['day_growth'])
            if fund_data['day_growth'].startswith('+'):
                day_growth_item.setForeground(QColor('red'))
            elif fund_data['day_growth'].startswith('-'):
                day_growth_item.setForeground(QColor('green'))
            self.fund_table.setItem(row, 4, day_growth_item)
            
            # 预测收益
            predicted_profit = predictor.predict_daily_profit([fund_data], market_data)
            predicted_item = QTableWidgetItem(f"{predicted_profit:+.2f}%")
            if predicted_profit > 0:
                predicted_item.setForeground(QColor('red'))
            elif predicted_profit < 0:
                predicted_item.setForeground(QColor('green'))
            self.fund_table.setItem(row, 5, predicted_item)
            
            # 更新日期
            date_item = QTableWidgetItem(fund_data['date'])
            self.fund_table.setItem(row, 6, date_item)
    
    def add_favorite_fund(self):
        """添加自选基金"""
        # 检查是否有勾选的基金
        checked_rows = []
        for row in range(self.search_result_table.rowCount()):
            item = self.search_result_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                checked_rows.append(row)
        
        if not checked_rows:
            QMessageBox.warning(self, '提示', '请选择要添加的基金')
            return
        
        # 验证并添加勾选的基金
        api = FundAPI()
        db = FundDB()
        success_count = 0
        
        for row in checked_rows:
            fund_code = self.search_result_table.item(row, 2).text()
            fund_name = self.search_result_table.item(row, 1).text()
            fund_type = self.search_result_table.item(row, 3).text()
            
            # 验证基金代码是否有效
            fund_info = api.get_fund_info(fund_code)
            if not fund_info:
                QMessageBox.error(self, '错误', f'基金 {fund_name} 不存在')
                continue
            
            # 添加到数据库
            success = db.add_favorite_fund(fund_code, fund_info['name'], fund_info['type'])
            if success:
                success_count += 1
        
        db.close()
        
        if success_count > 0:
            QMessageBox.information(self, '成功', f'成功添加 {success_count} 只基金到自选')
            self.load_favorite_funds()
        else:
            QMessageBox.error(self, '错误', '添加自选失败，基金可能已在自选列表中')
    
    def search_funds(self):
        """搜索基金"""
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, '提示', '请输入搜索内容')
            return
        
        # 使用真实API数据进行搜索
        from api.fund_api import FundAPI
        api = FundAPI()
        
        # 获取基金排行榜数据作为搜索结果
        fund_rank = api.get_fund_rank()
        
        # 如果API返回空数据，使用默认数据
        if not fund_rank:
            fund_rank = [
                {'code': '000001', 'name': '华夏成长混合', 'net_value': '1.5678', 'day_growth': '+0.87%'},
                {'code': '110022', 'name': '易方达消费行业股票', 'net_value': '1.0234', 'day_growth': '+0.12%'},
                {'code': '001475', 'name': '易方达国防军工混合', 'net_value': '3.2456', 'day_growth': '+1.23%'},
                {'code': '000689', 'name': '前海开源新经济混合', 'net_value': '2.8765', 'day_growth': '+0.98%'},
                {'code': '001593', 'name': '天弘中证计算机ETF联接', 'net_value': '1.6789', 'day_growth': '+0.21%'},
                {'code': '000008', 'name': '华夏全球精选', 'net_value': '2.3456', 'day_growth': '+0.43%'},
                {'code': '000006', 'name': '华夏优势增长', 'net_value': '1.9876', 'day_growth': '+0.65%'}
            ]
        
        # 过滤搜索结果
        search_results = []
        for fund in fund_rank:
            if search_text in fund['code'] or search_text in fund['name']:
                # 获取真实的基金类型
                fund_info = api.get_fund_info(fund['code'])
                if fund_info:
                    fund['type'] = fund_info['type']
                else:
                    fund['type'] = '未知类型'
                search_results.append(fund)
        
        # 如果没有匹配结果，尝试直接通过基金代码获取
        if not search_results:
            # 尝试直接获取基金信息
            fund_info = api.get_fund_info(search_text)
            if fund_info:
                # 获取基金净值
                fund_net_value = api.get_fund_net_value(search_text)
                if fund_net_value:
                    search_results.append({
                        'code': search_text,
                        'name': fund_info['name'],
                        'type': fund_info['type'],
                        'net_value': fund_net_value['net_value'],
                        'day_growth': fund_net_value['day_growth']
                    })
        
        # 显示搜索结果
        self.search_result_table.setRowCount(len(search_results))
        for row, fund in enumerate(search_results):
            # 添加复选框
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.Unchecked)
            self.search_result_table.setItem(row, 0, checkbox_item)
            
            # 基金名称
            name_item = QTableWidgetItem(fund.get('name', ''))
            self.search_result_table.setItem(row, 1, name_item)
            
            # 基金代码
            code_item = QTableWidgetItem(fund.get('code', ''))
            self.search_result_table.setItem(row, 2, code_item)
            
            # 基金类型（真实数据）
            type_item = QTableWidgetItem(fund.get('type', '未知类型'))
            self.search_result_table.setItem(row, 3, type_item)
    
    def refresh_data(self):
        """刷新数据"""
        self.load_favorite_funds()
        QMessageBox.information(self, '成功', '数据刷新完成')
