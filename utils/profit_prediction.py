#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金单日收益预测功能
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class ProfitPrediction:
    """基金收益预测类"""
    
    def __init__(self):
        pass
    
    def predict_daily_profit(self, fund_data, market_data):
        """
        预测基金单日收益
        :param fund_data: 基金历史数据
        :param market_data: 市场数据
        :return: 预测收益
        """
        try:
            # 计算基金最近的涨跌幅
            if len(fund_data) < 5:
                return 0.0
            
            # 提取最近5天的涨跌幅
            recent_growth = [float(item['day_growth'].replace('+', '').replace('-', '')) for item in fund_data[-5:]]
            
            # 计算平均涨跌幅
            avg_growth = np.mean(recent_growth)
            
            # 计算市场情绪因子
            market_sentiment = self._calculate_market_sentiment(market_data)
            
            # 计算行业因子
            industry_factor = self._calculate_industry_factor(fund_data[0].get('type', ''))
            
            # 综合预测
            predicted_profit = avg_growth * market_sentiment * industry_factor
            
            # 限制预测范围
            predicted_profit = max(-5.0, min(5.0, predicted_profit))
            
            return predicted_profit
        except Exception as e:
            print(f"预测收益失败: {e}")
            return 0.0
    
    def _calculate_market_sentiment(self, market_data):
        """
        计算市场情绪因子
        :param market_data: 市场数据
        :return: 市场情绪因子
        """
        try:
            # 计算主要指数的平均涨跌幅
            indices = ['上证指数', '深证成指', '创业板指']
            growth_rates = []
            
            for index_name in indices:
                if index_name in market_data:
                    change_percent = market_data[index_name].get('change_percent', 0)
                    growth_rates.append(change_percent)
            
            if growth_rates:
                avg_growth = np.mean(growth_rates)
                # 将市场情绪映射到0.5-1.5之间
                if avg_growth > 1:
                    return 1.5
                elif avg_growth > 0.5:
                    return 1.3
                elif avg_growth > 0:
                    return 1.1
                elif avg_growth > -0.5:
                    return 0.9
                elif avg_growth > -1:
                    return 0.7
                else:
                    return 0.5
            else:
                return 1.0
        except Exception as e:
            print(f"计算市场情绪失败: {e}")
            return 1.0
    
    def _calculate_industry_factor(self, fund_type):
        """
        计算行业因子
        :param fund_type: 基金类型
        :return: 行业因子
        """
        try:
            # 根据基金类型设置行业因子
            industry_factors = {
                '股票型': 1.2,
                '混合型': 1.0,
                '债券型': 0.8,
                '货币型': 0.1,
                '指数型': 1.1,
                'QDII': 1.0,
                'FOF': 0.9
            }
            
            for key, value in industry_factors.items():
                if key in fund_type:
                    return value
            
            return 1.0
        except Exception as e:
            print(f"计算行业因子失败: {e}")
            return 1.0
    
    def calculate_portfolio_profit(self, portfolio_funds, market_data):
        """
        计算组合收益
        :param portfolio_funds: 组合中的基金数据
        :param market_data: 市场数据
        :return: 组合预测收益
        """
        try:
            if not portfolio_funds:
                return 0.0
            
            # 计算每个基金的预测收益
            total_profit = 0.0
            for fund_data in portfolio_funds:
                if fund_data:
                    predicted_profit = self.predict_daily_profit([fund_data], market_data)
                    total_profit += predicted_profit
            
            # 计算平均收益
            avg_profit = total_profit / len(portfolio_funds)
            return avg_profit
        except Exception as e:
            print(f"计算组合收益失败: {e}")
            return 0.0
