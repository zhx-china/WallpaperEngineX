import ctypes.wintypes
import time
import win32gui
import win32con

# Windows API 定义
user32 = ctypes.windll.user32
FindWindowEx = user32.FindWindowExW
ShowWindow = user32.ShowWindow
FindWindow = user32.FindWindowW
SetParent = user32.SetParent
SendMessageTimeoutW = user32.SendMessageTimeoutW
SendMessage = user32.SendMessageW
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

SW_HIDE = 0
SMTO_NORMAL = 0
WM_CHANGEUISTATE = 0x052c
WM_TOPMOST = win32con.HWND_TOPMOST
WM_SWP_NOMOVE = win32con.SWP_NOMOVE
WM_SWP_NOSIZE = win32con.SWP_NOSIZE

def enum_windows_proc(hwnd, lParam):
    """回调函数，用于枚举窗口查找 WorkerW 并隐藏"""
    h_def_view = FindWindowEx(hwnd, None, "SHELLDLL_DefView", None)
    if h_def_view:
        # 找到 WorkerW 并隐藏
        workerw = FindWindowEx(None, hwnd, "WorkerW", None)
        if workerw:
            ShowWindow(workerw, SW_HIDE)
        return False  # 停止枚举
    return True


def main(WindowTitle: str = "", WindowClassName: str = "", hwnd: int | None = None):
    # 找到 Progman 窗口（桌面管理器）
    h_pm = FindWindow("Progman", None)
    if not h_pm:
        print("未找到 Progman 窗口")
        return

    # 发送消息以准备嵌入
    print("发送信息至Progman...")
    SendMessageTimeoutW(h_pm, WM_CHANGEUISTATE, 0, 0, SMTO_NORMAL, 1000, None)

    print("获取窗口")
    h_window: int | None = hwnd
    if h_window is None:
        if WindowTitle:
            h_window = win32gui.FindWindow(None, WindowTitle)
        elif WindowClassName:
            h_window = win32gui.FindWindow(WindowClassName, None)
        else:
            return 0

    if not h_window:
        print("未找到!")
        return 0
    else:
        print(f"发现窗口,句柄{h_window}")

    SetParent(h_window, h_pm)
    time.sleep(2)
    win32gui.SetWindowPos(
        h_window,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )
    time.sleep(1)
    SendMessage(h_window, WM_TOPMOST, 0, 0)

    time.sleep(1)
    EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

    print("成功嵌入")

    return h_window
