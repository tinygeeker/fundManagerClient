#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fund_manager.db')

class FundDB:
    """基金数据库操作类"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"数据库连接失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """创建数据表"""
        try:
            # 创建自选基金表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorite_funds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fund_code TEXT UNIQUE,
                    fund_name TEXT,
                    fund_type TEXT,
                    add_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建基金组合表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS fund_portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_name TEXT,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建组合基金关联表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_funds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER,
                    fund_code TEXT,
                    FOREIGN KEY (portfolio_id) REFERENCES fund_portfolios(id)
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"创建表失败: {e}")
            self.conn.rollback()
    
    def add_favorite_fund(self, fund_code, fund_name, fund_type):
        """
        添加自选基金
        :param fund_code: 基金代码
        :param fund_name: 基金名称
        :param fund_type: 基金类型
        :return: 是否添加成功
        """
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO favorite_funds (fund_code, fund_name, fund_type) VALUES (?, ?, ?)",
                (fund_code, fund_name, fund_type)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加自选基金失败: {e}")
            self.conn.rollback()
            return False
    
    def remove_favorite_fund(self, fund_code):
        """
        移除自选基金
        :param fund_code: 基金代码
        :return: 是否移除成功
        """
        try:
            self.cursor.execute(
                "DELETE FROM favorite_funds WHERE fund_code = ?",
                (fund_code,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"移除自选基金失败: {e}")
            self.conn.rollback()
            return False
    
    def get_favorite_funds(self):
        """
        获取所有自选基金
        :return: 自选基金列表
        """
        try:
            self.cursor.execute("SELECT * FROM favorite_funds")
            funds = self.cursor.fetchall()
            return [{
                'id': fund[0],
                'code': fund[1],
                'name': fund[2],
                'type': fund[3],
                'add_time': fund[4]
            } for fund in funds]
        except Exception as e:
            print(f"获取自选基金失败: {e}")
            return []
    
    def add_portfolio(self, portfolio_name):
        """
        添加基金组合
        :param portfolio_name: 组合名称
        :return: 组合ID
        """
        try:
            self.cursor.execute(
                "INSERT INTO fund_portfolios (portfolio_name) VALUES (?)",
                (portfolio_name,)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"添加组合失败: {e}")
            self.conn.rollback()
            return None
    
    def remove_portfolio(self, portfolio_id):
        """
        移除基金组合
        :param portfolio_id: 组合ID
        :return: 是否移除成功
        """
        try:
            # 先删除组合关联的基金
            self.cursor.execute(
                "DELETE FROM portfolio_funds WHERE portfolio_id = ?",
                (portfolio_id,)
            )
            # 再删除组合
            self.cursor.execute(
                "DELETE FROM fund_portfolios WHERE id = ?",
                (portfolio_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"移除组合失败: {e}")
            self.conn.rollback()
            return False
    
    def add_fund_to_portfolio(self, portfolio_id, fund_code):
        """
        向组合添加基金
        :param portfolio_id: 组合ID
        :param fund_code: 基金代码
        :return: 是否添加成功
        """
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO portfolio_funds (portfolio_id, fund_code) VALUES (?, ?)",
                (portfolio_id, fund_code)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"向组合添加基金失败: {e}")
            self.conn.rollback()
            return False
    
    def remove_fund_from_portfolio(self, portfolio_id, fund_code):
        """
        从组合移除基金
        :param portfolio_id: 组合ID
        :param fund_code: 基金代码
        :return: 是否移除成功
        """
        try:
            self.cursor.execute(
                "DELETE FROM portfolio_funds WHERE portfolio_id = ? AND fund_code = ?",
                (portfolio_id, fund_code)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"从组合移除基金失败: {e}")
            self.conn.rollback()
            return False
    
    def get_portfolios(self):
        """
        获取所有基金组合
        :return: 组合列表
        """
        try:
            self.cursor.execute("SELECT * FROM fund_portfolios")
            portfolios = self.cursor.fetchall()
            result = []
            for portfolio in portfolios:
                portfolio_id = portfolio[0]
                # 获取组合中的基金
                self.cursor.execute(
                    "SELECT fund_code FROM portfolio_funds WHERE portfolio_id = ?",
                    (portfolio_id,)
                )
                fund_codes = [item[0] for item in self.cursor.fetchall()]
                
                result.append({
                    'id': portfolio_id,
                    'name': portfolio[1],
                    'create_time': portfolio[2],
                    'fund_codes': fund_codes
                })
            return result
        except Exception as e:
            print(f"获取基金组合失败: {e}")
            return []
    
    def update_portfolio_name(self, portfolio_id, new_name):
        """
        更新组合名称
        :param portfolio_id: 组合ID
        :param new_name: 新组合名称
        :return: 是否更新成功
        """
        try:
            self.cursor.execute(
                "UPDATE fund_portfolios SET portfolio_name = ? WHERE id = ?",
                (new_name, portfolio_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新组合名称失败: {e}")
            self.conn.rollback()
            return False
    
    def delete_portfolio(self, portfolio_id):
        """
        删除组合（与remove_portfolio方法相同，作为别名）
        :param portfolio_id: 组合ID
        :return: 是否删除成功
        """
        return self.remove_portfolio(portfolio_id)

# 初始化数据库
def init_db():
    """初始化数据库"""
    db = FundDB()
    db.create_tables()
    db.close()

# 测试数据库操作
if __name__ == '__main__':
    init_db()
    db = FundDB()
    
    # 测试添加自选基金
    db.add_favorite_fund('000001', '华夏成长混合', '混合型')
    db.add_favorite_fund('110022', '易方达消费行业股票', '股票型')
    
    # 测试获取自选基金
    print("自选基金:")
    for fund in db.get_favorite_funds():
        print(f"{fund['code']} - {fund['name']} ({fund['type']})")
    
    # 测试添加组合
    portfolio_id = db.add_portfolio('我的投资组合')
    if portfolio_id:
        # 测试向组合添加基金
        db.add_fund_to_portfolio(portfolio_id, '000001')
        db.add_fund_to_portfolio(portfolio_id, '110022')
    
    # 测试获取组合
    print("\n基金组合:")
    for portfolio in db.get_portfolios():
        print(f"{portfolio['name']} - 基金代码: {portfolio['fund_codes']}")
    
    db.close()
