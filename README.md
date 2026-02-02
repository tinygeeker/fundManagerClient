# 📊 基金收益预测客户端

一款功能强大的基金收益预测和管理工具，支持基金自选、实时刷新、行情分析等功能。

## ✨ 功能特性

### 📈 核心功能
- **基金自选管理**：添加、删除、管理个人关注的基金
- **实时数据刷新**：下拉刷新获取最新基金净值和涨跌幅
- **组合管理**：创建和管理多个基金组合
- **收益预测**：基于历史数据和市场情绪的基金收益预测

### 📋 模块介绍
- **刷新模块**：管理基金组合，实时更新基金数据
- **自选模块**：管理个人关注的基金，支持搜索和批量操作
- **行情模块**：展示大盘指数、市场情绪、基金排行榜等信息

### 🌍 行情数据
- **A股**：上证指数、深证成指、创业板指、科创50、北证50、上证50、中证500、中证1000、沪深300
- **港股**：恒生指数、恒生科技、恒生国企
- **美股**：纳斯达克、标普500、道琼斯
- **亚太**：日经225、印度孟买sensex、越南胡志明

## 🛠️ 技术栈

- **前端框架**：PyQt5
- **后端API**：基金数据API（含模拟数据 fallback）
- **数据存储**：SQLite
- **数据处理**：Python
- **网络请求**：requests

## 🚀 安装说明

### 1. 克隆项目
```bash
git clone https://github.com/tinygeeker/fund-manager-client.git
cd fund-manager-client
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python main.py
```

## 📖 使用方法

### 1. 添加基金到自选
- 在「自选」标签页中，输入基金代码或名称进行搜索
- 在搜索结果中勾选要添加的基金
- 点击「添加到自选」按钮

### 2. 创建基金组合
- 在「刷新」标签页中，输入组合名称
- 点击「添加组合」按钮
- 选择创建的组合，输入基金代码添加基金

### 3. 查看行情数据
- 在「行情」标签页中，查看各类指数和基金排行榜
- 点击「刷新数据」按钮获取最新行情

## 🎨 界面预览

### 刷新模块
![刷新模块](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fund%20manager%20refresh%20tab%20interface%20with%20portfolio%20management%20and%20fund%20list&image_size=landscape_16_9)

### 自选模块
![自选模块](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fund%20manager%20favorite%20tab%20interface%20with%20search%20function%20and%20fund%20list&image_size=landscape_16_9)

### 行情模块
![行情模块](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fund%20manager%20market%20tab%20interface%20with%20stock%20indices%20and%20rankings&image_size=landscape_16_9)

## 项目贡献

如果你觉得项目有用，就请我喝杯奶茶吧。 :tropical_drink:

![donate](https://tinygeeker.github.io/assets/user/donate.jpg)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🌟 鸣谢

- 感谢所有支持和使用本项目的用户
- 感谢提供基金数据 API 的服务提供商

---

💖 希望这个工具能帮助您更好地管理和预测基金收益！
