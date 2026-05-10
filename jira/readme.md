















chromium下载
------------
(chromium-browser)[https://registry.npmmirror.com/binary.html?path=chromium-browser-snapshots/Win_x64/1348689/]
chromium_downloader.py下找到

```python
chromiumExecutable = {
    'linux': DOWNLOADS_FOLDER / REVISION / 'chrome-linux' / 'chrome',
    'mac': (DOWNLOADS_FOLDER / REVISION / 'chrome-mac' / 'Chromium.app' / 'Contents' / 'MacOS' / 'Chromium'),
    'win32': DOWNLOADS_FOLDER / REVISION / windowsArchive / 'chrome.exe',
    'win64': DOWNLOADS_FOLDER / REVISION / windowsArchive / 'chrome.exe',
}

from pyppeteer import __chromium_revision__, __pyppeteer_home__

DOWNLOADS_FOLDER = Path(__pyppeteer_home__) / 'local-chromium'
REVISION = os.environ.get('PYPPETEER_CHROMIUM_REVISION', __chromium_revision__)

# 打印这两个变量可以知道执行的驱动具体位置,把chromium-browser目录(zip解决后)复制过来
print(DOWNLOADS_FOLDER)
print(REVISION)
```

```python

## 确认插件是否需要新装
def ensure_chromium():
    # import os, pathlib

    # from pyppeteer import __chromium_revision__, __pyppeteer_home__

    # DOWNLOADS_FOLDER = pathlib.Path(__pyppeteer_home__) / "local-chromium"

    # REVISION = os.environ.get("PYPPETEER_CHROMIUM_REVISION", __chromium_revision__)
    # file: str = f"{DOWNLOADS_FOLDER}/{REVISION}"
    # logging.info("chromium %s", file)
    # if not os.path.exists(f"{file}/chrome-win"):
    #     try:
    #         os.makedirs(file)
    #     except:
    #         pass
    #     os.chdir(file)

    #     import urllib.request, zipfile

    #     zipName: str = "chrome-win.zip"
    #     try:
    #         with zipfile.ZipFile(zipName, "r") as zf:
    #             print("start unzip")
    #             zf.extractall()
    #     except:
    #         # 镜像下载地址
    #         chromeZip: str = (
    #             "https://registry.npmmirror.com/-/binary/chromium-browser-snapshots/Win_x64/1348689/chrome-win.zip"
    #         )
    #         print("start download. please wait...")
    #         urllib.request.urlretrieve(chromeZip, zipName)
    #         print("start unzip")
    #         with zipfile.ZipFile(zipName, "r") as zf:
    #             zf.extractall()
    #     print("chrome ok==")
    pass

# self.bind("<Return>", self.screenshot)
# self.bind("<Escape>", self.on_quit)
# 截图函数
def screenshot(self, evt):
    # print(evt)
    win_x1 = self.winfo_rootx()
    win_y1 = self.winfo_rooty()  # 内容区
    # client_y = root.winfo_y()  # 总窗口区
    # client_x = root.winfo_x()
    x2 = win_x1 + self.canvas.winfo_width()
    y2 = win_y1 + self.canvas.winfo_height()
    self.wm_attributes("-alpha", 0)

    # 截图并显示
    img = ImageGrab.grab(bbox=(win_x1, win_y1, x2, y2))
    DPWindow(self).display(
        self.canvas.winfo_width(), self.canvas.winfo_height(), img
    )
    self.iconify()
    self.wm_attributes("-alpha", GWindow.__ALPHA)
# 退出tkinter
def on_quit(self, e):
    self.destroy()
    
```
```python

# ##组合键 --绑定全局快捷键
import keyboard


class BindKey:
    def __init__(self) -> None:
        self.__keys: list[str] = []
        self.__onKeys: list[str] = []
        self.__call = None

    def __on_key(self, event: keyboard.KeyboardEvent):
        if event.name in self.__keys and event.event_type == "up":
            self.__onKeys.remove(event.name)
        elif (
            event.name in self.__keys
            and event.event_type == "down"
            and event.name not in self.__onKeys
        ):
            self.__onKeys.append(event.name)
            self.__onKeys.sort()
            if self.__keys == self.__onKeys:
                self.__call()

    def hook(self, keys: list[str], callback):
        """BindKey().hook(["alt", "q", "2"], self.deiconify)<br>绑定alt+q+2"""
        self.__call = callback
        self.__keys = keys
        self.__keys.sort()
        keyboard.hook(self.__on_key)  # 锁屏回来也生效
        
```