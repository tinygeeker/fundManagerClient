#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行情模块界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QGridLayout, QLabel, QGroupBox,
    QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from api.fund_api import FundAPI

class MarketUpdateThread(QThread):
    """市场数据更新线程"""
    market_index_signal = pyqtSignal(dict)
    market_sentiment_signal = pyqtSignal(dict)
    fund_rank_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.api = FundAPI()
    
    def run(self):
        # 获取大盘指数
        market_index = self.api.get_market_index()
        self.market_index_signal.emit(market_index)
        
        # 获取市场情绪
        market_sentiment = self.api.get_market_sentiment()
        self.market_sentiment_signal.emit(market_sentiment)
        
        # 获取基金排行榜
        fund_rank = {
            '涨幅榜': self.api.get_fund_rank('涨跌幅'),
            '自选榜': self.api.get_fund_rank('涨跌幅'),  # 暂时使用涨幅榜数据
            '持有榜': self.api.get_fund_rank('涨跌幅')   # 暂时使用涨幅榜数据
        }
        self.fund_rank_signal.emit(fund_rank)

class MarketTab(QWidget):
    """行情模块界面"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """初始化界面"""
        self.layout = QVBoxLayout(self)
        
        # 顶部刷新按钮
        top_layout = QHBoxLayout()
        self.refresh_btn = QPushButton('刷新数据')
        self.refresh_btn.clicked.connect(self.refresh_data)
        top_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(top_layout)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Vertical)
        
        # 第一部分：大盘指数
        market_index_group = QGroupBox('大盘指数')
        market_index_layout = QHBoxLayout(market_index_group)
        self.market_index_labels = {}
        
        # 指数分类
        index_categories = {
            'A股': ['上证指数', '深证成指', '创业板指', '科创50', '北证50', '上证50', '中证500', '中证1000', '沪深300'],
            '港股': ['恒生指数', '恒生科技', '恒生国企'],
            '美股': ['纳斯达克', '标普500', '道琼斯'],
            '亚太': ['日经225', '印度孟买sensex', '越南胡志明']
        }
        
        for category, indices in index_categories.items():
            # 创建分类组
            category_group = QGroupBox(category)
            category_layout = QGridLayout(category_group)
            # 设置垂直方向的对齐方式为顶部
            category_layout.setAlignment(Qt.AlignTop)
            
            for i, index_name in enumerate(indices):
                # 指数名称
                name_label = QLabel(index_name)
                category_layout.addWidget(name_label, i, 0)
                
                # 指数数据
                data_label = QLabel('--')
                data_label.setObjectName(f'{index_name}_data')
                self.market_index_labels[index_name] = data_label
                category_layout.addWidget(data_label, i, 1)
            
            market_index_layout.addWidget(category_group, 1)
        
        main_splitter.addWidget(market_index_group)
        
        # 第二部分：市场情绪和涨跌分布
        market_status_group = QGroupBox('市场状态')
        market_status_layout = QHBoxLayout(market_status_group)
        
        # 市场情绪
        sentiment_group = QGroupBox('市场情绪')
        sentiment_layout = QVBoxLayout(sentiment_group)
        # 设置垂直方向的对齐方式为顶部
        sentiment_layout.setAlignment(Qt.AlignTop)
        self.sentiment_label = QLabel('情绪指数: --')
        self.sentiment_desc_label = QLabel('市场情绪: --')
        self.main_fund_label = QLabel('主力资金: --')
        sentiment_layout.addWidget(self.sentiment_label)
        sentiment_layout.addWidget(self.sentiment_desc_label)
        sentiment_layout.addWidget(self.main_fund_label)
        market_status_layout.addWidget(sentiment_group)
        
        # 涨跌分布
        distribution_group = QGroupBox('涨跌分布')
        distribution_layout = QVBoxLayout(distribution_group)
        # 设置垂直方向的对齐方式为顶部
        distribution_layout.setAlignment(Qt.AlignTop)
        self.up_stocks_label = QLabel('上涨: --')
        self.down_stocks_label = QLabel('下跌: --')
        self.flat_stocks_label = QLabel('平盘: --')
        self.up_down_ratio_label = QLabel('涨跌比: --')
        distribution_layout.addWidget(self.up_stocks_label)
        distribution_layout.addWidget(self.down_stocks_label)
        distribution_layout.addWidget(self.flat_stocks_label)
        distribution_layout.addWidget(self.up_down_ratio_label)
        market_status_layout.addWidget(distribution_group)
        
        main_splitter.addWidget(market_status_group)
        
        # 第三部分：排行榜
        ranking_group = QGroupBox('排行榜')
        ranking_layout = QHBoxLayout(ranking_group)
        
        # 排行榜分类
        ranking_categories = {
            '热搜榜': ['序号', '基金名称', '基金代码'],
            '涨幅榜': ['序号', '基金名称', '基金代码'],
            '自选榜': ['序号', '基金名称', '基金代码'],
            '持有榜': ['序号', '基金名称', '基金代码']
        }
        
        # 存储所有排行榜表格
        self.rank_tables = {}
        
        for category, headers in ranking_categories.items():
            # 创建分类组
            category_group = QGroupBox(category)
            category_layout = QVBoxLayout(category_group)
            # 设置垂直方向的对齐方式为顶部
            category_layout.setAlignment(Qt.AlignTop)
            
            # 创建表格
            table = QTableWidget()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            # 隐藏垂直表头（行号）
            table.verticalHeader().setVisible(False)
            # 设置列宽
            table.setColumnWidth(0, 30)  # 序号列宽度
            table.setColumnWidth(2, 60)  # 基金代码列宽度
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 基金名称列自动拉伸
            # 启用上下文菜单
            table.setContextMenuPolicy(Qt.CustomContextMenu)
            table.customContextMenuRequested.connect(lambda pos, t=table: self.show_rank_context_menu(pos, t))
            table.setMaximumHeight(300)  # 设置最大高度
            self.rank_tables[category] = table
            
            category_layout.addWidget(table)
            ranking_layout.addWidget(category_group, 1)
        
        main_splitter.addWidget(ranking_group)
        
        self.layout.addWidget(main_splitter)
    
    def refresh_data(self):
        """刷新数据"""
        # 启动线程更新市场数据
        self.update_thread = MarketUpdateThread()
        self.update_thread.market_index_signal.connect(self.update_market_index)
        self.update_thread.market_sentiment_signal.connect(self.update_market_sentiment)
        self.update_thread.fund_rank_signal.connect(self.update_fund_rank)
        self.update_thread.start()
    
    def update_market_index(self, market_index):
        """更新大盘指数"""
        for index_name, data in market_index.items():
            if index_name in self.market_index_labels:
                price = data.get('price', 0)
                change_percent = data.get('change_percent', 0)
                
                # 设置颜色
                color = QColor('red') if change_percent > 0 else QColor('green') if change_percent < 0 else QColor('black')
                
                # 更新标签
                label = self.market_index_labels[index_name]
                label.setText(f"{price:.2f} ({change_percent:+.2f}%)")
                label.setStyleSheet(f"color: {color.name()}")
    
    def update_market_sentiment(self, market_sentiment):
        """更新市场情绪"""
        # 更新情绪指数
        sentiment_index = market_sentiment.get('sentiment_index', 0)
        self.sentiment_label.setText(f"情绪指数: {sentiment_index}")
        
        # 更新情绪描述
        description = market_sentiment.get('description', '未知')
        self.sentiment_desc_label.setText(f"市场情绪: {description}")
        
        # 更新主力资金
        main_fund_inflow = market_sentiment.get('main_fund_inflow', 0)
        self.main_fund_label.setText(f"主力资金: {main_fund_inflow:+.2f} 亿元")
        
        # 更新涨跌分布
        up_stocks = market_sentiment.get('up_stocks', 0)
        down_stocks = market_sentiment.get('down_stocks', 0)
        flat_stocks = market_sentiment.get('flat_stocks', 0)
        
        self.up_stocks_label.setText(f"上涨: {up_stocks}")
        self.down_stocks_label.setText(f"下跌: {down_stocks}")
        self.flat_stocks_label.setText(f"平盘: {flat_stocks}")
        
        # 更新涨跌比
        if down_stocks > 0:
            ratio = f"{up_stocks}:{down_stocks}"
            # 创建富文本标签，上涨用红色，下跌用绿色
            self.up_down_ratio_label.setText(f"涨跌比: <font color='red'>{up_stocks}</font>:<font color='green'>{down_stocks}</font>")
            self.up_down_ratio_label.setTextFormat(1)  # 设置为富文本格式
        else:
            self.up_down_ratio_label.setText("涨跌比: --")
        
        # 更新热搜榜
        hot_funds = market_sentiment.get('hot_funds', [])
        # 如果没有热搜基金数据，使用默认数据
        if not hot_funds:
            hot_funds = [
                {'code': '000001', 'name': '华夏成长混合', 'reason': '科技板块领涨', 'heat': '100'},
                {'code': '110022', 'name': '易方达消费行业股票', 'reason': '消费升级概念', 'heat': '95'},
                {'code': '001475', 'name': '易方达国防军工混合', 'reason': '军工板块异动', 'heat': '90'},
                {'code': '000689', 'name': '前海开源新经济混合', 'reason': '新能源题材', 'heat': '85'},
                {'code': '001593', 'name': '天弘中证计算机ETF联接', 'reason': '计算机板块走强', 'heat': '80'},
                {'code': '000008', 'name': '华夏全球精选', 'reason': '全球市场走强', 'heat': '75'},
                {'code': '000006', 'name': '华夏优势增长', 'reason': '优势行业表现', 'heat': '70'}
            ]
        
        # 填充热搜榜表格
        if '热搜榜' in self.rank_tables:
            table = self.rank_tables['热搜榜']
            table.setRowCount(len(hot_funds))
            
            for row, fund in enumerate(hot_funds):
                # 序号
                index_item = QTableWidgetItem(str(row + 1))
                table.setItem(row, 0, index_item)
                
                # 基金名称
                name_item = QTableWidgetItem(fund.get('name', ''))
                table.setItem(row, 1, name_item)
                
                # 基金代码
                code_item = QTableWidgetItem(fund.get('code', ''))
                table.setItem(row, 2, code_item)
    
    def update_fund_rank(self, fund_rank):
        """更新基金排行榜"""
        for rank_type, funds in fund_rank.items():
            if rank_type in self.rank_tables:
                table = self.rank_tables[rank_type]
                table.setRowCount(len(funds))
                
                for row, fund in enumerate(funds):
                    # 序号
                    index_item = QTableWidgetItem(str(row + 1))
                    table.setItem(row, 0, index_item)
                    
                    # 基金名称
                    name_item = QTableWidgetItem(fund.get('name', ''))
                    table.setItem(row, 1, name_item)
                    
                    # 基金代码
                    code_item = QTableWidgetItem(fund.get('code', ''))
                    table.setItem(row, 2, code_item)
    
    def show_rank_context_menu(self, position, table):
        """显示排行榜上下文菜单"""
        # 获取当前选中的项
        selected_items = table.selectedItems()
        if not selected_items:
            return
        
        # 获取选中行
        row = selected_items[0].row()
        
        # 获取基金代码和名称
        fund_code = table.item(row, 2).text()
        fund_name = table.item(row, 1).text()
        
        # 创建上下文菜单
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        # 添加加入自选动作
        add_to_favorite_action = menu.addAction('加入自选')
        add_to_favorite_action.triggered.connect(lambda: self.add_fund_to_favorite(fund_code, fund_name))
        
        # 显示菜单
        menu.exec_(table.mapToGlobal(position))
    
    def add_fund_to_favorite(self, fund_code, fund_name):
        """添加基金到自选"""
        from database.db_manager import FundDB
        from api.fund_api import FundAPI
        
        # 验证基金代码是否有效
        api = FundAPI()
        fund_info = api.get_fund_info(fund_code)
        if not fund_info:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.error(self, '错误', f'基金 {fund_name} 不存在')
            return
        
        # 添加到数据库
        db = FundDB()
        success = db.add_favorite_fund(fund_code, fund_info['name'], fund_info['type'])
        db.close()
        
        from PyQt5.QtWidgets import QMessageBox
        if success:
            QMessageBox.information(self, '成功', f'基金 {fund_info["name"]} 已添加到自选')
        else:
            QMessageBox.warning(self, '提示', f'基金 {fund_info["name"]} 已在自选列表中')
