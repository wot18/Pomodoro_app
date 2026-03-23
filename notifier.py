"""通知模块 - Windows通知和音效实现"""

import platform
import threading
import subprocess


def play_system_sound(sound_type="completion"):
    """播放系统声音（线程安全）"""

    def _play():
        try:
            import winsound

            if sound_type == "completion":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif sound_type == "alert":
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif sound_type == "reminder":
                winsound.MessageBeep(winsound.MB_ICONQUESTION)
            else:
                winsound.MessageBeep()
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()


class Notifier:
    """通知管理类"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.winotify_available = False

        if self.is_windows:
            try:
                from winotify import Notification, audio

                self.winotify_available = True
                print("winotify 库可用")
            except ImportError:
                print("winotify 库不可用，将使用系统提示音")

    def notify(self, title: str, message: str, duration: int = 5):
        """发送通知"""
        if self.is_windows:
            try:
                if self.winotify_available:
                    from winotify import Notification, audio

                    toast = Notification(
                        app_id="番茄钟",
                        title=title,
                        msg=message,
                        duration="short" if duration <= 5 else "long",
                    )
                    toast.set_audio(audio.Default, loop=False)
                    toast.show()
                else:
                    # 备选方案：使用 PowerShell 发送通知
                    self._powershell_notify(title, message)
            except Exception as e:
                print(f"通知发送失败: {e}")
                # 最后备选：只播放声音
                play_system_sound("alert")
        else:
            print(f"[{title}] {message}")

    def _powershell_notify(self, title: str, message: str):
        """使用 PowerShell 发送 Windows 通知"""
        try:
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title}</text>
                        <text id="2">{message}</text>
                    </binding>
                </visual>
            </toast>
"@
            
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("番茄钟").Show($toast)
            """
            subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, timeout=5
            )
        except Exception as e:
            print(f"PowerShell 通知失败: {e}")

    def notify_work_complete(self):
        """工作时间结束通知"""
        play_system_sound("completion")
        self.notify("工作时间结束!", "太棒了！完成一个番茄钟，休息一下吧~")

    def notify_break_complete(self):
        """休息时间结束通知"""
        play_system_sound("alert")
        self.notify("休息结束!", "休息好啦，准备开始下一个番茄钟吧！")

    def notify_pomodoro_complete(self):
        """一个完整番茄钟周期完成通知"""
        play_system_sound("completion")
        self.notify("番茄钟完成!", "恭喜！完成一个工作+休息周期，准备开始下一个吗？")

    def notify_reminder(self, idle_minutes: int):
        """提醒用户开始下一个番茄钟"""
        play_system_sound("reminder")
        self.notify(
            "还在工作吗?", f"已经过去 {idle_minutes} 分钟了，开始下一个番茄钟吧！"
        )
