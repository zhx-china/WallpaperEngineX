import cv2
import numpy as np


class Video:
    def __init__(self):
        self.cap = None
        self.path = None
        self.running = False
        self.target_size = None

    def open(self, path):
        self.path = path

    def get_desktop_size(self):
        """获取桌面分辨率"""
        import win32api
        width = win32api.GetSystemMetrics(0)  # 屏幕宽度
        height = win32api.GetSystemMetrics(1)  # 屏幕高度
        return (width, height)

    def run(self):
        if self.cap is None and self.path is not None:
            self.cap = cv2.VideoCapture(self.path)
        else:
            return

        if not self.cap.isOpened():
            print("Error: Could not open video.")
            return

        # 获取桌面分辨率
        desktop_width, desktop_height = self.get_desktop_size()

        # 获取视频原始尺寸
        video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"视频分辨率: {video_width}x{video_height}")
        print(f"桌面分辨率: {desktop_width}x{desktop_height}")

        # 如果视频分辨率小于桌面，使用高质量缩放
        need_resize = (video_width != desktop_width or video_height != desktop_height)

        # 创建窗口
        cv2.namedWindow('WallpaperEngineX', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('WallpaperEngineX', desktop_width, desktop_height)

        # 设置窗口属性
        cv2.setWindowProperty('WallpaperEngineX', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps > 0 else 30
        self.running = True

        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # 如果需要缩放，使用高质量插值
            if need_resize:
                frame = cv2.resize(
                    frame,
                    (desktop_width, desktop_height),
                    interpolation=cv2.INTER_LANCZOS4  # 高质量缩放
                )

            cv2.imshow('WallpaperEngineX', frame)

            if cv2.waitKey(delay) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False