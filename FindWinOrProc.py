import psutil
import win32gui
import win32process
import os
from typing import Optional, Dict, List, Tuple


def findProcessByExe(exe: str) -> Optional[Dict]:
    exe_path = os.path.normpath(exe)

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username', 'cpu_percent', 'memory_info']):
        try:
            proc_exe = proc.info['exe']
            if proc_exe and os.path.normpath(proc_exe) == exe_path:
                return {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'exe': proc.info['exe'],
                    'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '',
                    'username': proc.info['username'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return None


def findWindowsByPid(pid: int) -> List[Tuple[int, str, str]]:
    windows = []

    def enum_windows_callback(hwnd, hwnd_list):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
            try:
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    class_name = win32gui.GetClassName(hwnd)
                    title = win32gui.GetWindowText(hwnd)
                    if title:  # 只返回有标题的窗口
                        hwnd_list.append((hwnd, class_name, title))
            except Exception:
                pass

    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows


def findWindowsByExe(exe: str) -> Dict:
    result = {
        'process': None,
        'windows': []
    }

    # 查找进程
    process = findProcessByExe(exe)
    if not process:
        return result

    result['process'] = process

    # 查找该进程的窗口
    windows = findWindowsByPid(process['pid'])
    result['windows'] = windows

    return result


def getAllWindowsInfo():
    def enum_windows_callback(hwnd, hwnd_list):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                title = win32gui.GetWindowText(hwnd)
                if title:  # 过滤掉没有标题的窗口
                    class_name = win32gui.GetClassName(hwnd)

                    # 尝试获取进程名
                    try:
                        proc = psutil.Process(pid)
                        proc_name = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = "Unknown"

                    hwnd_list.append({
                        'hwnd': hwnd,
                        'pid': pid,
                        'process_name': proc_name,
                        'class_name': class_name,
                        'title': title
                    })
            except Exception:
                pass

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)

    return windows


def find_specific_window(exe: str, title_contains: Optional[str] = None, class_name: Optional[str] = None) -> Optional[
    Tuple[int, str, str]]:
    result = findWindowsByExe(exe)

    for hwnd, cls_name, title in result['windows']:
        # 检查标题过滤
        if title_contains and title_contains.lower() not in title.lower():
            continue

        # 检查类名过滤
        if class_name and class_name != cls_name:
            continue

        return hwnd, cls_name, title

    return None


# 测试
if __name__ == "__main__":
    exe_path = r"C:\Windows\System32\notepad.exe"
    print(f"\n=== 查找 {exe_path} 的窗口 ===")
    result = findWindowsByExe(exe_path)
    if result['process']:
        print(f"进程: {result['process']['name']} (PID: {result['process']['pid']})")
        for hwnd, class_name, title in result['windows']:
            print(f"  窗口句柄: {hwnd}, 类名: {class_name}, 标题: {title}")
    else:
        print("未找到该进程")

    print("\n=== 查找包含 '记事本' 标题的 Notepad 窗口 ===")
    window = find_specific_window(
        exe=r"C:\Windows\System32\notepad.exe",
        title_contains="记事本"
    )
    if window:
        hwnd, class_name, title = window
        print(f"找到窗口: 句柄={hwnd}, 类名={class_name}, 标题={title}")
    else:
        print("未找到匹配的窗口")
