#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金收益预测可视化客户端
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QToolBar, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.refresh_tab import RefreshTab
from ui.favorite_tab import FavoriteTab
from ui.market_tab import MarketTab
from database.db_manager import init_db

class FundManagerApp(QMainWindow):
    """基金管理器主应用"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('基金收益预测')
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化数据库
        init_db()
        
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 添加操作菜单
        action_menu = menubar.addMenu('操作')
        
        # 添加关闭操作
        close_action = QAction('关闭', self)
        close_action.triggered.connect(self.close)
        action_menu.addAction(close_action)
        
        # 添加全屏操作
        fullscreen_action = QAction('全屏', self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        action_menu.addAction(fullscreen_action)
        
        # 添加设置菜单
        settings_menu = menubar.addMenu('设置')
        
        # 添加刷新设置选项
        refresh_settings_action = QAction('刷新设置', self)
        refresh_settings_action.triggered.connect(self.show_refresh_settings)
        settings_menu.addAction(refresh_settings_action)
        
        # 添加网络设置选项
        network_settings_action = QAction('网络设置', self)
        network_settings_action.triggered.connect(self.show_network_settings)
        settings_menu.addAction(network_settings_action)
        
        # 添加界面设置选项
        interface_settings_action = QAction('界面设置', self)
        interface_settings_action.triggered.connect(self.show_interface_settings)
        settings_menu.addAction(interface_settings_action)
        
        # 添加关于菜单
        about_menu = menubar.addMenu('关于')
        
        # 添加打赏选项
        donate_action = QAction('打赏', self)
        donate_action.triggered.connect(self.show_donate)
        about_menu.addAction(donate_action)
        
        # 添加主页选项
        homepage_action = QAction('主页', self)
        homepage_action.triggered.connect(self.open_homepage)
        about_menu.addAction(homepage_action)
        
        # 添加说明选项
        description_action = QAction('说明', self)
        description_action.triggered.connect(self.show_about_description)
        about_menu.addAction(description_action)
        
        # 创建主控件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建垂直布局
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # 添加三个标签页
        self.refresh_tab = RefreshTab()
        self.favorite_tab = FavoriteTab()
        self.market_tab = MarketTab()
        
        self.tab_widget.addTab(self.refresh_tab, '刷新')
        self.tab_widget.addTab(self.favorite_tab, '自选')
        self.tab_widget.addTab(self.market_tab, '行情')
    
    def toggle_fullscreen(self):
        """切换全屏状态"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_refresh_settings(self):
        """显示刷新设置"""
        refresh_settings_text = "刷新设置：\n\n"
        refresh_settings_text += "1. 自动刷新频率\n"
        refresh_settings_text += "2. 手动刷新选项\n"
        refresh_settings_text += "3. 组合刷新设置\n"
        
        QMessageBox.information(self, '刷新设置', refresh_settings_text)
    
    def show_network_settings(self):
        """显示网络设置"""
        network_settings_text = "网络设置：\n\n"
        network_settings_text += "1. 网络连接测试\n"
        network_settings_text += "2. API超时设置\n"
        network_settings_text += "3. 代理设置\n"
        
        QMessageBox.information(self, '网络设置', network_settings_text)
    
    def show_interface_settings(self):
        """显示界面设置"""
        interface_settings_text = "界面设置：\n\n"
        interface_settings_text += "1. 主题设置\n"
        interface_settings_text += "2. 字体大小\n"
        interface_settings_text += "3. 布局调整\n"
        
        QMessageBox.information(self, '界面设置', interface_settings_text)
    
    def show_about_description(self):
        """显示关于信息"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        
        # 创建关于对话框
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle('关于')
        about_dialog.resize(400, 200)  # 减小对话框高度
        
        layout = QVBoxLayout(about_dialog)
        # 减小文字间距，设置为默认值的一半
        layout.setSpacing(10)
        
        # 添加软件信息
        app_name_label = QLabel('基金收益预测客户端')
        app_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name_label)
        
        version_label = QLabel('版本：1.0.0')
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        desc_label = QLabel('一款功能强大的基金收益预测和管理工具')
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # 添加禁止商业用途声明
        commercial_label = QLabel('禁止一切商业用途！')
        commercial_label.setAlignment(Qt.AlignCenter)
        commercial_label.setStyleSheet('QLabel { color: red; font-weight: bold; }')
        layout.addWidget(commercial_label)
        
        # 删除关闭按钮，使用对话框默认的关闭方式
        
        about_dialog.exec_()
    
    def show_donate(self):
        """显示打赏照片"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
        from PyQt5.QtGui import QPixmap
        
        # 创建打赏对话框
        donate_dialog = QDialog(self)
        donate_dialog.setWindowTitle('打赏')
        donate_dialog.resize(700, 450)
        
        layout = QVBoxLayout(donate_dialog)
        # 移除布局边距
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加打赏图片
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        
        # 加载assets/donate.jpg图片
        donate_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'donate.jpg')
        
        if os.path.exists(donate_image_path):
            pixmap = QPixmap(donate_image_path)
            if not pixmap.isNull():
                # 调整图片大小以适应对话框
                scaled_pixmap = pixmap.scaled(680, 430, Qt.KeepAspectRatio)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText('图片加载失败')
                image_label.setStyleSheet('QLabel { border: 1px solid #ccc; padding: 100px; font-size: 16px; }')
        else:
            image_label.setText('打赏图片不存在')
            image_label.setStyleSheet('QLabel { border: 1px solid #ccc; padding: 100px; font-size: 16px; }')
        
        layout.addWidget(image_label)
        
        donate_dialog.exec_()
    
    def open_homepage(self):
        """打开主页"""
        import webbrowser
        webbrowser.open('https://github.com/tinygeeker')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FundManagerApp()
    window.show()
    sys.exit(app.exec_())
