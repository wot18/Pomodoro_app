"""主窗口UI实现"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QGroupBox,
    QDialog,
    QFrame,
    QProgressBar,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QSizePolicy,
    QSlider,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QCloseEvent
from pathlib import Path

from config import Config
from data_manager import DataManager
from timer import PomodoroTimer, TimerState
from notifier import Notifier


class PomodoroCompleteDialog(QDialog):
    """番茄完成对话框 - 询问是否开始下一个番茄钟"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("番茄完成！")
        self.setModal(True)
        self.setFixedSize(450, 220)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 恭喜信息
        label = QLabel("🎉 恭喜！完成了一个番茄钟！")
        label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #27AE60;")
        layout.addWidget(label)

        question = QLabel("是否开始下一个番茄钟？")
        question.setFont(QFont("Microsoft YaHei", 13))
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(question)

        layout.addSpacing(20)

        # 按钮
        btn_layout = QHBoxLayout()

        self.yes_btn = QPushButton("开始下一个番茄钟")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_layout.addWidget(self.yes_btn)

        self.no_btn = QPushButton("暂不")
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        btn_layout.addWidget(self.no_btn)

        layout.addLayout(btn_layout)

        # 连接信号
        self.yes_btn.clicked.connect(lambda: self.done(1))
        self.no_btn.clicked.connect(lambda: self.done(0))


class IdleReminderDialog(QDialog):
    """空闲提醒对话框 - 5分钟未操作提醒"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("休息一下？")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        label = QLabel("已经5分钟没有开启新的番茄钟了！")
        label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(label)

        question = QLabel("要现在开始一个新的番茄钟吗？")
        question.setFont(QFont("Microsoft YaHei", 12))
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(question)

        layout.addSpacing(20)

        btn_layout = QHBoxLayout()

        self.yes_btn = QPushButton("开始番茄钟")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45B7AA;
            }
        """)
        btn_layout.addWidget(self.yes_btn)

        self.later_btn = QPushButton("稍后提醒")
        self.later_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        btn_layout.addWidget(self.later_btn)

        self.skip_btn = QPushButton("跳过")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7F8C8D;
                border: 2px solid #95A5A6;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ECF0F1;
            }
        """)
        btn_layout.addWidget(self.skip_btn)

        layout.addLayout(btn_layout)

        self.yes_btn.clicked.connect(lambda: self.done(1))
        self.later_btn.clicked.connect(lambda: self.done(2))
        self.skip_btn.clicked.connect(lambda: self.done(0))


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("时间设置")
        self.setFixedSize(700, 620)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 25, 40, 25)

        # 标题
        title = QLabel("时间设置")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # 工作时间设置
        work_group = QGroupBox("工作时间")
        work_group.setFont(QFont("Microsoft YaHei", 12))
        work_group.setMinimumHeight(100)
        work_layout = QVBoxLayout(work_group)
        work_layout.setSpacing(8)
        work_layout.setContentsMargins(20, 25, 20, 15)

        work_header = QHBoxLayout()
        work_header.setSpacing(15)
        work_label = QLabel("时长:")
        work_label.setFont(QFont("Microsoft YaHei", 12))
        work_label.setMinimumWidth(50)
        work_header.addWidget(work_label)

        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setSuffix(" 分钟")
        self.work_spin.setFixedWidth(130)
        self.work_spin.setFont(QFont("Microsoft YaHei", 12))
        self.work_spin.setMinimumHeight(30)
        work_header.addWidget(self.work_spin)
        work_header.addStretch()

        self.work_value_label = QLabel("25 分钟")
        self.work_value_label.setMinimumWidth(80)
        self.work_value_label.setStyleSheet(
            "font-weight: bold; color: #E74C3C; font-size: 14px;"
        )
        self.work_value_label.setFont(QFont("Microsoft YaHei", 12))
        work_header.addWidget(self.work_value_label)
        work_layout.addLayout(work_header)

        self.work_slider = QSlider(Qt.Orientation.Horizontal)
        self.work_slider.setRange(1, 120)
        self.work_slider.setValue(25)
        self.work_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.work_slider.setTickInterval(10)
        self.work_slider.setMinimumHeight(30)
        self.work_slider.valueChanged.connect(self.on_work_slider_changed)
        self.work_spin.valueChanged.connect(self.on_work_spin_changed)
        work_layout.addWidget(self.work_slider)

        layout.addWidget(work_group)

        # 短休息设置
        short_break_group = QGroupBox("短休息")
        short_break_group.setFont(QFont("Microsoft YaHei", 12))
        short_break_group.setMinimumHeight(100)
        short_break_layout = QVBoxLayout(short_break_group)
        short_break_layout.setSpacing(8)
        short_break_layout.setContentsMargins(20, 25, 20, 15)

        short_header = QHBoxLayout()
        short_header.setSpacing(15)
        short_label = QLabel("时长:")
        short_label.setFont(QFont("Microsoft YaHei", 12))
        short_label.setMinimumWidth(50)
        short_header.addWidget(short_label)

        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 60)
        self.short_break_spin.setSuffix(" 分钟")
        self.short_break_spin.setFixedWidth(130)
        self.short_break_spin.setFont(QFont("Microsoft YaHei", 12))
        self.short_break_spin.setMinimumHeight(30)
        short_header.addWidget(self.short_break_spin)
        short_header.addStretch()

        self.short_break_value_label = QLabel("5 分钟")
        self.short_break_value_label.setMinimumWidth(80)
        self.short_break_value_label.setStyleSheet(
            "font-weight: bold; color: #27AE60; font-size: 14px;"
        )
        self.short_break_value_label.setFont(QFont("Microsoft YaHei", 12))
        short_header.addWidget(self.short_break_value_label)
        short_break_layout.addLayout(short_header)

        self.short_break_slider = QSlider(Qt.Orientation.Horizontal)
        self.short_break_slider.setRange(1, 60)
        self.short_break_slider.setValue(5)
        self.short_break_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.short_break_slider.setTickInterval(5)
        self.short_break_slider.setMinimumHeight(30)
        self.short_break_slider.valueChanged.connect(self.on_short_break_slider_changed)
        self.short_break_spin.valueChanged.connect(self.on_short_break_spin_changed)
        short_break_layout.addWidget(self.short_break_slider)

        layout.addWidget(short_break_group)

        # 长休息设置
        long_break_group = QGroupBox("长休息")
        long_break_group.setFont(QFont("Microsoft YaHei", 12))
        long_break_group.setMinimumHeight(100)
        long_break_layout = QVBoxLayout(long_break_group)
        long_break_layout.setSpacing(8)
        long_break_layout.setContentsMargins(20, 25, 20, 15)

        long_header = QHBoxLayout()
        long_header.setSpacing(15)
        long_label = QLabel("时长:")
        long_label.setFont(QFont("Microsoft YaHei", 12))
        long_label.setMinimumWidth(50)
        long_header.addWidget(long_label)

        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 120)
        self.long_break_spin.setSuffix(" 分钟")
        self.long_break_spin.setFixedWidth(130)
        self.long_break_spin.setFont(QFont("Microsoft YaHei", 12))
        self.long_break_spin.setMinimumHeight(30)
        long_header.addWidget(self.long_break_spin)
        long_header.addStretch()

        self.long_break_value_label = QLabel("20 分钟")
        self.long_break_value_label.setMinimumWidth(80)
        self.long_break_value_label.setStyleSheet(
            "font-weight: bold; color: #3498DB; font-size: 14px;"
        )
        self.long_break_value_label.setFont(QFont("Microsoft YaHei", 12))
        long_header.addWidget(self.long_break_value_label)
        long_break_layout.addLayout(long_header)

        self.long_break_slider = QSlider(Qt.Orientation.Horizontal)
        self.long_break_slider.setRange(1, 120)
        self.long_break_slider.setValue(20)
        self.long_break_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.long_break_slider.setTickInterval(10)
        self.long_break_slider.setMinimumHeight(30)
        self.long_break_slider.valueChanged.connect(self.on_long_break_slider_changed)
        self.long_break_spin.valueChanged.connect(self.on_long_break_spin_changed)
        long_break_layout.addWidget(self.long_break_slider)

        layout.addWidget(long_break_group)

        # 长休息间隔
        pomodoros_group = QGroupBox("长休息间隔")
        pomodoros_group.setFont(QFont("Microsoft YaHei", 12))
        pomodoros_group.setMinimumHeight(100)
        pomodoros_layout = QVBoxLayout(pomodoros_group)
        pomodoros_layout.setSpacing(8)
        pomodoros_layout.setContentsMargins(20, 25, 20, 15)

        pomodoros_header = QHBoxLayout()
        pomodoros_header.setSpacing(15)
        pomodoros_label = QLabel("完成番茄数:")
        pomodoros_label.setFont(QFont("Microsoft YaHei", 12))
        pomodoros_label.setMinimumWidth(90)
        pomodoros_header.addWidget(pomodoros_label)

        self.pomodoros_spin = QSpinBox()
        self.pomodoros_spin.setRange(2, 10)
        self.pomodoros_spin.setSuffix(" 个番茄")
        self.pomodoros_spin.setFixedWidth(130)
        self.pomodoros_spin.setFont(QFont("Microsoft YaHei", 12))
        self.pomodoros_spin.setMinimumHeight(30)
        pomodoros_header.addWidget(self.pomodoros_spin)
        pomodoros_header.addStretch()

        self.pomodoros_value_label = QLabel("4 个番茄")
        self.pomodoros_value_label.setMinimumWidth(80)
        self.pomodoros_value_label.setStyleSheet(
            "font-weight: bold; color: #9B59B6; font-size: 14px;"
        )
        self.pomodoros_value_label.setFont(QFont("Microsoft YaHei", 12))
        pomodoros_header.addWidget(self.pomodoros_value_label)
        pomodoros_layout.addLayout(pomodoros_header)

        self.pomodoros_slider = QSlider(Qt.Orientation.Horizontal)
        self.pomodoros_slider.setRange(2, 10)
        self.pomodoros_slider.setValue(4)
        self.pomodoros_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pomodoros_slider.setTickInterval(1)
        self.pomodoros_slider.setMinimumHeight(30)
        self.pomodoros_slider.valueChanged.connect(self.on_pomodoros_slider_changed)
        self.pomodoros_spin.valueChanged.connect(self.on_pomodoros_spin_changed)
        pomodoros_layout.addWidget(self.pomodoros_slider)

        layout.addWidget(pomodoros_group)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.setFixedSize(120, 40)
        self.save_btn.setFont(QFont("Microsoft YaHei", 12))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45B7AA;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(120, 40)
        self.cancel_btn.setFont(QFont("Microsoft YaHei", 12))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7F8C8D;
                border: 2px solid #95A5A6;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #ECF0F1;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def on_work_slider_changed(self, value):
        self.work_spin.blockSignals(True)
        self.work_spin.setValue(value)
        self.work_spin.blockSignals(False)
        self.work_value_label.setText(f"{value} 分钟")

    def on_work_spin_changed(self, value):
        self.work_slider.blockSignals(True)
        self.work_slider.setValue(value)
        self.work_slider.blockSignals(False)
        self.work_value_label.setText(f"{value} 分钟")

    def on_short_break_slider_changed(self, value):
        self.short_break_spin.blockSignals(True)
        self.short_break_spin.setValue(value)
        self.short_break_spin.blockSignals(False)
        self.short_break_value_label.setText(f"{value} 分钟")

    def on_short_break_spin_changed(self, value):
        self.short_break_slider.blockSignals(True)
        self.short_break_slider.setValue(value)
        self.short_break_slider.blockSignals(False)
        self.short_break_value_label.setText(f"{value} 分钟")

    def on_long_break_slider_changed(self, value):
        self.long_break_spin.blockSignals(True)
        self.long_break_spin.setValue(value)
        self.long_break_spin.blockSignals(False)
        self.long_break_value_label.setText(f"{value} 分钟")

    def on_long_break_spin_changed(self, value):
        self.long_break_slider.blockSignals(True)
        self.long_break_slider.setValue(value)
        self.long_break_slider.blockSignals(False)
        self.long_break_value_label.setText(f"{value} 分钟")

    def on_pomodoros_slider_changed(self, value):
        self.pomodoros_spin.blockSignals(True)
        self.pomodoros_spin.setValue(value)
        self.pomodoros_spin.blockSignals(False)
        self.pomodoros_value_label.setText(f"{value} 个番茄")

    def on_pomodoros_spin_changed(self, value):
        self.pomodoros_slider.blockSignals(True)
        self.pomodoros_slider.setValue(value)
        self.pomodoros_slider.blockSignals(False)
        self.pomodoros_value_label.setText(f"{value} 个番茄")

    def load_settings(self):
        """加载当前设置"""
        work = self.config.work_time_minutes
        short = self.config.short_break_minutes
        long = self.config.long_break_minutes
        pomodoros = self.config.pomodoros_for_long_break

        self.work_slider.setValue(work)
        self.work_spin.setValue(work)
        self.work_value_label.setText(f"{work} 分钟")

        self.short_break_slider.setValue(short)
        self.short_break_spin.setValue(short)
        self.short_break_value_label.setText(f"{short} 分钟")

        self.long_break_slider.setValue(long)
        self.long_break_spin.setValue(long)
        self.long_break_value_label.setText(f"{long} 分钟")

        self.pomodoros_slider.setValue(pomodoros)
        self.pomodoros_spin.setValue(pomodoros)
        self.pomodoros_value_label.setText(f"{pomodoros} 个番茄")

    def save_settings(self):
        """保存设置"""
        self.config.set("work_time", self.work_spin.value())
        self.config.set("short_break", self.short_break_spin.value())
        self.config.set("long_break", self.long_break_spin.value())
        self.config.set("pomodoros_before_long_break", self.pomodoros_spin.value())
        self.accept()


class PomodoroMainWindow(QMainWindow):
    """番茄钟主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("番茄钟")
        self.setFixedSize(500, 650)

        # 设置窗口图标
        icon_path = Path(__file__).parent / "favicon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 初始化组件
        self.config = Config()
        self.data_manager = DataManager()
        self.timer = PomodoroTimer(self.config)
        self.notifier = Notifier()

        # 设置系统托盘
        self.setup_system_tray()

        # 初始化UI
        self.setup_ui()
        self.apply_styles()

        # 连接信号
        self.connect_signals()

        # 空闲检测计时器
        self.idle_timer = QTimer()
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self.show_idle_reminder)
        self.last_pomodoro_complete_time = None

        # 更新显示
        self.update_display()
        self.update_statistics()

    def setup_system_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)

        # 设置托盘图标
        icon_path = Path(__file__).parent / "favicon.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self.tray_icon.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            )

        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示")
        show_action.triggered.connect(self.show_and_activate)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def show_and_activate(self):
        """显示并激活窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
        # 设置窗口在最前面显示
        self.setWindowState(
            self.windowState() & ~Qt.WindowState.WindowMinimized
            | Qt.WindowState.WindowActive
        )

    def on_tray_activated(self, reason):
        """托盘图标被激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_activate()

    def quit_application(self):
        """退出应用"""
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """关闭事件处理 - 直接退出程序"""
        self.tray_icon.hide()
        event.accept()
        QApplication.quit()

    def changeEvent(self, event):
        """窗口状态改变事件"""
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                # 最小化时隐藏到托盘
                self.hide()
                self.tray_icon.showMessage(
                    "番茄钟",
                    "应用已最小化到系统托盘，双击图标恢复",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000,
                )
                event.ignore()
                return
        super().changeEvent(event)

    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ========== 统计信息区域 ==========
        stats_group = QGroupBox("今日统计")
        stats_layout = QHBoxLayout(stats_group)

        self.yesterday_label = QLabel("昨日: 0 个番茄")
        self.yesterday_label.setFont(QFont("Microsoft YaHei", 12))
        stats_layout.addWidget(self.yesterday_label)

        stats_layout.addStretch()

        self.today_label = QLabel("今日: 0 个番茄")
        self.today_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        stats_layout.addWidget(self.today_label)

        stats_layout.addStretch()

        self.total_label = QLabel("完成: 0")
        self.total_label.setFont(QFont("Microsoft YaHei", 12))
        stats_layout.addWidget(self.total_label)

        main_layout.addWidget(stats_group)

        # ========== 主计时器区域 ==========
        timer_frame = QFrame()
        timer_frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 20px;
            }
        """)
        timer_layout = QVBoxLayout(timer_frame)

        self.state_label = QLabel("准备开始")
        self.state_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("color: #ECF0F1;")
        timer_layout.addWidget(self.state_label)

        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("Microsoft YaHei", 72, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #4ECDC4;")
        timer_layout.addWidget(self.time_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #34495E;
                height: 10px;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background-color: #4ECDC4;
            }
        """)
        timer_layout.addWidget(self.progress_bar)

        self.next_break_label = QLabel("短休息: 5分钟")
        self.next_break_label.setFont(QFont("Microsoft YaHei", 12))
        self.next_break_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_break_label.setStyleSheet("color: #BDC3C7;")
        timer_layout.addWidget(self.next_break_label)

        main_layout.addWidget(timer_frame)

        # ========== 控制按钮区域 ==========
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始番茄钟")
        self.start_btn.setFixedHeight(50)
        btn_layout.addWidget(self.start_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedHeight(50)
        btn_layout.addWidget(self.reset_btn)

        main_layout.addLayout(btn_layout)

        # ========== 设置按钮 ==========
        self.settings_btn = QPushButton("⚙ 设置")
        self.settings_btn.setFixedHeight(40)
        main_layout.addWidget(self.settings_btn)

        info_label = QLabel("💡 提示: 完成4个番茄钟后将进入20分钟长休息")
        info_label.setFont(QFont("Microsoft YaHei", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #7F8C8D;")
        main_layout.addWidget(info_label)

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECF0F1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #BDC3C7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                color: #2C3E50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                color: white;
                background-color: #3498DB;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2472A4;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #95A5A6;
            }
            QSpinBox {
                padding: 5px;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                font-size: 14px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #BDC3C7;
                height: 8px;
                background: #ECF0F1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498DB;
                border: 1px solid #2980B9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #3498DB;
                border-radius: 4px;
            }
            QLabel {
                color: #2C3E50;
            }
        """)

        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)

        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)

        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
            }
            QPushButton:hover {
                background-color: #45B7AA;
            }
        """)

    def connect_signals(self):
        """连接信号"""
        self.timer.tick.connect(self.on_timer_tick)
        self.timer.state_changed.connect(self.on_state_changed)
        self.timer.work_complete.connect(self.on_work_complete)
        self.timer.break_complete.connect(self.on_break_complete)
        self.timer.pomodoro_complete.connect(self.on_pomodoro_complete)
        self.timer.cycle_complete.connect(self.on_cycle_complete)

        self.start_btn.clicked.connect(self.on_start_clicked)
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.settings_btn.clicked.connect(self.on_settings_clicked)

    def update_display(self):
        """更新显示"""
        time_str = self.timer.get_formatted_time()
        self.time_label.setText(time_str)
        progress = self.timer.get_progress_percentage()
        self.progress_bar.setValue(int(progress))

    def update_statistics(self):
        """更新统计数据"""
        today_count = self.data_manager.get_today_completed()
        yesterday_count = self.data_manager.get_yesterday_completed()

        self.today_label.setText(f"今日: {today_count} 个番茄")
        self.yesterday_label.setText(f"昨日: {yesterday_count} 个番茄")
        self.total_label.setText(f"完成: {today_count}")

        completed = self.timer.completed_pomodoros
        if (
            completed > 0
            and (completed + 1) % self.config.pomodoros_for_long_break == 0
        ):
            self.next_break_label.setText(
                f"长休息: {self.config.long_break_minutes}分钟"
            )
        else:
            self.next_break_label.setText(
                f"短休息: {self.config.short_break_minutes}分钟"
            )

    def on_start_clicked(self):
        """开始/暂停按钮点击"""
        if self.timer.timer.isActive():
            self.timer.pause()
            self.start_btn.setText("继续")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27AE60;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
        else:
            if self.timer.state == TimerState.IDLE:
                self.timer.start_work()
            else:
                self.timer.resume()

            # 立即更新显示，确保时间立即显示
            self.update_display()

            self.start_btn.setText("暂停")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F39C12;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #E67E22;
                }
            """)

    def on_reset_clicked(self):
        """重置按钮点击"""
        self.timer.stop()
        self.start_btn.setText("开始番茄钟")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.update_display()
        self.state_label.setText("准备开始")

    def on_settings_clicked(self):
        """设置按钮点击"""
        dialog = SettingsDialog(self.config, self)
        # 设置对话框始终在最前面
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 重新加载配置
            self.config.reload()
            self.timer.set_config(self.config)
            self.update_statistics()
            self.update_display()

    def on_timer_tick(self, remaining):
        """计时器每秒触发"""
        self.update_display()

    def on_state_changed(self, state):
        """状态改变处理"""
        state_text = self.timer.get_state_text()
        self.state_label.setText(state_text)

        if state == TimerState.WORKING:
            self.time_label.setStyleSheet("color: #4ECDC4;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 5px;
                    background-color: #34495E;
                    height: 10px;
                }
                QProgressBar::chunk {
                    border-radius: 5px;
                    background-color: #4ECDC4;
                }
            """)
        elif state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self.time_label.setStyleSheet("color: #E67E22;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 5px;
                    background-color: #34495E;
                    height: 10px;
                }
                QProgressBar::chunk {
                    border-radius: 5px;
                    background-color: #E67E22;
                }
            """)

    def on_work_complete(self):
        """工作完成 - 播放声音但不发送通知"""
        self.notifier.notify_work_complete()

    def on_break_complete(self, is_long_break):
        """休息完成 - 弹出对话框询问是否开始下一个番茄"""
        self.show_next_pomodoro_dialog()

    def show_next_pomodoro_dialog(self):
        """显示是否开始下一个番茄钟的对话框"""
        # 先显示并激活窗口
        self.show_and_activate()

        dialog = PomodoroCompleteDialog(self)
        # 设置对话框始终在最前面
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        result = dialog.exec()

        # 确保对话框完全关闭
        dialog.deleteLater()
        QApplication.processEvents()

        if result == 1:  # 开始下一个番茄钟
            # 确保窗口显示并激活
            self.show_and_activate()

            # 直接开始新的番茄计时
            self.timer.start_work()
            self.update_display()
            # 更新按钮状态
            self.start_btn.setText("暂停")
            self.start_btn.setStyleSheet(
                "QPushButton { "
                "    background-color: #F39C12; "
                "    font-size: 16px; "
                "} "
                "QPushButton:hover { "
                "    background-color: #E67E22; "
                "} "
            )
        else:  # 暂不 - 隐藏窗口并启动5分钟计时器
            self.hide()
            self.tray_icon.showMessage(
                "番茄钟",
                "应用已最小化到系统托盘，双击图标恢复",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            self.idle_timer.start(5 * 60 * 1000)

    def on_pomodoro_complete(self):
        # Pomodoro cycle completed
        self.last_pomodoro_complete_time = datetime.now()

        self.start_btn.setText("开始番茄钟")
        self.start_btn.setStyleSheet(
            "QPushButton { "
            "    background-color: #E74C3C; "
            "    font-size: 16px; "
            "} "
            "QPushButton:hover { "
            "    background-color: #C0392B; "
            "} "
        )

    def on_cycle_complete(self, completed_count):
        # Cycle completed - save data
        self.data_manager.complete_pomodoro(
            self.config.work_time_minutes,
            self.config.short_break_minutes
            if self.timer.state != TimerState.LONG_BREAK
            else self.config.long_break_minutes,
        )
        self.update_statistics()

    def show_idle_reminder(self):
        # Pomodoro cycle completed
        self.last_pomodoro_complete_time = datetime.now()

        self.start_btn.setText("开始番茄钟")
        self.start_btn.setStyleSheet(
            "QPushButton { "
            "    background-color: #E74C3C; "
            "    font-size: 16px; "
            "} "
            "QPushButton:hover { "
            "    background-color: #C0392B; "
            "} "
        )

    def on_cycle_complete(self, completed_count):
        # Cycle completed - save data
        self.data_manager.complete_pomodoro(
            self.config.work_time_minutes,
            self.config.short_break_minutes
            if self.timer.state != TimerState.LONG_BREAK
            else self.config.long_break_minutes,
        )
        self.update_statistics()

    def show_idle_reminder(self):
        # Show idle reminder after 5 minutes
        if self.timer.state != TimerState.IDLE:
            return

        # 先显示并激活窗口
        self.show_and_activate()

        dialog = IdleReminderDialog(self)
        # 设置对话框始终在最前面
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        result = dialog.exec()

        if result == 1:  # 开始番茄钟
            self.on_start_clicked()
        elif result == 2:  # 稍后提醒
            self.idle_timer.start(5 * 60 * 1000)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PomodoroMainWindow()
    window.show()
    window.raise_()  # 将窗口置于最前面
    window.activateWindow()  # 激活窗口
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
