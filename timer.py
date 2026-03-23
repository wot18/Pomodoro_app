"""计时器核心逻辑"""

from enum import Enum, auto
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from datetime import datetime


class TimerState(Enum):
    """计时器状态枚举"""

    IDLE = auto()  # 空闲状态
    WORKING = auto()  # 工作中
    SHORT_BREAK = auto()  # 短休息
    LONG_BREAK = auto()  # 长休息


class PomodoroTimer(QObject):
    """番茄钟计时器类"""

    # 信号定义
    tick = pyqtSignal(int)  # 每秒触发，传递剩余秒数
    state_changed = pyqtSignal(TimerState)  # 状态改变
    work_complete = pyqtSignal()  # 工作完成
    break_complete = pyqtSignal(bool)  # 休息完成（是否是长休息）
    pomodoro_complete = pyqtSignal()  # 完整番茄周期完成
    cycle_complete = pyqtSignal(int)  # 周期完成，传递番茄计数

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.state = TimerState.IDLE
        self.remaining_seconds = 0
        self.completed_pomodoros = 0
        self.total_pomodoros_today = 0

        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)

        # 空闲检测计时器
        self.idle_timer = QTimer()
        self.idle_timer.setSingleShot(True)

    def set_config(self, config):
        """更新配置"""
        self.config = config

    def start_work(self):
        """开始工作"""
        self.state = TimerState.WORKING
        self.remaining_seconds = self.config.work_time_minutes * 60
        self.timer.start(1000)  # 每秒触发一次
        self.state_changed.emit(self.state)
        self.tick.emit(self.remaining_seconds)  # 立即发射tick信号更新显示

    def start_break(self):
        """开始休息"""
        # 检查是否应该长休息
        if (
            self.completed_pomodoros > 0
            and self.completed_pomodoros % self.config.pomodoros_for_long_break == 0
        ):
            self.state = TimerState.LONG_BREAK
            self.remaining_seconds = self.config.long_break_minutes * 60
        else:
            self.state = TimerState.SHORT_BREAK
            self.remaining_seconds = self.config.short_break_minutes * 60

        self.timer.start(1000)
        self.state_changed.emit(self.state)
        self.tick.emit(self.remaining_seconds)  # 立即发射tick信号更新显示

    def pause(self):
        """暂停计时"""
        self.timer.stop()

    def resume(self):
        """恢复计时"""
        if self.state != TimerState.IDLE:
            self.timer.start(1000)

    def stop(self):
        """停止计时"""
        self.timer.stop()
        self.state = TimerState.IDLE
        self.remaining_seconds = 0
        self.state_changed.emit(self.state)

    def _on_tick(self):
        """每秒触发"""
        self.remaining_seconds -= 1

        # 先检查是否时间到，再发送tick信号
        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0  # 防止显示负数
            self._on_time_complete()
        else:
            self.tick.emit(self.remaining_seconds)

    def _on_time_complete(self):
        """时间到处理"""
        self.timer.stop()

        if self.state == TimerState.WORKING:
            # 工作完成
            self.completed_pomodoros += 1
            self.work_complete.emit()
            self.start_break()

        elif self.state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            # 休息完成
            is_long_break = self.state == TimerState.LONG_BREAK
            
            # 先设置为IDLE状态，再发射信号，防止信号处理中启动新番茄后状态被覆盖
            self.state = TimerState.IDLE
            self.state_changed.emit(self.state)
            
            self.break_complete.emit(is_long_break)
            self.pomodoro_complete.emit()
            self.cycle_complete.emit(self.completed_pomodoros)

    def get_formatted_time(self) -> str:
        """获取格式化的时间显示"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.state == TimerState.IDLE:
            return 0.0

        total_seconds = {
            TimerState.WORKING: self.config.work_time_minutes * 60,
            TimerState.SHORT_BREAK: self.config.short_break_minutes * 60,
            TimerState.LONG_BREAK: self.config.long_break_minutes * 60,
        }.get(self.state, 1)

        if total_seconds == 0:
            return 0.0

        return ((total_seconds - self.remaining_seconds) / total_seconds) * 100

    def get_state_text(self) -> str:
        """获取状态文本"""
        state_texts = {
            TimerState.IDLE: "准备开始",
            TimerState.WORKING: "工作中",
            TimerState.SHORT_BREAK: "短休息",
            TimerState.LONG_BREAK: "长休息",
        }
        return state_texts.get(self.state, "未知")
