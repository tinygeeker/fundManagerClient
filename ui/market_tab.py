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
        self.up_stocks_label = QLabel('上涨: --')
        self.down_stocks_label = QLabel('下跌: --')
        self.flat_stocks_label = QLabel('平盘: --')
        distribution_layout.addWidget(self.up_stocks_label)
        distribution_layout.addWidget(self.down_stocks_label)
        distribution_layout.addWidget(self.flat_stocks_label)
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
            table.setColumnWidth(0, 50)  # 序号列宽度
            table.setColumnWidth(2, 100)  # 基金代码列宽度
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 基金名称列自动拉伸
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
        
        # 更新热搜榜
        hot_funds = market_sentiment.get('hot_funds', [])
        # 如果没有热搜基金数据，使用默认数据
        if not hot_funds:
            hot_funds = [
                {'code': '000001', 'name': '华夏成长混合', 'reason': '科技板块领涨', 'heat': '100'},
                {'code': '110022', 'name': '易方达消费行业股票', 'reason': '消费升级概念', 'heat': '95'},
                {'code': '001475', 'name': '易方达国防军工混合', 'reason': '军工板块异动', 'heat': '90'},
                {'code': '000689', 'name': '前海开源新经济混合', 'reason': '新能源题材', 'heat': '85'},
                {'code': '001593', 'name': '天弘中证计算机ETF联接', 'reason': '计算机板块走强', 'heat': '80'}
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
