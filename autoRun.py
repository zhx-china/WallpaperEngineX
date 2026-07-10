import os
import sys
import pathlib
import winreg


def setup_autostart_registry(enable=True):
    """使用注册表设置自启动（推荐）"""

    # 获取程序信息
    program_dir = pathlib.Path(__file__).parent.absolute()
    script_path = program_dir / "main.py"

    if not script_path.exists():
        print(f"✗ 找不到 main.py: {script_path}")
        return False

    # 构建命令
    if getattr(sys, 'frozen', False):
        # 打包成 exe
        cmd = f'"{sys.executable}" --selfrun'
    else:
        # Python 脚本
        cmd = f'"{sys.executable}" "{script_path}" --selfrun'

    # 注册表路径
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE
        )

        if enable:
            winreg.SetValueEx(key, "WallpaperEngineX", 0, winreg.REG_SZ, cmd)
            print(f"✓ 已添加到注册表自启动")
            print(f"  命令: {cmd}")
        else:
            try:
                winreg.DeleteValue(key, "WallpaperEngineX")
                print("✓ 已从注册表删除自启动")
            except FileNotFoundError:
                print("启动项不存在")

        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"✗ 设置自启动失败: {e}")
        return False