#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-19
# decription: 进度条相关
##进度
class Progress:
    currIndex = 0
    max = 0
    __rate = 0
    __sTime = 0

    def __init__(self, max1: int = None, rate=10000) -> None:
        import time

        self.__rate = rate
        self.max = max1
        self.__sTime = time.time()
        pass

    ##进度-有总量的
    def Progress(self):
        curr = round(self.currIndex / self.max * self.__rate)
        print("\r" + "#" * curr + "_" * (self.__rate - curr), end="")

    ##无总量的,每100数刷一下
    def progress_no_sum(self, rate: int = 10000):
        self.currIndex += 1
        if (self.currIndex % rate) == 0:
            f = "/" if ((self.currIndex) / rate % 2) == 0 else "\\"
            print(
                "\r\033[1;32m curr:{0}  {1}  \033[m ".format(self.currIndex, f), end=""
            )

    ##进度完成 可手动del
    def __del__(self):
        import time

        __eTime = time.time()
        # 前景：黑色30紅色31綠色32黃色33藍色34紫紅色35青藍色36白色37
        # 背景：在前景值 基础上+10
        print(
            f"\033[1;37m \n =done={self.currIndex} use {int(__eTime)-int(self.__sTime)} second"
        )
