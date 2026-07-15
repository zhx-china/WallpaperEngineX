import subprocess
import time
import logging
import win32con

import MoveWindowToWallpaper
import settings

logger = logging.getLogger('ffplay')

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

    try:
        process = subprocess.Popen(
            cmd_line,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logger.info("ffplay进程已启动, PID: %s", process.pid)
    except Exception as e:
        logger.error("启动ffplay失败: %s", e)
        return

    # 等待窗口出现并嵌入桌面
    for attempt in range(3):
        time.sleep(1)
        try:
            logger.info("尝试查找SDL_app窗口 (attempt %d/3)", attempt + 1)
            hwnd = MoveWindowToWallpaper.main(WindowClassName="SDL_app")
            if hwnd:
                logger.info("SDL_app嵌入成功, 句柄: %s", hwnd)
                return
        except Exception as e:
            logger.warning("SDL_app查找失败: %s", e)

    # 按窗口标题再试一次
    try:
        logger.info("尝试按标题查找窗口...")
        hwnd = MoveWindowToWallpaper.main(WindowTitle="WallpaperEngineX")
        if hwnd:
            logger.info("标题查找嵌入成功, 句柄: %s", hwnd)
    except Exception as e:
        logger.error("嵌入桌面最终失败: %s", e)


if __name__ == "__main__":
    main()


