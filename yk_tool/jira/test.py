#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-06
# decription:测试协程

import asyncio, time
from urllib.request import urlopen
from types import FunctionType
from multiprocessing import Pool


# 计时
def calc_time(fun1: FunctionType):
    def wrap(*args, **kargs):
        s1 = time.time()
        ret = fun1(*args, **kargs)
        s2 = time.time()
        print(f"{fun1.__name__},timeUse {s2-s1}")
        return ret

    return wrap


@calc_time
def get_url(url: str) -> str:
    try:
        # 同步函数不会让出线程,会阻塞.此处只有换专门的异步io函数,以具有让出线程执行的特性
        r = urlopen(url, timeout=5.0)
    except:
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
    l = await asyncio.gather(t1, t2)
    # await t1
    # await t2
    # done,pending=await asyncio.wait({test(u),test(u)},return_when=asyncio.ALL_COMPLETED)
    # print('main=',done,pending)


def thread_test():
    # 线程
    import threading

    # 多线程会被时间片切碎，两个的总用时是重叠的，不会累长
    t1 = threading.Thread(target=test, args=("http://2.2.2.2",))
    t2 = threading.Thread(target=test, args=("http://2.2.2.3",))
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


if __name__ == "__main__":
    test_main()
