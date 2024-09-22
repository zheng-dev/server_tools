#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-08-29
# decription:监听指定jira中的帐号是不是分配了新的jira
from requests import Response
from requests_html import HTMLSession
import threading, time, logging, webbrowser
import enum, asyncio


## 确认插件是否需要新装
def ensure_chromium():
    import os, pathlib
    from pyppeteer import __chromium_revision__, __pyppeteer_home__

    DOWNLOADS_FOLDER = pathlib.Path(__pyppeteer_home__) / "local-chromium"
    REVISION = os.environ.get("PYPPETEER_CHROMIUM_REVISION", __chromium_revision__)
    file: str = f"{DOWNLOADS_FOLDER}/{REVISION}"
    logging.info("chromium %s", file)
    if not os.path.exists(f"{file}/chrome-win"):
        try:
            os.makedirs(file)
        except:
            pass
        os.chdir(file)

        import urllib.request, zipfile

        zipName: str = "chrome-win.zip"
        try:
            with zipfile.ZipFile(zipName, "r") as zf:
                print("start unzip")
                zf.extractall()
        except:
            # 镜像下载地址
            chromeZip: str = (
                "https://registry.npmmirror.com/-/binary/chromium-browser-snapshots/Win_x64/1348689/chrome-win.zip"
            )
            print("start download. please wait...")
            urllib.request.urlretrieve(chromeZip, zipName)
            print("start unzip")
            with zipfile.ZipFile(zipName, "r") as zf:
                zf.extractall()
        print("chrome ok==")


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
    oldJira: list[str] = []
    __isLogin: JiraState = None
    session2 = HTMLSession()
    __sessionLoop: asyncio.AbstractEventLoop = None  # 多线程登录时不卡ui
    cfg: dict[str, str] = {}
    list_interval: int = None
    __head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "upgrade-insecure-requests": "1",
    }

    def __init__(self) -> None:
        self.__isLogin = JiraState.LOGIN_NEED
        self.cfg = AppCfg.cfg_json()

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
    def async_login(self):
        def l(a: MyJira):
            asyncio.set_event_loop(a.__sessionLoop)
            a.login()
            pass

        threading.Thread(target=l, args=(self,), name="tt").start()
        pass

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
                # 确认最新状态
                return self.jira()
        elif self.__isLogin == JiraState.LOGIN_WAIT:
            return ([], 1000)
        else:
            return (["net_error"], 5000)

    ##检查有没有新的
    def _do_jira_check(self, html: str) -> list[str]:
        import lxml.etree

        tree = lxml.etree.HTML(html)
        #'//td[@class="issuerow"]/p/a/@href'
        matchL: list[str] = tree.xpath('//tr[@class="issuerow"]/@data-issuekey')

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

    ##单例用
    def __new__(cls, *args, **kwargs):
        if not hasattr(MyJira, "_instance"):
            with MyJira._instance_lock:
                if not hasattr(MyJira, "_instance"):
                    MyJira._instance = object.__new__(cls)
                    ensure_chromium()
                    cls._instance.session2.browser  # 把loop先在主线程开出来
                    cls._instance.__sessionLoop = asyncio.get_event_loop()  # 子线程set

        return MyJira._instance

    ##
    def __del__(self):
        logging.info("jire __del__")
        self.session2.close()


##
def main_win():
    import tkinter

    logging.info("main_win")
    jira = MyJira()  # __new__时会创出event_loop
    jira.async_login()

    root = tkinter.Tk()
    root.title("jira")  # #窗口标题
    root.geometry("300x190+900+110")  # #窗口位置500后面是字母x
    root.lift()
    # root.attributes('-toppost',True)
    l1 = tkinter.Text(root, height=20, width=38)
    l1.pack(side=tkinter.LEFT)
    yscrollbar = tkinter.Scrollbar(root)
    yscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    yscrollbar.config(command=l1.yview)
    l1.config(yscrollcommand=yscrollbar.set)

    browseUrl = jira.cfg["browse"]

    def update():
        nonlocal jira, root, l1
        r: tuple[list[str], int] = jira.jira()
        (r1, ms) = r
        if len(r1) > 0:
            tStr = time.strftime(
                f"==%m/%d %H:%M:%S num:{len(r1)}==\n", time.localtime()
            )
            l1.insert(1.0, tStr + ("\n".join(r1)) + "\n")
            root.deiconify()
        root.after(ms, update)

    root.after(10, update)

    # 隐藏
    def hide(event):
        nonlocal root
        root.withdraw()

    root.bind("<Escape>", hide)

    # 打开jira号的详情
    def jira_info(event):
        nonlocal l1, browseUrl
        t = l1.get(tkinter.SEL_FIRST, tkinter.SEL_LAST)
        webbrowser.open(f"{browseUrl}{t}")

    l1.bind("<Control-Button-1>", jira_info)

    # 显示窗口-绑定全局快捷键
    BindKey().hook(["alt", "q", "0"], root.deiconify)

    root.mainloop()
    # tk主窗关闭后
    logging.info("main_win exit")
    return


##组合键
import keyboard


class BindKey:
    __keys: list[str] = []
    __onKeys: list[str] = []
    __call = None

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
        self.__call = callback
        self.__keys = keys
        self.__keys.sort()
        keyboard.hook(self.__on_key)  # 锁屏回来也生效


##
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
        level=logging.INFO,
        filename="./jira.log",
        filemode="w",
    )
    main_win()
