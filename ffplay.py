import subprocess
import time
import win32con

import MoveWindowToWallpaper
import settings

def main():
    # 准备命令行
    cmd_line = f'"{settings.ffplay_path}" "{settings.video_path}" -window_title WallpaperEngineX -noborder -fs -loop 0'
    if not settings.sound:
        cmd_line += " -an"
    else:
        cmd_line += " -volume " + str(settings.volume)

    print("执行命令:", cmd_line)

    # 启动 ffplay 进程（隐藏控制台窗口）
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = win32con.SW_HIDE

    process = subprocess.Popen(
        cmd_line,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(1)
    MoveWindowToWallpaper.main(WindowClassName="SDL_app")


if __name__ == "__main__":
    main()


