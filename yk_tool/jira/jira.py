#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-08-29
# decription:监听指定jira中的帐号是不是分配了新的jira

import threading, time, logging, webbrowser
import enum, asyncio
import tkinter
from tkinter import scrolledtext
from PIL import ImageGrab, ImageTk, Image

## 因为import时__init__需要用到下面的设置信息,所以要在最开始处运行
if __name__ == "__main__":
    # 这里配置log必需在脚本最前面
    logging.basicConfig(
        format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
        level=logging.INFO,
        filename="./.jira.log",
        filemode="w",
    )
    #
    import os

    os.environ.setdefault("PYPPETEER_CHROMIUM_REVISION", "1348689")  # 设置下载变量
    os.environ.setdefault(
        "PYPPETEER_DOWNLOAD_HOST", "https://registry.npmmirror.com/-/binary"
    )  # 设置下载变量


from requests import Response
from requests_html import HTMLSession

__LOG_TIMES__ = 60


##字典cfg
class AppCfg:
    def __get_dir() -> str:
        import pathlib

        return str(pathlib.Path.home())

    def cfg_json() -> dict:
        import json

        cfgFile: str = ".cfg.txt"
        try:
            with open(cfgFile, "r+", -1, "utf-8-sig") as f:
                cfg = json.load(f)
                host = cfg["host"]
                if host == "http://xx/":
                    raise (FileNotFoundError("host_err"))
                cfg["login"] = f"{host}login.jsp"
                # 登录后的必要请求
                cfg["after_login"] = [f"{host}issues/?filter=-1"]
                cfg["browse"] = f"{host}browse/"  # 浏览指定jira的信息
                # 帐号下jira列表
                cfg["list"] = (
                    f"{host}secure/views/bulkedit/BulkEdit1!default.jspa?reset=true&tempMax=30"
                )
                return cfg
        except FileNotFoundError as e:
            with open(cfgFile, "w+", -1, "utf-8-sig") as f:
                sample = {
                    "user": "xx",
                    "pwd": "xx",
                    "host": "http://xx/",
                    "interval": 1200,
                }
                json.dump(sample, f)
            logging.error(f"cfg_err,update cfg:{cfgFile}")
            raise (Exception("cfg_err"))


##状态枚举
class JiraState(enum.Enum):
    LOGIN_OK = 1
    LOGIN_WAIT = 2
    LOGIN_NEED = 3
    NET_ERROR = 4


## 检查jira
class MyJira:
    _instance_lock = threading.Lock()

    ##单例用
    def single():
        # __new__会在return后一定调用__init__运行多次
        if not hasattr(MyJira, "_instance"):
            with MyJira._instance_lock:
                if not hasattr(MyJira, "_instance"):
                    MyJira._instance = MyJira()
        return MyJira._instance

    def __init__(self) -> None:
        self.checkTimes: int = 0
        self.session2 = HTMLSession()
        # 把loop先在主线程开出来,多线程登录--不卡ui
        self.session2.browser
        self.__sessionLoop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self.cfg: dict[str, str] = AppCfg.cfg_json()
        self.oldJira: list[str] = []
        self.list_interval: int = None
        self.__isLogin = JiraState.LOGIN_NEED
        self.__head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "max-age=0",
            "upgrade-insecure-requests": "1",
        }

    ##
    def __del__(self):
        logging.info("jire __del__")
        self.session2.close()

    ##
    def login(self):
        self.__isLogin = JiraState.LOGIN_WAIT
        cfg = self.cfg
        uName: str = cfg["user"]
        self.list_interval = cfg["interval"]
        data = {"os_username": uName, "os_password": cfg["pwd"]}
        data["os_destination"] = ""
        data["user_role"] = ""
        data["atl_token"] = ""
        data["login"] = "登录"

        lhead = self.__head
        lhead["Content-Type"] = "application/x-www-form-urlencoded"

        r: Response = self.session2.post(cfg["login"], data=data, headers=lhead)
        if r.status_code != 200:
            self.__isLogin = JiraState.NET_ERROR
            logging.warning("login err2:%s==%s", r.status_code, r.text)
        elif f'<meta name="ajs-remote-user" content="{uName}">' in r.text:
            r.html.render()
            for uri1 in cfg["after_login"]:
                r: Response = self.session2.get(uri1)
                r.html.render()
                self.__isLogin = JiraState.LOGIN_OK

    ##
    def async_login(self) -> None:
        def l(a: MyJira):
            asyncio.set_event_loop(a.__sessionLoop)
            a.login()

        threading.Thread(target=l, args=(self,), name="tt").start()

    ##
    def get_list(self) -> None | list[str]:
        cfg = self.cfg
        # 没登录就先登录 如果取jira失败就再登录
        uName: str = cfg["user"]
        r = self.session2.get(cfg["list"])
        if (
            r.status_code == 200
            and f'<meta name="ajs-remote-user" content="{uName}">' in r.text
        ):
            return self._do_jira_check(r.text)
        elif r.status_code != 200:
            logging.warning("login net_err:%s==%s", r.status_code)
            self.__isLogin = JiraState.NET_ERROR
        else:
            self.__isLogin = JiraState.LOGIN_NEED
            logging.warning("login err2:%s==%s", r.status_code, r.text)

    ##Rets:(jira列表,下次update时间)
    def jira(self) -> tuple[list[str], int]:
        logging.debug("state=%s", self.__isLogin)
        if self.__isLogin == JiraState.LOGIN_NEED:
            self.async_login()
            # 确认最新状态
            return self.jira()
        elif self.__isLogin == JiraState.LOGIN_OK:
            r = self.get_list()
            logging.debug("LIST=%s", r)
            if r is not None and len(r) >= 0:
                return (r, self.list_interval)
            else:
                return (["net_error"], 5000)
        elif self.__isLogin == JiraState.LOGIN_WAIT:
            return ([], 1000)
        elif self.__isLogin == JiraState.NET_ERROR:
            self.__isLogin = JiraState.LOGIN_NEED
            return ([], 100)
        else:
            return (["net_error"], 5000)

    ##检查有没有新的
    def _do_jira_check(self, html: str) -> list[str]:
        import lxml.etree

        tree = lxml.etree.HTML(html)
        #'//td[@class="issuerow"]/p/a/@href'
        matchL: list[str] = tree.xpath('//tr[@class="issuerow"]/@data-issuekey')
        self.checkTimes += 1
        if self.checkTimes % __LOG_TIMES__ == 0:
            logging.info(f"check times={self.checkTimes}    cnt={len(matchL)}")
        newL = []
        old = self.oldJira
        for i in matchL:
            if i not in old:
                newL.append(i)

        self.oldJira = matchL  # 更新
        return newL

    ##
    def _save_html(self, html: str) -> None:
        with open("t.htm", "w+", encoding="utf-8") as f:
            f.write(html)
            webbrowser.open("t.htm")


##
def main():
    logging.info("main_win")

    class JWindow(tkinter.Tk):
        tops = "jira   ctrl+q截图"

        def __init__(self):
            super().__init__()
            #
            self.jira = MyJira.single()  # 时会创出event_loop
            self.jira.async_login()
            self.browseUrl = self.jira.cfg["browse"]

        def display(self):
            self.title(JWindow.tops)  # #窗口标题
            self.geometry("260x210+900+110")  # #窗口位置500后面是字母x
            self.attributes("-topmost", 1)
            self.resizable(False, False)

            self.l1 = scrolledtext.ScrolledText(self, height=20, width=38)
            self.l1.pack(side=tkinter.LEFT, fill="both", expand=True)
            self.after(10, self.update)

            self.l1.bind("<Control-Button-1>", self.jira_info)
            self.l1.bind("<Button-1>", self.read_flag)
            self.l1.bind("<Control-q>", self.grab)
            # 显示窗口-绑定全局快捷键
            # BindKey().hook(["alt", "q", "0"], self.deiconify)
            self.bind("<Escape>", self.hide)
            return self

        def read_flag(self, e):
            self.title(JWindow.tops)

        def update(self):
            r: tuple[list[str], int] = self.jira.jira()
            (r1, ms) = r
            if len(r1) > 0:
                tStr = time.strftime(
                    f"==%m/%d %H:%M:%S num:{len(r1)}==\n", time.localtime()
                )
                self.l1.insert(1.0, tStr + ("\n".join(r1)) + "\n")
                self.title("new jira")
                self.deiconify()
            self.after(ms, self.update)

        # 隐藏
        def hide(self, event):
            # self.withdraw() # 消失
            self.iconify()

        # 打开jira号的详情
        def jira_info(self, event):
            t = self.l1.get(tkinter.SEL_FIRST, tkinter.SEL_LAST)
            webbrowser.open(f"{self.browseUrl}{t}")

        # 截图
        def grab(self, evt):
            self.iconify()
            GWindow(self).display()

    gui = JWindow()
    gui.display().mainloop()
    # tk主窗关闭后
    logging.info("main_win exit")
    return


# ##组合键
# import keyboard


# class BindKey:
#     def __init__(self) -> None:
#         self.__keys: list[str] = []
#         self.__onKeys: list[str] = []
#         self.__call = None

#     def __on_key(self, event: keyboard.KeyboardEvent):
#         if event.name in self.__keys and event.event_type == "up":
#             self.__onKeys.remove(event.name)
#         elif (
#             event.name in self.__keys
#             and event.event_type == "down"
#             and event.name not in self.__onKeys
#         ):
#             self.__onKeys.append(event.name)
#             self.__onKeys.sort()
#             if self.__keys == self.__onKeys:
#                 self.__call()

#     def hook(self, keys: list[str], callback):
#         self.__call = callback
#         self.__keys = keys
#         self.__keys.sort()
#         keyboard.hook(self.__on_key)  # 锁屏回来也生效


class DPWindow(tkinter.Toplevel):
    def __init__(self, parent: tkinter.Toplevel):
        super().__init__(parent)

    def display(self, w: int, h: int, img1: Image):
        self.wm_attributes("-topmost", 1)
        self.overrideredirect(True)
        self.resizable(True, True)
        self.geometry(f"{w}x{h}+100+600")  # 设置窗口大小
        #
        img = ImageTk.PhotoImage(img1)
        # 将图像添加到标签小部件中
        image1 = tkinter.Label(self, image=img, border=0)
        image1.image = img
        image1.place(x=0, y=0)
        self.bind("<ButtonPress-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.bind("<Escape>", self.on_quit)
        return self

    def on_drag_start(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.winfo_x() + deltax
        new_y = self.winfo_y() + deltay
        self.geometry(f"+{new_x}+{new_y}")

    def on_drag_stop(self, _event):
        self.x = 0
        self.y = 0

    def on_quit(self, e):
        self.destroy()


class GWindow(tkinter.Toplevel):
    __ALPHA: int = 0.6

    def __init__(self, p):
        super().__init__(p)

    def display(self):
        self.geometry("400x200")  # 设置窗口大小
        self.title("取景框-->回车")
        # attributes("-fullscreen", True)
        self.wm_attributes("-alpha", GWindow.__ALPHA)
        self.wm_attributes("-topmost", 1)
        self.canvas = tkinter.Canvas(self, bg="blue")
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.Y)
        self.bind("<Return>", self.screenshot)
        self.bind("<Escape>", self.on_quit)
        return self

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

    def on_quit(self, e):
        self.destroy()


if __name__ == "__main__":
    main()
