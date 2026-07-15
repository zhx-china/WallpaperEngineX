import winreg
import os
import sys
from pathlib import Path

try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\WallpaperEngineX", 0, winreg.KEY_READ) as key:
        self_path = winreg.QueryValueEx(key, "selfPath")[0]
        os.chdir(self_path)
except Exception:
    os.chdir(str(Path(sys.executable).parent))

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import logging

# 创建处理器，将输出重定向到日志
class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

# 将 sys.stdout 重定向到 logger.info
sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)

import colors
import settings
import Run

import json

import argparse


# 配置日志记录
print("配置日志...")
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s] %(message)s',
    filename='WallpaperEngineX.log',
    filemode='a',
    encoding='utf-8'
)


print("配置命令行...")
# 创建ArgumentParser对象
parser = argparse.ArgumentParser(description='WallpaperEngineX')

parser.add_argument("-s", "--selfrun", help="启动壁纸",
                    action="store_true")
args = parser.parse_args()
if args.selfrun:
    print("正在自启动...")
    Run.Run()
    sys.exit(0)
else:
    try:
        software = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\WallpaperEngineX", reserved=0,
                                      access=winreg.KEY_WRITE)
        winreg.SetValueEx(software, "selfRun", 0, winreg.REG_DWORD, 1 if settings.selfRun else 0)
        winreg.SetValueEx(software, "selfPath", 0, winreg.REG_SZ, settings.self_path)
        winreg.CloseKey(software)
        print("✓ 注册表设置成功")
    except Exception as e:
        print(f"✗ 写入注册表失败: {e}")


class Wallpaper(QPushButton):
    def __init__(self, name):
        super().__init__()
        self.wallpaper_folder = name
        self.json_data = None
        self.display_name = ""
        self.Setting = settings.config
        self.author = ""
        self.tags = []
        self.description = ""
        self.image = QImage()
        self.context_label = QLabel()

        self.MainBox = QHBoxLayout(self)
        self.ContentBox = QVBoxLayout()

        self.init_file()
        self.init_ui()

    def init_file(self):
        wallpaper_path = settings.wallpaper_path
        json_path = os.path.join(wallpaper_path, self.wallpaper_folder, "wallpaper.json")

        print("扫描壁纸:" + json_path + "\n")
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                self.json_data = json.load(file)
        except UnicodeDecodeError:
            pass

        self.display_name = self.json_data.get("name", self.wallpaper_folder)
        self.author = self.json_data.get("author", "")
        self.tags = self.json_data.get("tags", [])
        self.description = self.json_data.get("description", "")
        self.isExe = self.json_data.get("is_exe", 0)

        if self.json_data.get("image_name"):
            image_path = os.path.join(wallpaper_path, self.wallpaper_folder, f"{self.json_data['image_name']}.png")
            self.image = QImage(image_path)

    def init_ui(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #80{colors.GetColor("con")};
                border-radius: 5px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #CC{colors.GetColor("con")};
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #{colors.GetColor("con")};
                border: none;
            }}
        """)
        self.setLayout(self.MainBox)

        if not self.image.isNull():
            pixmap = QPixmap.fromImage(self.image)
            scaled_pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(scaled_pixmap)
            self.MainBox.addWidget(image_label)

        tags_text = ' '.join([f"#{tag}" for tag in self.tags])
        text = f"{self.display_name} : from {self.author if self.author else '?'} - {tags_text}\n{self.description if self.description else '这个作者什么都没有留下'}"
        if self.isExe == 1:
            text += "\n该程序是可执行程序, 请确认来源后运行!"

        self.context_label.setText(text)

        self.ContentBox.addWidget(self.context_label)
        self.MainBox.addLayout(self.ContentBox)


class ZWallpaperEngine(QMainWindow):
    def __init__(self):
        super().__init__()
        if settings.topic == 1:
            self.setStyleSheet("""
                QLabel {
                    color:#FFFFFF;
                    font-weight: bold;
                }
                QRadioButton {
                    color:#FFFFFF;
                    font-weight: bold;
                }
                QPushButton {
                    color:#FFFFFF;
                    font-weight: bold;
                }
            """)
        self.setWindowTitle("WallpaperEngineX-UI")

        self.wallpapers = []

        # 中心部件
        self.central = QWidget()
        self.setCentralWidget(self.central)

        # 主布局
        self.MainBox = QHBoxLayout(self.central)

        # 菜单布局
        self.MenuFrame = QFrame()
        self.MenuBox = QVBoxLayout(self.MenuFrame)
        self.WallpaperMenu = QRadioButton(self.MenuFrame)
        self.SettingsMenu = QRadioButton(self.MenuFrame)
        self.MainMenu = QRadioButton(self.MenuFrame)

        # QStackedWidget
        self.MainStack = QStackedWidget()

        # 页面0：壁纸列表
        self.ContentFrame = QFrame()
        self.ContentBox = QVBoxLayout(self.ContentFrame)

        # 壁纸显示区域
        self.Wallpapers = QFrame()
        self.WallpapersBox = QVBoxLayout(self.Wallpapers)

        # 页面1：壁纸详情
        self.WallpaperFrame = QFrame()
        self.WallpaperBox = QVBoxLayout(self.WallpaperFrame)
        self.WallpaperNameLabel = QLabel()
        self.AboutWallpaper = QLabel()
        self.SetItToWallpaper = QPushButton()
        self.Quit = QPushButton()

        #页面2：主页
        self.MainFrame = QFrame()
        self.RunWallpaperButton = QPushButton()
        self.StopWallpaperButton = QPushButton()
        self.MainFrameBox = QVBoxLayout()

        # 页面3：设置
        self.SettingsFrame = QFrame()
        self.SettingsBox = QVBoxLayout(self.SettingsFrame)

        self.SelfRunBox = QHBoxLayout()
        self.SelfRunFrame = QFrame()
        self.SelfRunRadioButton = QRadioButton()

        self.FfplayBox = QHBoxLayout()
        self.FfplayFrame = QFrame()
        self.FfplayRadioButtonFf = QRadioButton()
        self.FfplayRadioButtonOp = QRadioButton()
        self.SelfRunLabel = QLabel()
        self.FfplayLabel = QLabel()
        self.SoundLabel = QLabel()
        self.SoundToggle = QPushButton()
        self.SoundFrame = QFrame()
        self.SoundBox = QHBoxLayout()

        self.VolumeLabel = QLabel()
        self.VolumeSlider = QSlider()
        self.VolumeValue = QLabel()
        self.VolumeFrame = QFrame()
        self.VolumeBox = QHBoxLayout()
 
        self.init_ui()

    def init_ui(self):
        self.central.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
        """)

        # 菜单区域
        self.MenuFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
            border: 10px solid #{colors.GetColor("con")};
            border-radius: 10px;
            margin: 10px;
        """)

        self.WallpaperMenu.setStyleSheet(f"""
            background-color: #{colors.GetColor("con")};
            border-radius: 10px
        """)
        self.WallpaperMenu.setText("壁纸")

        self.SettingsMenu.setStyleSheet(f"""
            background-color: #{colors.GetColor("con")};
            border-radius: 10px
        """)
        self.SettingsMenu.setText("设置")

        self.MainMenu.setStyleSheet(f"""
            background-color: #{colors.GetColor("con")};
            border-radius: 10px
        """)
        self.MainMenu.setText("主页")

        # 内容区域
        self.ContentFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("con")};
            border-radius: 10px;
            margin: 10px;
        """)

        self.Wallpapers.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
            border-radius: 5px;
            margin: 5px;
        """)

        self.ContentBox.addWidget(self.Wallpapers)
        self.ContentBox.setSpacing(5)
        self.ContentBox.setContentsMargins(10, 10, 10, 10)

        # 主页
        self.MainFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
            border: 10px solid #{colors.GetColor("con")};
            border-radius: 10px;
            margin: 10px;
        """)
        self.RunWallpaperButton.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A{colors.GetColor("con")};
                border: 10px solid #1A{colors.GetColor("con")};
            }}
            QPushButton:hover {{
                background-color: #66{colors.GetColor("con")};
                border: 10px solid #66{colors.GetColor("con")};
            }}
            QPushButton:pressed {{
                background-color: #E6{colors.GetColor("con")};
                border: 10px solid #E6{colors.GetColor("con")};
            }}
        """)
        self.StopWallpaperButton.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A{colors.GetColor("con")};
                border: 10px solid #1A{colors.GetColor("con")};
            }}
            QPushButton:hover {{
                background-color: #66{colors.GetColor("con")};
                border: 10px solid #66{colors.GetColor("con")};
            }}
            QPushButton:pressed {{
                background-color: #E6{colors.GetColor("con")};
                border: 10px solid #E6{colors.GetColor("con")};
            }}
        """)
        self.RunWallpaperButton.clicked.connect(Run.Run)
        self.StopWallpaperButton.clicked.connect(Run.Stop)

        self.MainFrame.setLayout(self.MainFrameBox)
        self.RunWallpaperButton.setText("启动壁纸")
        self.StopWallpaperButton.setText("强制关闭壁纸(对于ffplay启动的壁纸,关闭软件并不会关闭壁纸)")
        self.MainFrameBox.addStretch()
        self.MainFrameBox.addWidget(self.StopWallpaperButton)
        self.MainFrameBox.addWidget(self.RunWallpaperButton)

        # 设置
        self.SettingsFrame.setLayout(self.SettingsBox)
        self.SettingsFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
            border: 10px solid #{colors.GetColor("con")};
            border-radius: 10px;
            margin: 10px;
        """)
        self.SelfRunRadioButton.setText("自启动")
        self.SelfRunRadioButton.setChecked(settings.selfRun)
        self.FfplayRadioButtonOp.setText("使用opencv")
        self.FfplayRadioButtonFf.setText("使用ffplay(推荐)")
        self.FfplayRadioButtonFf.setChecked(settings.ffplay)
        self.FfplayRadioButtonOp.setChecked(not settings.ffplay)
        self.SelfRunLabel.setText("自启动选项")
        self.FfplayLabel = QLabel("视频运行方式选项")
        self.SelfRunFrame.setLayout(self.SelfRunBox)
        self.FfplayFrame.setLayout(self.FfplayBox)
        self.SettingsBox.addWidget(self.SelfRunFrame)
        self.SettingsBox.addWidget(self.FfplayFrame)

        self.SelfRunBox.addWidget(self.SelfRunLabel)
        self.SelfRunBox.addWidget(self.SelfRunRadioButton)
        self.SelfRunBox.addStretch()

        self.FfplayBox.addWidget(self.FfplayLabel)
        self.FfplayBox.addWidget(self.FfplayRadioButtonFf)
        self.FfplayBox.addWidget(self.FfplayRadioButtonOp)
        self.FfplayBox.addStretch()

        # 声音设置
        self.SoundFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
            border: 10px solid #{colors.GetColor("con")};
            border-radius: 10px;
            margin: 10px;
        """)
        self.SoundLabel.setText("声音")
        self.SoundToggle.setCheckable(True)
        self.SoundToggle.setChecked(settings.sound)
        self.SoundToggle.setFixedSize(44, 24)
        self.SoundToggle.setCursor(Qt.PointingHandCursor)
        self._set_toggle_style(self.SoundToggle, settings.sound)
        self.SoundFrame.setLayout(self.SoundBox)
        self.SoundBox.addWidget(self.SoundLabel)
        self.SoundBox.addStretch()
        self.SoundBox.addWidget(self.SoundToggle)
        self.SettingsBox.addWidget(self.SoundFrame)

        # 音量设置
        self.VolumeFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
            border: 10px solid #{colors.GetColor("con")};
            border-radius: 10px;
            margin: 10px;
        """)
        self.VolumeLabel.setText("音量")
        self.VolumeSlider.setOrientation(Qt.Horizontal)
        self.VolumeSlider.setRange(0, 100)
        self.VolumeSlider.setValue(settings.volume)
        self.VolumeSlider.setEnabled(settings.sound)
        self.VolumeSlider.setFixedHeight(20)
        self.VolumeValue.setText(str(settings.volume))
        self.VolumeValue.setFixedWidth(30)
        self.VolumeValue.setAlignment(Qt.AlignRight)
        self.VolumeFrame.setLayout(self.VolumeBox)
        self.VolumeBox.addWidget(self.VolumeLabel)
        self.VolumeBox.addWidget(self.VolumeSlider)
        self.VolumeBox.addWidget(self.VolumeValue)
        self.SettingsBox.addWidget(self.VolumeFrame)

        self.SettingsBox.addStretch()

        # 内容区域
        self.WallpaperFrame.setStyleSheet(f"""
            background-color: #{colors.GetColor("con")};
            border-radius: 5px;
            padding: 20px;
        """)

        self.WallpaperNameLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.AboutWallpaper.setWordWrap(True)
        self.AboutWallpaper.setStyleSheet("font-size: 12px; color: #666;")

        self.WallpaperBox.addWidget(self.WallpaperNameLabel)
        self.WallpaperBox.addWidget(self.AboutWallpaper)
        self.WallpaperBox.addStretch()
        self.WallpaperBox.addWidget(self.Quit)
        self.WallpaperBox.addWidget(self.SetItToWallpaper)

        # 添加菜单
        self.MenuBox.addWidget(self.MainMenu)
        self.MenuBox.addWidget(self.SettingsMenu)
        self.MenuBox.addWidget(self.WallpaperMenu)
        self.MenuBox.addStretch()
        self.WallpaperMenu.setChecked(True)

        # 添加到 QStackedWidget
        self.MainStack.addWidget(self.ContentFrame)    # index 0
        self.MainStack.addWidget(self.WallpaperFrame)  # index 1
        self.MainStack.addWidget(self.MainFrame)       # index 2
        self.MainStack.addWidget(self.SettingsFrame)   # index 3

        # 主布局
        self.MainBox.addWidget(self.MenuFrame, 1)
        self.MainBox.addWidget(self.MainStack, 5)
        self.MainBox.setSpacing(0)
        self.MainBox.setContentsMargins(10, 10, 10, 10)

        # 加载壁纸
        for wallpaper_name in os.listdir(settings.wallpaper_path):
            self.wallpapers.append(Wallpaper(wallpaper_name))

        for wallpaper in self.wallpapers:
            wallpaper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            wallpaper.setFixedHeight(100)
            self.WallpapersBox.addWidget(wallpaper)
            wallpaper.clicked.connect(
                lambda checked, name=wallpaper.wallpaper_folder: self.Wallpaper(name)
            )
        self.WallpapersBox.addStretch()

        # 返回按钮
        self.Quit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.Quit.clicked.connect(self.back_to_list)
        self.Quit.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
        """)

        # 设为壁纸按钮
        self.SetItToWallpaper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.SetItToWallpaper.setStyleSheet(f"""
            background-color: #{colors.GetColor("bac")};
        """)
        self.SetItToWallpaper.clicked.connect(self.apply_wallpaper)

        # 菜单项
        self.MainMenu.clicked.connect(lambda: self.MainStack.setCurrentIndex(2))
        self.WallpaperMenu.clicked.connect(lambda: self.MainStack.setCurrentIndex(0))
        self.SettingsMenu.clicked.connect(lambda: self.MainStack.setCurrentIndex(3))

        #设置项
        self.FfplayRadioButtonOp.clicked.connect(lambda: self.SetWallpaperLaunch(False))
        self.FfplayRadioButtonFf.clicked.connect(lambda: self.SetWallpaperLaunch(True))

        self.SelfRunRadioButton.clicked.connect(lambda: self.SetSelfRun(self.SelfRunRadioButton.isChecked()))

        self.SoundToggle.clicked.connect(self._on_sound_toggle)
        self.VolumeSlider.valueChanged.connect(self._on_volume_change)

    def _set_toggle_style(self, btn, on):
        if on:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d7d46;
                    border-radius: 12px;
                    border: none;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #555;
                    border-radius: 12px;
                    border: none;
                }
            """)

    def _on_sound_toggle(self):
        checked = self.SoundToggle.isChecked()
        self._set_toggle_style(self.SoundToggle, checked)
        self.VolumeSlider.setEnabled(checked)
        settings.SetVal("sound", checked)

    def _on_volume_change(self, value):
        self.VolumeValue.setText(str(value))
        settings.SetVal("volume", value)

    def SetWallpaperLaunch(self, isFf):
        settings.SetVal("ffplay", isFf)

    def SetSelfRun(self, Run):
        settings.SetVal("selfrun", Run)

    def Wallpaper(self, name):
        with open(settings.wallpaper_path + "\\" + name + "\\wallpaper.json", "r", encoding='utf-8') as file:
            WallpaperJson = json.load(file)
        self.WallpaperNameLabel.setText(WallpaperJson.get("name", name))
        tags_text = ' '.join([f"#{tag}" for tag in WallpaperJson.get("tags", [])])
        self.AboutWallpaper.setText(
            f"{tags_text}\nWallpaper by {WallpaperJson.get('author', '?')}\n{WallpaperJson.get('description', '')}"
        )
        self.Quit.setText("返回")
        self.SetItToWallpaper.setText("设为壁纸")

        self.WallpaperFrame.repaint()
        # 切换到详情页面
        self.MainStack.setCurrentIndex(1)
        self.current_wallpaper_name = name

    def apply_wallpaper(self):
        """应用壁纸"""
        # 读取壁纸配置判断类型
        json_path = os.path.join(settings.wallpaper_path, self.current_wallpaper_name, "wallpaper.json")
        is_exe = 0
        exe_filename = ""
        try:
            with open(json_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                is_exe = data.get("is_exe", 0)
                exe_filename = data.get("path", "")
        except Exception:
            pass

        if is_exe == 1 and exe_filename:
            # exe壁纸
            exe_full = os.path.join(settings.wallpaper_path, self.current_wallpaper_name, f"{exe_filename}.exe")
            settings.SetVal("exe_path", exe_full)
            settings.SetVal("video_path", "empty")
            print(f"设置exe壁纸: {exe_full}")
        else:
           # 视频壁纸
            video = os.path.join(settings.wallpaper_path, self.current_wallpaper_name, "wallpaper.mp4")
            settings.SetVal("video_path", video)
            settings.SetVal("exe_path", "empty")
            print(f"设置视频壁纸: {video}")

        self.back_to_list()

    def back_to_list(self):
        """返回壁纸列表"""
        self.MainStack.setCurrentIndex(0)

    def run(self):
        self.showMaximized()


if __name__ == "__main__":
    print("=" * 9 + " Start " + "=" * 9)
    app = QApplication(sys.argv)
    engine = ZWallpaperEngine()
    engine.run()
    app.exec()
    print("="*10 + " End " + "="*10)
    sys.exit(0)
