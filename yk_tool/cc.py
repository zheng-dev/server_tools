#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2025-03-31
# decription:对比目录 且以主目录为准进行文件同步-支持忽略指定路径文件

from typing import NoReturn, NamedTuple, TypedDict
import os, time, shutil


class Cache(NamedTuple):
    checked_times: int  # 文件经历检查次数-作删除判定
    last_m_time: float  # 上次修改时间-作修改判定


class Cfg(TypedDict):
    mainDir: str  # 主目录
    dirs: list[str]  # 附目录
    ignores: list[str]  # 忽略文件列表


# 文件对比同步（从主目录 对比到 附目录）
class TongBuFile:
    def _cfg_json_load(self) -> None | NoReturn:
        """
        dict[
            mainDir:str,
            dirs:list[str],
            ignores:list[str]
        ]
        """
        import json, sys

        utf: str = "utf-8-sig"
        cfgFile: str = ".cc.cnf"
        try:
            with open(cfgFile, "r+", -1, utf) as f:
                cfg: Cfg = json.load(f)
                # 主目录
                if (
                    type(cfg["mainDir"]) is str
                    and type(cfg["dirs"]) is list
                    and type(cfg["ignores"]) is list
                ):
                    self.mainDir: str = cfg["mainDir"]
                    # 绝对路径目录列表 附目录
                    self.dirs: list[str] = cfg["dirs"]
                    # 忽略文件列表
                    self.ignores: list[str] = cfg["ignores"]
                else:
                    raise (FileNotFoundError("value_err"))
        except FileNotFoundError:
            with open(cfgFile, "w+", -1, utf) as f:
                json.dump(
                    {
                        "mainDir": "改成主目录",
                        "dirs": ["附目录1", "附目录2"],
                        "ignores": ["主目录下的相对完整文件路径"],
                    },
                    f,
                    ensure_ascii=False,
                )

                print("请去填写配置文件>" + cfgFile + "<,然后保存再重启程序")
                sys.exit()

    #
    def __init__(self):
        self._cfg_json_load()

        self.title: str = ""
        # 主目录缓存表
        self.cache: dict[str, Cache] = {}
        # 公共检查次数
        self.checkTimes: int = 0

    def check_main_dir(self):
        """检查主目录文件"""
        self.checkTimes += 1
        for i in os.listdir(self.mainDir):
            self._loop_dir_check1(os.sep, i)
        self._del_file()

    # 检查删除
    def _del_file(self):
        publicCheckTimes: int = self.checkTimes
        deleted: list[str] = []
        for k in self.cache:
            old = self.cache[k]
            if old.checked_times != publicCheckTimes:
                deleted.append(k)
                print("del", k)
                for dir in self.dirs:
                    file: str = dir + k
                    try:
                        if os.path.isfile(file):
                            os.remove(file)
                        else:
                            shutil.rmtree(file)
                    except Exception as e:
                        print("del err:" + file, e.args)
                        pass

        # 遍历后才能pop
        for k in deleted:
            self.cache.pop(k)
        pass

    # 递归目录check
    def _loop_dir_check1(self, path: str, file: str):
        file1: str = path + file
        if file1 in self.ignores:
            return

        absFile1: str = self.mainDir + file1
        try:
            isFile: bool = os.path.isfile(absFile1)
            modifyTime: float = (
                os.path.getmtime(absFile1) if isFile else os.path.getctime(absFile1)
            )
            # 是否同步,如None,文件时间晚于上次检查时间；
            old: None | Cache = self.cache.get(file1, None)
            isCopy: bool = True if old is None else old.last_m_time != modifyTime

            if isCopy:
                self._copy(file1, isFile, modifyTime)

            self.cache[file1] = Cache(self.checkTimes, modifyTime)
            # 继续子目录
            if not isFile:
                for i in os.listdir(absFile1):
                    self._loop_dir_check1(file1 + os.sep, i)
        except:
            # 文件、目录 中途被del
            pass

    # 同步
    def _copy(self, fileOrDir: str, isFile: bool, modifyTime: float):
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


def main() -> NoReturn:
    """命令行入口"""
    try:
        a = TongBuFile()
        while True:
            a.check_main_dir()
            now: str = time.strftime("%y-%m-%d %a %H:%M:%S", time.localtime())
            print(
                "\r===done====" + now,
                end="",
            )
            #
            title: str = now[0:12]
            if a.title != title:
                a.title = title
                print(f"\033]0;{title}\007")
            time.sleep(10)
    except FileNotFoundError as e:
        print(e.filename + " 文件路径错误,检查配置文件各项是否正确")
    except Exception as e:
        print(e.args, "检查配置文件各项是否正确")
    finally:
        os._exit(1)


if __name__ == "__main__":
    main()
