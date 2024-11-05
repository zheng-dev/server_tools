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

    def go(dir):
        os.chdir(dir)
        a = FindHrlDir()
        os.chdir("plugin")
        a._find_dir("", "./")
        os.chdir(dir)
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
                self.__iml: str = fileStr1
                self.__GFindRet: list[str] = []  # 递归遍历目录时存path用
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


import tkinter, tkinter.messagebox, tkinter.filedialog


class WFrame(tkinter.Tk):

    def __init__(self, title1):
        super().__init__()
        self.title(title1)
        self.geometry("300x100+900+110")  # 窗口位置500后面是字母x

    def display(self):
        self.wm_attributes("-topmost", 1)
        l1 = tkinter.Label(self, text="项目路径")
        l1.pack()

        self.dir = tkinter.Entry(self, width=40)
        self.dir.pack(pady=5)

        self.go_ask_dir()

        r1 = tkinter.Frame(self)
        tkinter.Button(r1, text="  go  ", command=self.go_handle).pack(side="left")
        tkinter.Button(r1, text="选择项目", command=self.go_ask_dir).pack(
            side="left", padx=15
        )
        r1.pack()
        return self

    def go_ask_dir(self):
        self.ask = tkinter.filedialog.askdirectory(title="选择项目目录")
        self.dir.delete(0, tkinter.END)
        self.dir.insert(0, self.ask)
        self.dir.focus_set()

    def go_handle(self):
        pathStr = self.dir.get()
        print(f"project dir==> {pathStr}")
        try:
            FindHrlDir.go(pathStr)
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
    WFrame("iml-hrl目录增加").display().mainloop()


if __name__ == "__main__":
    main()
    print("over")
