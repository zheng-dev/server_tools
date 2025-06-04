#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-08-29
# decription:查找idea目录中erlang项目的头文件目录,加入到iml的include配置中

import os
import xml.etree.ElementTree as et
from typing import List
import tkinter as tk
from tkinter import messagebox, filedialog

GAME = ".idea/modules.xml"  # 文件


class FindHrlDir:
    __iml: str

    @staticmethod
    def go(dir_path: str) -> None:
        os.chdir(dir_path)
        a = FindHrlDir()
        plugin_dir = os.path.join(dir_path, "plugin")
        hrl_dirs = a._find_dir(plugin_dir)
        a._after_find(hrl_dirs)
        del a

    def __init__(self) -> None:
        # 检查目录是否是idea项目
        if os.path.isfile(GAME):
            try:
                tree = et.parse(GAME)
                p_root = tree.getroot()
                ModL = p_root.find('component[@name="ProjectModuleManager"]/modules')
                m = ModL.find("module") # type: ignore
                fileStr = m.attrib["filepath"] # type: ignore
                fileStr1 = (fileStr.split("/"))[-1]
                print(fileStr1)
                self.__iml = fileStr1
            except Exception as e:
                raise Exception(f"{GAME} xml_err: {e}")
        else:
            raise Exception("project_dir_err")

    # 查找出所有包含.hrl文件的目录，返回绝对路径列表
    def _find_dir(self, path: str) -> List[str]:
        hrl_dirs: List[str] = []
        for root, _, files in os.walk(path):
            if any(f.endswith(".hrl") for f in files):
                # IDEA iml中路径格式为相对plugin的路径
                rel_path = os.path.relpath(root, os.path.dirname(self.__iml))
                hrl_dirs.append(rel_path)
        return hrl_dirs

    # 使用查找到的目录结果生成iml文件
    def _after_find(self, hrl_dirs: List[str]) -> None:
        try:
            tree = et.parse(self.__iml)
            p_root = tree.getroot()
            ctt = p_root.find('component[@inherit-compiler-output="true"]/content')
            if ctt is None:
                raise Exception("iml结构异常，未找到content节点")
            sFList = ctt.findall("sourceFolder")
            # 整理出已经有的dir
            oldDir = [
                i.attrib["url"] for i in sFList if i.attrib.get("type") == "erlang-include"
            ]
            # 追加搜到的dir
            for newI in hrl_dirs:
                pathStr = f"file://$MODULE_DIR$/{newI.replace(os.sep, '/')}"
                if pathStr not in oldDir:
                    et.SubElement(
                        ctt, "sourceFolder", {"url": pathStr, "type": "erlang-include"}
                    )
            et.indent(tree, "\t")  # xml换行
            tree.write(self.__iml, "UTF-8", True, None, "xml")
        except Exception as e:
            print(f"xml_err: {e}")


class WFrame(tk.Tk):
    dir: tk.Entry

    def __init__(self, title1: str):
        super().__init__()
        self.title(title1)
        self.geometry("300x100+900+110")  # 窗口位置500后面是字母x

    def display(self) -> "WFrame":
        self.wm_attributes("-topmost", 1) # type: ignore
        l1 = tk.Label(self, text="项目路径")
        l1.pack()

        self.dir = tk.Entry(self, width=40)
        self.dir.pack(pady=5)

        self.go_ask_dir()

        r1 = tk.Frame(self)
        tk.Button(r1, text="  go  ", command=self.go_handle).pack(side="left")
        tk.Button(r1, text="选择项目", command=self.go_ask_dir).pack(
            side="left", padx=15
        )
        r1.pack()
        return self

    def go_ask_dir(self) -> None:
        ask = filedialog.askdirectory(title="选择项目目录")
        self.dir.delete(0, tk.END)
        self.dir.insert(0, ask)
        self.dir.focus_set()

    def go_handle(self) -> None:
        pathStr = self.dir.get()
        print(f"project dir==> {pathStr}")
        try:
            FindHrlDir.go(pathStr)
            messagebox.showinfo("成功", "生成完毕")  # type: ignore
            return None
        except OSError as a:
            messagebox.showinfo(  # type: ignore
                "err", f"文件错误信息:\n{a.strerror}\n{a.filename}"
            )
        except Exception as a:
            messagebox.showinfo(  # type: ignore
                "err", f"错误信息:\n{a}\n{type(a)}"
            )


def main() -> None:
    WFrame("iml-hrl目录增加").display().mainloop()


if __name__ == "__main__":
    main()
    print("over")
