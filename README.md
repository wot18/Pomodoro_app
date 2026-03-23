# 番茄钟 Pomodoro Timer

一个功能完整的番茄工作法计时器应用，支持Windows 11系统通知和系统托盘功能。

## 功能特性

### 核心功能
- **番茄计时**：25分钟工作时间 + 5分钟短休息，4个番茄后20分钟长休息
- **可自定义时间**：工作时间、短休息、长休息时间均可调节
- **智能提醒**：时间结束自动弹出通知
- **空闲检测**：5分钟未开启新番茄时提醒用户
- **数据统计**：记录每日完成的番茄数量

### 数据记录
- 显示昨日完成番茄数，激励今日工作
- 自动保存每天完成的番茄钟数据到本地
- 数据存储在用户目录下的 `.pomodoro_data.json`

### Windows通知
- 工作时间结束时弹出通知
- 休息时间结束时弹出通知
- 完整番茄周期完成时弹出通知
- 系统托盘图标支持

## 安装运行

### 方法1：使用conda（推荐）

```bash
# 创建虚拟环境
conda create -n pomodoro python=3.11 -y

# 激活环境
conda activate pomodoro

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方法2：使用自动启动脚本

**Windows用户：**
双击运行 `run.bat`

**Linux/Mac用户：**
```bash
chmod +x run.sh
./run.sh
```

## 依赖说明

- **PyQt6**: GUI框架，用于创建美观的桌面应用界面
- **win11toast**: Windows 11 Toast通知（Windows系统）

## 文件结构

```
Pomodoro_app/
├── main.py              # 主程序，包含UI和逻辑
├── timer.py             # 计时器核心逻辑
├── config.py            # 配置管理
├── data_manager.py      # 数据管理（每日番茄记录）
├── notifier.py          # 通知系统
├── requirements.txt     # Python依赖
├── run.bat             # Windows启动脚本
├── run.sh              # Linux/Mac启动脚本
└── README.md           # 说明文档
```

## 使用说明

### 基本使用
1. 启动程序后，点击「开始番茄钟」按钮
2. 25分钟计时开始后，专注工作
3. 工作时间结束时会收到通知，自动进入休息时间
4. 休息时间结束后，选择开始下一个番茄或稍后再开始

### 自定义设置
点击「设置」按钮可以调整：
- 工作时长（默认25分钟）
- 短休息时长（默认5分钟）
- 长休息时长（默认20分钟）
- 长休息间隔（默认4个番茄）

### 数据统计
- 界面上方显示「今日」和「昨日」完成的番茄数量
- 昨日数据用于激励今日工作
- 数据自动保存，程序关闭后不会丢失

### 系统托盘
- 点击窗口关闭按钮会将应用最小化到系统托盘
- 双击托盘图标可恢复窗口
- 右键托盘图标可选择「显示」或「退出」

## 通知说明

程序会在以下时机发送Windows通知：
- ⏱️ **工作时间结束**：提示休息
- ☕ **休息时间结束**：提示开始工作
- ✅ **番茄周期完成**：提醒是否开始下一个
- 💤 **5分钟空闲**：询问是否开始番茄钟

## 数据存储

- 配置文件：`%USERPROFILE%\.pomodoro_config.json`
- 数据文件：`%USERPROFILE%\.pomodoro_data.json`

## 技术栈

- Python 3.11
- PyQt6（GUI框架）
- win11toast（Windows通知）

## 许可证

MIT License

## 开发说明

如需修改源码：
1. 编辑 `main.py` 修改界面
2. 编辑 `timer.py` 修改计时器逻辑
3. 编辑 `config.py` 修改配置管理
4. 编辑 `data_manager.py` 修改数据存储逻辑
5. 编辑 `notifier.py` 修改通知行为
