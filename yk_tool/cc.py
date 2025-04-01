#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2025-03-31
# decription:对比目录 且以主目录为准进行文件同步-支持忽略指定路径文件

from collections import namedtuple
from typing import NoReturn
import os, time, shutil

Cache = namedtuple(
    "Cache",
    [
        "checked_times",  # 文件经历检查次数-作删除判定
        "last_m_time",  # 上次修改时间-作修改判定
    ],
)


# 文件对比同步（从主目录 对比到 附目录）
class TongBuFile:
    def _cfg(self):
        self.mainDir: str = "F:\\sanguozhi\\server\\int\\plugin"
        # 绝对路径目录列表 附目录
        self.dirs: list[str] = [
            "F:\\sanguozhi\\server\\int2\\plugin",
            "F:\\sanguozhi\\server\\int3\\plugin",
            "F:\\sanguozhi\\server\\int4\\plugin",
        ]
        # 忽略文件列表
        self.ignores: list[str] = ["\\#\\.cfg\\port.cfg"]

    #
    def __init__(self):
        self._cfg()

        # 主目录缓存表
        self.cache: dict[str, Cache] = {}
        # 公共检查次数
        self.checkTimes: int = 0

    # 检查删除
    def del_file(self):
        publicCheckTimes: int = self.checkTimes
        deleted: list[str] = []
        for k in self.cache:
            old = self.cache[k]
            if old.checked_times != publicCheckTimes:
                deleted.append(k)
                for dir in self.dirs:
                    file: str = dir + k
                    try:
                        if os.path.isfile:
                            os.remove(file)
                        else:
                            shutil.rmtree(file)
                    except:
                        pass
                print("del", k)
        # 遍历后才能pop
        for k in deleted:
            self.cache.pop(k)
        pass

    # 检查文件修改
    def check(self):
        self.checkTimes += 1
        for i in os.listdir(self.mainDir):
            self._check1(os.sep, i)

        self.del_file()
        print("===done====", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        time.sleep(10)

    # 递归check
    def _check1(self, path: str, file: str):
        file1: str = path + file
        if file1 in self.ignores:
            return

        absFile1: str = self.mainDir + file1
        isFile: bool = os.path.isfile(absFile1)
        if isFile:
            modifyTime: float = os.path.getmtime(absFile1)
        else:
            modifyTime: float = os.path.getctime(absFile1)

        # 是否同步,如None,文件时间晚于上次检查时间；
        old: None | Cache = self.cache.get(file1, None)
        isCopy: bool = True
        if old is not None:
            isCopy: bool = old.last_m_time != modifyTime
        if isCopy:
            self.copy(file1, isFile, modifyTime)

        self.cache[file1] = Cache(self.checkTimes, modifyTime)
        # 继续子目录
        if not isFile:
            for i in os.listdir(absFile1):
                self._check1(file1 + os.sep, i)

    # 同步
    def copy(self, fileOrDir: str, isFile: bool, modifyTime: float):
        for i in self.dirs:
            if isFile:
                destModifyTime: float = 0.0
                dest: str = i + fileOrDir
                try:
                    destModifyTime = os.path.getmtime(dest)
                except:
                    pass
                if modifyTime != destModifyTime:
                    print("cp", dest)
                    shutil.copy2(self.mainDir + fileOrDir, dest)
            else:
                try:
                    os.mkdir(i + fileOrDir)
                except:
                    pass
        pass

    # 开始
    def start(self) -> NoReturn:
        while True:
            self.check()


def main() -> None:
    a = TongBuFile()
    a.start()


if __name__ == "__main__":
    main()
