# settings.py
from configparser import ConfigParser
import os
import sys
from pathlib import Path

config = ConfigParser()
config_file = "config.ini"

# 获取程序目录
_is_exe = not sys.executable.lower().endswith(('python.exe', 'python3.exe'))
if _is_exe:
    program_dir = Path(sys.executable).parent.absolute()
else:
    program_dir = Path(__file__).parent.absolute()

# 默认值
selfRun = False
ffplay = True
sound = False
topic = 0  # 0 Light 1 Dark
volume = 0
ffplay_path = str(program_dir / "ffmpeg" / "bin" / "ffplay.exe")
video_path = str(program_dir / "wallpaper.mp4")
exe_path = "empty"
wallpaper_path = str(program_dir / "wallpapers")
self_path = str(program_dir)

# 检查配置文件是否存在
if not os.path.exists(config_file):
    # 配置文件不存在，创建新配置
    config["settings"] = {
        "selfRun": "False",
        "ffplay": "True",
        "sound": "False",
        "topic": "0",
        "volume": "100",
        "ffplay_path": str(program_dir / "ffmpeg" / "bin" / "ffplay.exe"),
        "video_path": "empty",
        "wallpaper_path": str(program_dir / "wallpapers"),
        "self_path": str(program_dir),
        "exe_path": "empty"
    }
    # 保存配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
else:
    # 配置文件存在，读取它
    config.read(config_file, encoding='utf-8')

    # 检查是否有 settings section
    if "settings" not in config.sections():
        # 如果没有，创建默认配置
        config["settings"] = {
            "selfRun": "False",
            "ffplay": "True",
            "sound": "False",
            "topic": "0",
            "volume": "100",
            "ffplay_path": str(program_dir / "ffmpeg" / "bin" / "ffplay.exe"),
            "video_path": "empty",
            "wallpaper_path": str(program_dir / "wallpapers"),
            "self_path": str(program_dir),
            "exe_path": "empty"
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
    else:
        # 读取配置 - 转换为正确的类型
        selfRun = config.getboolean("settings", "selfRun")
        ffplay = config.getboolean("settings", "ffplay")
        sound = config.getboolean("settings", "sound")
        topic = config.getint("settings", "topic")
        volume = config.getint("settings", "volume")

        # 如果 sound 为 False，音量强制为 0
        if not sound:
            volume = 0

        exe_path = config.get("settings", "exe_path")

        ffplay_path = config.get("settings", "ffplay_path")
        video_path = config.get("settings", "video_path")
        wallpaper_path = config.get("settings", "wallpaper_path")
        self_path = config.get("settings", "self_path")


def SetVal(type, value):
    """设置配置值并保存到文件"""
    config.set("settings", type, str(value))
    # 保存到文件
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)

    global selfRun, ffplay, sound, topic, volume, ffplay_path, video_path, wallpaper_path, self_path, exe_path
    if type == "selfRun":
        selfRun = config.getboolean("settings", type)
    elif type == "ffplay":
        ffplay = config.getboolean("settings", type)
    elif type == "sound":
        sound = config.getboolean("settings", type)
        if not sound:
            volume = 0
            config.set("settings", "volume", "0")
    elif type == "topic":
        topic = config.getint("settings", type)
    elif type == "volume":
        volume = config.getint("settings", type)
    elif type == "ffplay_path":
        ffplay_path = config.get("settings", type)
    elif type == "video_path":
        video_path = config.get("settings", type)
    elif type == "wallpaper_path":
        wallpaper_path = config.get("settings", type)
    elif type == "self_path":
        self_path = config.get("settings", type)
    elif type == "exe_path":
        global exe_path
        exe_path = config.get("settings", type)


# 调试信息
if __name__ == "__main__":
    print("配置信息:")
    print(f"程序目录: {program_dir}")
    print(f"ffplay路径: {ffplay_path}")
    print(f"壁纸路径: {wallpaper_path}")
    print(f"视频路径: {video_path}")
    print(f"ffplay存在: {os.path.exists(ffplay_path)}")
