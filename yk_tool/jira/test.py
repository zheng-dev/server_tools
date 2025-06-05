#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-06
# decription:测试协程

from http.client import HTTPResponse
import asyncio, time
from urllib.request import urlopen
from multiprocessing import Pool
import functools
from typing import Callable,TypeVar,Any
F=TypeVar('F', bound=Callable[..., Any])


# 计时
def calc_time(fun1: F)->F:
    @functools.wraps(fun1)
    def wrap(*args:Any, **kargs:Any)-> Any:
        s1 = time.time()
        ret = fun1(*args, **kargs)
        s2 = time.time()
        print(f"{fun1.__name__},timeUse {s2-s1}")
        return ret

    return wrap # type: ignore


@calc_time
def get_url(url: str) -> HTTPResponse | str:
    try:
        # 同步函数不会让出线程,会阻塞.此处只有换专门的异步io函数,以具有让出线程执行的特性
        r = urlopen(url, timeout=5.0)
    except Exception:
        r = "0"
    return r


async def test(i):
    print(f"{i}------b")
    r = get_url(i)
    print(f"{i}------e")
    return r


async def crtns_main():
    # coroutines
    u = "http://192.168.2.9"
    # 同步io函数在多个任务中也会把线程阻塞，所以两个任务的总用时是累长成了双倍
    t1 = asyncio.create_task(test(u))
    t2 = asyncio.create_task(test(u))
    l: tuple[HTTPResponse | str, HTTPResponse | str] = await asyncio.gather(t1, t2)
    print("crtns_main=", l)
    # await t1
    # await t2
    # done,pending=await asyncio.wait({test(u),test(u)},return_when=asyncio.ALL_COMPLETED)
    # print('main=',done,pending)


def thread_test():
    # 线程
    import threading

    # 多线程会被时间片切碎，两个的总用时是重叠的，不会累长
    def sync_test(url: str) -> None:
        asyncio.run(test(url))

    t1 = threading.Thread(target=sync_test, args=("http://2.2.2.2",))
    t2 = threading.Thread(target=sync_test, args=("http://2.2.2.3",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def f(x):
    import os

    get_url("http://2.2.2.2")
    print(os.getpid())
    return x * x


def process_test():
    # 多进程
    with Pool(5) as p:
        print(p.map(f, [60, 29, 3, 4, 5]))  # 刚好5个时间并发重叠,不会累长时间
        # print(p.map(f, [1, 2, 3, 4, 5, 6]))  # 多1个,要跑两轮,所以时间会累长


@calc_time
def test_main():
    print("test main")
    process_test()
    # asyncio.run(crtns_main())
    # thread_test()
    print("test main====")
    pass


import tkinter
from PIL import ImageGrab, ImageTk, Image


class WG(tkinter.Tk):
    def display(self):
        self.title("dddd")
        self.geometry("600x800")
        self.iconbitmap("a.ico")
        self.iconphoto(False, tkinter.PhotoImage(file="a.ico"))
        # self.wm_attributes("-alpha", 0.3)
        self.wm_attributes("-topmost", 1)
        self.ca = ca = tkinter.Canvas(self, background="red", highlightthickness=0)
        ca.pack(expand=True, fill=tkinter.BOTH)

        img1 = ImageGrab.grab()
        self.myPic = ImageTk.PhotoImage(img1)
        ca.create_image(0, 0, anchor=tkinter.NW, image=self.myPic)

        ca.bind("<ButtonPress-1>", self.on_drag_start)
        ca.bind("<B1-Motion>", self.on_drag)
        ca.bind("<ButtonRelease-1>", self.on_drag_stop)

        # image1 = tkinter.Label(self, image=myPic, border=20)
        # image1.image = myPic
        # image1.pack()

        return self

    def on_drag_start(self, evt):
        self.x = evt.x
        self.y = evt.y
        self.rect1 = self.ca.create_rectangle(
            evt.x, evt.y, evt.x, evt.y, dash=(2, 3, 5), outline="red", width=3
        )

    def on_drag(self, evt):
        self.ca.delete(self.rect1)
        self.rect1 = self.ca.create_rectangle(
            self.x, self.y, evt.x, evt.y, dash=(2, 3, 5), outline="red", width=1
        )

    def on_drag_stop(self, evt: tkinter.Event):
        print(self.x, self.y, evt.x, evt.y)
        print(type(evt))
        self.ca.delete(self.rect1)


def main():
    # WG().display().mainloop()

    from pathlib import Path

    # print(Path("a.ico").read_bytes())
    # import subprocess as sp

    # p = sp.run(
    #     ["powershell", "-Command", "ps", "|", "Format-List", "*"], stdout=sp.PIPE
    # )
    # p2 = p.stdout.split(b"\r\n")
    # print(len(p2))
    # for i in p2:
    #     print(i)

    #1 扫描主目录，处理增改、生成索引信息表
    #2 对比上次索引信息表和第1步的索引信息表做删除判定
    #3 修正上次索引信息表
    q:bool=False
    import signal
    def s(s,frame):
        nonlocal q
        q=True
        print('===wait=')

    signal.signal(signal.SIGINT,s)
    import atexit
    def clean_up():
        print('==at_exit')
        with open('a.txt','w') as f:
            f.write('atext')
    atexit.register(clean_up)    
    while True:
        if q:
            print('exit')
            return
        else:    
            print('r....')    
            time.sleep(10)
    # import shelve,time
    # s=shelve.open('.test',flag='c',writeback=True)
    # print(s)
    # t={'a':3}
    # print(t)
    # key:str=time.strftime("%Y%m%d%H%M%S",time.localtime())
    # s[key]={'int':10,'float':9.5,'s':"okk",'t':key}
    # print(key)
    # for keyCur in s:
    #     print(keyCur,s[keyCur])
    # s.close()    

    print(hash(__file__),__file__)


    # name: str = "go"
    # while name.strip() != "exit":
    #     name: str = input("input:")
    #     print(name)
    #     match name.strip():
    #         case "e":
    #             print("m_3")
    #         case "a":
    #             print("m_a")
    #         case _:
    #             print("__")

    pass


if __name__ == "__main__":
    main()
