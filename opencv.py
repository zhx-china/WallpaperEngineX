import time
import win32gui
import win32con
from win32con import WM_CLOSE
import threading

from win32gui import SendMessage

import MoveWindowToWallpaper
import RunVideo
import settings

def main():
    # 在子线程中启动视频播放
    video_path = settings.video_path
    video = RunVideo.Video()
    video.open(video_path)

    print("启动视频播放...")
    video_thread = threading.Thread(target=video.run, daemon=True)
    video_thread.start()

    time.sleep(1)

    h_play = MoveWindowToWallpaper.main(WindowTitle="WallpaperEngineX")

    # 移除窗口边框和标题栏
    style = win32gui.GetWindowLong(h_play, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_BORDER)
    win32gui.SetWindowLong(h_play, win32con.GWL_STYLE, style)

    # 等待视频线程结束
    video_thread.join()

    # 清理
    print("清理资源...")
    if h_play:
        SendMessage(h_play, WM_CLOSE, 0, 0)


if __name__ == "__main__":
    main()