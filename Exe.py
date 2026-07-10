import subprocess
import time
import os

import win32con
import win32gui
import win32process

import FindWinOrProc
import MoveWindowToWallpaper


def main(exe_full_path: str):
    """启动exe壁纸进程，找到窗口并嵌入桌面"""
    exe_name = os.path.basename(exe_full_path)

    if not os.path.isfile(exe_full_path):
        print(f"exe文件不存在: {exe_full_path}")
        return

    # 启动exe进程
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = win32con.SW_HIDE

    process = subprocess.Popen(exe_full_path, startupinfo=startupinfo)
    print(f"启动exe壁纸: {exe_full_path} (PID: {process.pid})")

    # 重试查找窗口（最长约10秒）
    for attempt in range(5):
        time.sleep(2)

        # 方法1: 通过进程名查找（有标题才返回）
        for search_name in [exe_full_path, exe_name]:
            result = FindWinOrProc.findWindowsByExe(search_name)
            if result["process"] and result["windows"]:
                for hwnd, class_name, title in result['windows']:
                    print(f"找到窗口: 句柄={hwnd}, 类名={class_name}, 标题={title}")
                    MoveWindowToWallpaper.main(WindowTitle=title, WindowClassName=class_name, hwnd=hwnd)
                return

        # 方法2: 按PID枚举所有可见窗口（不限制标题）
        windows = _enum_windows_by_pid(process.pid)
        if windows:
            for hwnd, class_name, title in windows:
                print(f"找到窗口(PID直查): 句柄={hwnd}, 类名={class_name}, 标题={repr(title)}")
                MoveWindowToWallpaper.main(hwnd=hwnd)
            return

        if attempt < 4:
            print(f"等待窗口出现... ({attempt+1}/5)")

    print(f"未找到exe的窗口: {exe_name}")


def _enum_windows_by_pid(pid: int):
    """不限制窗口标题，枚举指定PID的所有可见窗口"""
    result = []
    def callback(hwnd, _):
        if not (win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)):
            return True
        try:
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid:
                cn = win32gui.GetClassName(hwnd)
                t = win32gui.GetWindowText(hwnd)
                result.append((hwnd, cn, t))
        except Exception:
            pass
        return True
    win32gui.EnumWindows(callback, 0)
    return result
