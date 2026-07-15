import settings
import os
import shutil
import ffplay
import opencv
import threading
import winreg
import sys
import autoRun

os.system('chcp 65001')
selfRun = False

# 安全获取注册表值
try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\WallpaperEngineX", 0, winreg.KEY_READ) as key:
        selfRun = bool(winreg.QueryValueEx(key, "selfRun")[0])
except FileNotFoundError:
    selfRun = False
except Exception as e:
    print(f"读取注册表失败: {e}")
    selfRun = False

# 获取程序路径
try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\WallpaperEngineX", 0, winreg.KEY_READ) as key:
        self_path = winreg.QueryValueEx(key, "selfPath")[0]
        os.chdir(self_path)
except Exception:
    pass

# 使用用户启动文件夹（不需要管理员权限）
startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
bat_name = "open_self.bat"
bat_path = os.path.join(startup_folder, bat_name)

print(startup_folder)

autoRun.setup_autostart_registry(selfRun)

def Run_():
    if settings.exe_path and settings.exe_path != "empty":
        import Exe
        Exe.main(settings.exe_path)
    elif settings.ffplay:
        ffplay.main()
    else:
        opencv.main()

def Run():
    thread = threading.Thread(target=Run_)
    thread.start()

def Stop():
    # 关闭exe壁纸
    if settings.exe_path and settings.exe_path != "empty":
        exe_name = os.path.basename(settings.exe_path)
        print(f"\n关闭exe壁纸: {exe_name}")
        os.system(f"taskkill /f /im {exe_name}")

    # 关闭视频播放器
    if settings.ffplay:
        print("\n关闭中...")
        os.system("taskkill /f /im ffplay.exe")
