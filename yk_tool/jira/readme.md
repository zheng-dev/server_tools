(chromium-browser)[https://registry.npmmirror.com/binary.html?path=chromium-browser-snapshots/Win_x64/1348689/]

chromium_downloader.py下找到
```python
chromiumExecutable = {
    'linux': DOWNLOADS_FOLDER / REVISION / 'chrome-linux' / 'chrome',
    'mac': (DOWNLOADS_FOLDER / REVISION / 'chrome-mac' / 'Chromium.app' / 'Contents' / 'MacOS' / 'Chromium'),
    'win32': DOWNLOADS_FOLDER / REVISION / windowsArchive / 'chrome.exe',
    'win64': DOWNLOADS_FOLDER / REVISION / windowsArchive / 'chrome.exe',
}
# from pyppeteer import __chromium_revision__, __pyppeteer_home__

# DOWNLOADS_FOLDER = Path(__pyppeteer_home__) / 'local-chromium'
# REVISION = os.environ.get('PYPPETEER_CHROMIUM_REVISION', __chromium_revision__)

# 打印这两个变量可以知道执行的驱动具体位置,把chromium-browser目录(zip解决后)复制过来
# print(DOWNLOADS_FOLDER)
# print(REVISION)
```