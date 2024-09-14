#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-08-29
# decription:查找idea目录中erlang项目的头文件目录,加入到iml的include配置中
import os
import xml.etree.ElementTree as et

# ,shutil,sys

GAME = ".idea/modules.xml"  # 文件


class FindHrlDir:
    __iml: str = ""
    __GFindRet: list[str] = []  # 递归遍历目录时存path用

    def go(dir):
        os.chdir(dir)
        a = FindHrlDir()
        os.chdir("plugin")
        a._find_dir("", "./")
        os.chdir("../")
        a._after_find()
        del a

    def __init__(self) -> None:
        # 检查目录是否是idea项目
        if os.path.isfile(GAME):
            try:
                tree = et.parse(GAME)
                p_root = tree.getroot()
                ModL = p_root.find('component[@name="ProjectModuleManager"]/modules')
                m = ModL.find("module")
                fileStr = m.attrib["filepath"]
                fileStr1 = (fileStr.split("/"))[-1]
                print(fileStr1)
                self.__iml = fileStr1
            except:
                raise Exception(f"{GAME} xml_err")
        else:
            raise Exception("project_dir_err")

    # 查找出头目录到全局变量中
    def _find_dir(self, Prent: str, path: str) -> None:
        os.chdir(path)
        isHrlDir = False
        for f in os.listdir("."):
            if os.path.isdir(f):
                self._find_dir(Prent + path + "/", f)
            elif isHrlDir:
                continue
            else:
                if (os.path.splitext(f)[-1]) == ".hrl":
                    isHrlDir = True
                    self.__GFindRet.append("{0}{1}".format(Prent, path))
                pass
        if Prent != "":
            os.chdir("../")
        return

    # 使用全局变量的目录结果生成文件
    def _after_find(self) -> None:
        try:
            tree = et.parse(self.__iml)
            p_root = tree.getroot()
            ctt = p_root.find('component[@inherit-compiler-output="true"]/content')
            sFList = ctt.findall("sourceFolder")
            # 整理出已经有的dir
            oldDir = []
            for i in sFList:
                try:
                    if "erlang-include" == i.attrib["type"]:
                        oldDir.append(i.attrib["url"])
                except:
                    pass
            # 追加搜到的dir
            for newI in self.__GFindRet:
                pathStr = f"file://$MODULE_DIR$/plugin{newI[2:]}"
                if pathStr not in oldDir:
                    et.SubElement(
                        ctt, "sourceFolder", {"url": pathStr, "type": "erlang-include"}
                    )
            self.__GFindRet = []  # 重置结果
            et.indent(tree, "\t")  # xml换行
            tree.write(self.__iml, "UTF-8", True, None, "xml")

        except Exception as a:
            print("xml_err:{0}".format(a.args()))


class AppCfg:
    last_dir = ""

    def serialize(self):
        # 使用instance的__dict__属性来获取实例的所有属性
        return {key: value for key, value in self.__dict__.items()}

    def __get_cfg(self):
        import pathlib

        return str(pathlib.Path.home()) + "/.find_hrl_dir.cfg"

    def __init__(self) -> None:
        import json

        try:
            with open(self.__get_cfg(), "r+", -1, "utf-8-sig") as f:
                r = json.load(f)
                self.last_dir = r["last_dir"]
        except:
            self.last_dir = os.path.dirname(__file__)
        pass

    def save(self):
        import json

        data = self.serialize()
        if {} != data:
            with open(self.__get_cfg(), "w+", -1, "utf-8-sig") as f:
                json.dump(data, f)


import tkinter, tkinter.messagebox


class WFrame(tkinter.Tk):
    __me = None
    cfg: AppCfg = None
    dir: tkinter.Entry = None

    def __new__(cls, *args, **argsK):
        if cls.__me is None:
            cls.__me = object.__new__(cls)
        return cls.__me

    def __init__(self, title1):
        super().__init__()
        self.title(title1)
        self.geometry("300x90+900+110")  # 窗口位置500后面是字母x

    def display(self):
        l1 = tkinter.Label(self, text="项目路径")
        l1.pack()
        self.dir = tkinter.Entry(self, width=40)

        self.cfg = AppCfg()
        self.dir.insert(0, self.cfg.last_dir)
        self.dir.pack()
        self.dir.focus_set()

        tkinter.Button(self, text="  go  ", command=self.go_handle).pack()
        return self

    def go_handle(self):
        pathStr = self.dir.get()
        print(f"=={pathStr}")
        try:
            FindHrlDir.go(pathStr)
            self.cfg.last_dir = pathStr
            self.cfg.save()
            tkinter.messagebox.showinfo("成功", "生成完毕")
        except OSError as a:
            tkinter.messagebox.showinfo(
                "err", "文件错误信息:\n{0}\n{1}".format(a.strerror, a.filename)
            )
        except Exception as a:
            tkinter.messagebox.showinfo(
                "err", "错误信息:\n{0}-{1}".format(a.args, type(a))
            )


def main():
    a = WFrame("iml-hrl目录增加").display()
    a.mainloop()
    a.cfg.save()


if __name__ == "__main__":
    main()
    print("over")
