"""配置文件管理"""

import json
from pathlib import Path


class Config:
    """应用配置管理类"""

    DEFAULT_CONFIG = {
        "work_time": 25,  # 工作时间（分钟）
        "short_break": 5,  # 短休息时间（分钟）
        "long_break": 20,  # 长休息时间（分钟）
        "pomodoros_before_long_break": 4,  # 完成几个番茄后进入长休息
    }

    def __init__(self):
        # 优先使用当前目录的配置文件（方便手动编辑）
        local_config = Path(__file__).parent / "pomodoro_config.json"
        if local_config.exists():
            self.config_file = local_config
            print(f"使用配置文件: {self.config_file}")
        else:
            self.config_file = Path.home() / ".pomodoro_config.json"
            print(f"使用配置文件: {self.config_file}")
        self.settings = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有键都存在
                    result = {**self.DEFAULT_CONFIG, **config}
                    print(f"加载配置: {result}")
                    return result
            except Exception as e:
                print(f"加载配置失败: {e}")
        print(f"使用默认配置: {self.DEFAULT_CONFIG}")
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self, key, default=None):
        """获取配置项"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self.settings[key] = value
        self.save_config()

    def reload(self):
        """重新加载配置"""
        self.settings = self.load_config()

    @property
    def work_time_minutes(self):
        return self.get("work_time", 25)

    @property
    def short_break_minutes(self):
        return self.get("short_break", 5)

    @property
    def long_break_minutes(self):
        return self.get("long_break", 20)

    @property
    def pomodoros_for_long_break(self):
        return self.get("pomodoros_before_long_break", 4)
