"""数据管理模块"""

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any


class DataManager:
    """番茄钟数据管理类"""

    def __init__(self, data_file: Path = None):
        if data_file is None:
            # 优先使用当前目录的数据文件
            self.data_file = Path(__file__).parent / "pomodoro_data.json"
            if not self.data_file.parent.exists():
                self.data_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.data_file = data_file
        self.data = self.load_data()
        print(f"数据文件路径: {self.data_file}")

    def load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"加载数据: {data}")
                return data
            except Exception as e:
                print(f"加载数据失败: {e}")
        return {
            "history": {},
            "current_session": {
                "date": str(date.today()),
                "completed": 0,
                "total_work_time": 0,
                "total_break_time": 0,
            },
        }

    def save_data(self):
        """保存数据到文件"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"数据已保存: {self.data}")
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False

    def get_today_data(self) -> Dict[str, Any]:
        """获取今日数据"""
        today_str = str(date.today())
        if self.data["current_session"]["date"] != today_str:
            # 新的一天，保存昨日数据到历史
            yesterday_data = self.data["current_session"].copy()
            yesterday_date = self.data["current_session"]["date"]
            self.data["history"][yesterday_date] = yesterday_data
            print(f"保存昨日数据: {yesterday_date} -> {yesterday_data}")
            # 初始化今日数据
            self.data["current_session"] = {
                "date": today_str,
                "completed": 0,
                "total_work_time": 0,
                "total_break_time": 0,
            }
            self.save_data()
        return self.data["current_session"]

    def get_yesterday_completed(self) -> int:
        """获取昨天完成的番茄数"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        print(f"今天: {today}, 昨天: {yesterday_str}")
        print(f"历史记录: {self.data['history']}")
        # 查找昨天在历史记录中
        if yesterday_str in self.data["history"]:
            result = self.data["history"][yesterday_str].get("completed", 0)
            print(f"昨天完成的番茄数: {result}")
            return result
        return 0

    def complete_pomodoro(self, work_minutes: int, break_minutes: int):
        """完成一个番茄钟"""
        today_data = self.get_today_data()
        today_data["completed"] += 1
        today_data["total_work_time"] += work_minutes
        today_data["total_break_time"] += break_minutes
        self.save_data()
        return today_data["completed"]

    def add_work_time(self, minutes: int):
        """添加工作时间（分钟）"""
        today_data = self.get_today_data()
        today_data["total_work_time"] += minutes
        self.save_data()

    def add_break_time(self, minutes: int):
        """添加休息时间（分钟）"""
        today_data = self.get_today_data()
        today_data["total_break_time"] += minutes
        self.save_data()

    def get_today_completed(self) -> int:
        """获取今天完成的番茄数"""
        return self.get_today_data().get("completed", 0)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        today = self.get_today_data()
        yesterday = self.get_yesterday_completed()

        # 计算本周、本月统计
        current_date = date.today()
        week_total = 0
        month_total = 0

        for date_str, data in self.data["history"].items():
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
                if (current_date - d).days < 7:
                    week_total += data.get("completed", 0)
                if d.month == current_date.month and d.year == current_date.year:
                    month_total += data.get("completed", 0)
            except:
                pass

        return {
            "today": today.get("completed", 0),
            "yesterday": yesterday,
            "week": week_total,
            "month": month_total,
            "total_work_hours": today.get("total_work_time", 0),
            "total_break_hours": today.get("total_break_time", 0),
        }
