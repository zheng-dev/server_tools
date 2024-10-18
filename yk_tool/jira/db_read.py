#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-29
# decription: db增量bin的读、增

from erlang import *
from tkinter.filedialog import *
import logging, struct
from datetime import *
from tkinter import scrolledtext


if __name__ == "__main__":
    # 这里配置log必需在脚本最前面
    logging.basicConfig(
        format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
        level=logging.INFO,
        filename=".db_read.log",
        filemode="w",
    )


class BinFile:
    """开关bin文件的上下文件用"""

    def __init__(self) -> None:
        self.fileName: str = ""
        self.fileHand = None
        """文件句柄"""
        self.hash = 0  # 原串hash

    def __del__(self):
        self.do_close()
        logging.info(f"{self.fileHand} close")

    def open(self, file: str):
        if len(self.fileName) > 0 and self.fileName != file:
            self.fileHand.close()
        self.fileName = file
        self.fileHand = open(file, "rb+")
        return self

    def get_row(self) -> str:
        """取出N条数据\n已经格式化成str\n多条以换行分隔"""
        # TODO 定长文件格式为：[2字节键长+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        # TODO 变长文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+2字节血源+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        termStr = ""
        self.fileHand.seek(0)
        row_num = 0  # 行计数
        while True:
            b = self.fileHand.read(4)
            if len(b) != 4:
                break
            kl = self.fileHand.read(2)
            # (block_size,) = struct.unpack(b">I", b)
            (key_len_num,) = struct.unpack(b">H", kl)
            row_num += 1
            if key_len_num == 0:
                # 空块,加位移
                break
            k_txt = self.fileHand.read(key_len_num)
            logging.debug(f"bnum:{b},k-len:{kl},k:{k_txt}")
            key = binary_to_term(k_txt)
            (
                src,
                vsn,
            ) = struct.unpack(b">HI", self.fileHand.read(6))
            (t1,) = struct.unpack(b">Q", bytes([0, 0]) + self.fileHand.read(6))
            (val_len,) = struct.unpack(b">I", self.fileHand.read(4))

            # print(val_len, key_len_num, vsn, t1)

            bContext = self.fileHand.read(val_len)

            if len(bContext) > 0:
                try:
                    r = binary_to_term(bContext)
                    t = datetime.fromtimestamp(t1 // 1000)
                    ext_info: dict = {
                        "vsn": vsn,
                        "key": key,
                        "val": r,
                        "src": src,
                        "time": str(t) + str(t1 % 1000),
                        "row_num": row_num,
                    }
                    termStr += str(ext_info) + "\n\n"
                except:
                    logging.error(f"bin_err:{bContext}")
                    termStr += "\nbin_err"
            else:
                termStr += "\nno data"
                break

        self.hash = hash(termStr)
        return termStr

    def save_rows(self, appendFile: str, key: bytes, val: bytes, src: int = 1001):
        """追加块到文件"""
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+2字节血源+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        vsize = len(val)
        ksize = len(key)
        blockSize = 22 - 4 + vsize + ksize  # 去掉4字节块长
        # db加载用的时间最新的 2064-10-11 11:03:58
        time = struct.pack(b">Q", 2990919838000)
        r = struct.pack(b">IH", blockSize, ksize) + key
        r += struct.pack(b">HI", src, 3)
        r += time[2:]  # 8byte变6
        r += struct.pack(b">I", vsize) + val
        with open(appendFile, "rb+") as f:
            f.seek(0, 2)  # 跳到文件末尾
            f.write(r)
            f.flush()

    def do_close(self):
        if self.fileHand is not None:
            self.fileHand.close()


def str_check(str1: str):
    l = ["os.system(", "import "]
    for i in l:
        if i in str1:
            raise (Exception("txt_illegal"))


def parse(str1: str):
    # 避免os的引入
    #   File "<string>", line 1, in <module>
    #    NameError: name 'os' is not defined. Did you forget to import 'os'
    return term_to_binary(eval(str1))


def diff_time(stime: str = "2024-11-03 20:46:00") -> int:
    import time

    tFormat = "%Y-%m-%d %H:%M:%S"
    dt = time.strptime(stime, tFormat)
    utc = int(time.mktime(dt))
    nowUtc = int(time.time())
    return utc - nowUtc


## 查找窗口
def find_window(findStr: str, matchStr: str):
    import tkinter

    root = tkinter.Tk()
    root.title(f"yk db表数据-->{findStr}")  # #窗口标题
    root.geometry("500x490+900+110")  # #窗口位置500后面是字母x
    root.lift()

    text = scrolledtext.ScrolledText(root, width=80, height=5)
    text.insert(tkinter.CURRENT, matchStr)
    text.pack(pady=12, fill=tkinter.BOTH, expand=True)
    highlight_word([(findStr, "white", "royalblue")], text, tkinter.END)
    pass


##
def main():
    import tkinter, tkinter.messagebox as t_box

    logging.info("main start")

    class DbWindow(tkinter.Tk):
        def __init__(self):
            super().__init__()
            self.title("yk db表数据")  # #窗口标题
            self.geometry("600x490+900+110")  # #窗口位置500后面是字母x
            self.binPath: str = ""
            self.binFile = BinFile()
            self.dis: bool = False
            self.lift()

        def display(self):
            self.top = tkinter.Frame(self, width=250, height=30)
            self.findFram = tkinter.Frame(self, width=250, height=30)
            self.fB = tkinter.Button(self.findFram, command=self.find, text="查找")
            self.fB.pack(side="left", padx=3)
            self.matchStr = tkinter.Text(self.findFram, width=20, height=1)
            self.matchStr.insert(1.0, "输入查找字符")
            self.matchStr.pack(side="left", pady=10, padx=5, after=self.fB)

            # 保存表kv
            self.addFram = tkinter.Frame(self, width=250, height=30)
            self.valSrc = tkinter.Text(self.addFram, width=20, height=1)
            self.valKey = scrolledtext.ScrolledText(self.addFram, width=80, height=1)
            self.valText = scrolledtext.ScrolledText(self.addFram, width=80, height=5)
            tkinter.Button(self.addFram, text="追加kv到表", command=self.save).pack()
            self.valSrc.pack(side="top", pady=12, anchor="w")
            self.valKey.pack()
            self.valText.pack(pady=12)
            # 显示表bin内容
            # width，如果你设置width=50，那么意味着ScrolledText组件的宽度大约可以容纳50个字符。这些字符是指在组件的默认字体和字号下的“0”这样的标准字符。因此，实际的像素宽度将取决于所使用的字体和屏幕的显示设置
            self.txtCont = scrolledtext.ScrolledText(self, width=80, height=30)
            tkinter.Button(self.top, text="打开表文件", command=self.fOTab).pack(
                side="left"
            )
            tkinter.Button(self.top, text="表追加存kv", command=self.disp_save).pack(
                side="left", padx=10
            )
            tkinter.Button(self.top, text="计算时间", command=self.time_ok1).pack(
                side="left"
            )
            self.timeTxt = tkinter.Text(self.top, height=1, width=47)
            self.timeTxt.insert(1.0, "2024-11-03 20:46:00减系统当前时间的秒数差")
            self.timeTxt.pack(pady=12)
            self.top.pack(anchor="w", ipadx=10, padx=5)
            self.labTabBin = tkinter.Label(
                self, text="--------------------------------------"
            )
            self.labTabBin.pack(side="top", anchor="w")
            self.findFram.pack(side="top", fill="x", expand=False, padx=2)
            self.txtCont.insert(1.0, "选择表-->选择增量目录-->打开增量bin文件(可多选)")

            # 全屏填充
            self.txtCont.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
            return self

        # 保存
        def find(self):
            allStr = self.txtCont.get(1.0, tkinter.END)
            findStr: str = self.matchStr.get(1.0, tkinter.END)[:-1]  # 去掉系统加的\n
            self.matchStr.delete(1.0, tkinter.END)
            self.matchStr.insert(1.0, "输入查找字符")
            if findStr == "输入查找字符":
                return
            retStr: str = ""
            for i in allStr.split("\n"):
                if findStr in i:
                    retStr += f"{i}\n\n"
            find_window(findStr, retStr)

        # 追加kv到表的最新bin文件中
        def save(self):
            import os

            srcInput: str = self.valSrc.get(1.0, tkinter.END)
            key: str = self.valKey.get(1.0, tkinter.END)
            val: str = self.valText.get(1.0, tkinter.END)
            if "放入key串\n" == key or "放入value串\n" == val:
                return
            str_check(key)
            str_check(val)

            tab: str = os.path.dirname(
                os.path.dirname(os.path.abspath(self.binFile.fileName))
            )
            try:
                os.chdir(tab)
                dirl = os.listdir(".")
                dirl.sort()
                dirl.reverse()
                os.chdir(dirl[0])
                fileL = os.listdir(".")
                fileL.sort()
                fileL.reverse()
                appendFile: str = fileL[0]  # 在最新的文件追加

                keyBin = parse(key)
                valBin = parse(val)
                self.binFile.save_rows(appendFile, keyBin, valBin, src=int(srcInput))

                t_box.showinfo("sucess", "操作成功")
                # print(tab, fileL[0], key, keyBin, valBin)
            finally:
                os.chdir(os.path.dirname(os.path.abspath(self.binFile.fileName)))
            self.dis = False
            self.valKey.delete(1.0, tkinter.END)
            self.valSrc.delete(1.0, tkinter.END)
            self.valText.delete(1.0, tkinter.END)
            self.addFram.pack_forget()

        # 选表
        def fOTab(self):
            selBinPath: str = askopenfilenames(title="选择表bin文件", initialdir="")
            if len(selBinPath) == 0:
                t_box.showinfo("err", "必需选择db增量bin")
                return

            # labTabBin.config(text=selBinPath)
            sp: list = list(selBinPath)
            sp.sort()
            self.txtCont.config()
            self.txtCont.delete(1.0, tkinter.END)
            for selP in sp:
                self.txtCont.insert(tkinter.CURRENT, f"\n===={selP}=====\n")
                termStr = self.binFile.open(selP).get_row()
                self.txtCont.insert(tkinter.CURRENT, termStr)
            wordColor: list = [
                ("val", "red", ""),
                ("key", "red", ""),
                ("vsn", "red", ""),
                ("row_num", "red", ""),
                ("Atom", "blue", ""),
                ("Binary", "blue", ""),
                ("List", "blue", ""),
                ("Pid", "blue", ""),
                ("Port", "blue", ""),
                ("Reference", "blue", ""),
                ("Function", "blue", ""),
            ]
            highlight_word(wordColor, self.txtCont, tkinter.END)

        # 显示保存界面
        def disp_save(self):
            if not self.dis:
                self.dis = True
                self.valKey.insert(1.0, "放入key串")
                self.valSrc.insert(1.0, "放入src整数")
                self.valText.insert(1.0, "放入value串")
                self.addFram.pack(after=self.labTabBin)

        # 计算目标时间到当前时间的秒数差
        def time_ok1(self):
            v = self.timeTxt.get(1.0, tkinter.END)
            self.timeTxt.delete(1.0, tkinter.END)
            if len(v) < 19:
                return
            secondstr = diff_time(v[0:19])
            self.timeTxt.insert(1.0, str(secondstr))

    gui = DbWindow()
    gui.display().mainloop()

    # tk主窗关闭后
    logging.info("main end")


# 定义一个函数来着色指定的单词
def highlight_word(
    wordColor: list[tuple[str, str, str]], s: scrolledtext.ScrolledText, pos: int
):
    # txtCont.tag_remove(tag, "1.0", tkinter.END)
    tag: int = 0
    for word, color, gColor in wordColor:
        startIndex = "1.0"
        tag += 1
        tagS: str = int(tag)
        while True:
            startIndex = s.search(word, startIndex, pos)
            if not startIndex:
                break
            # 通过计算单词长度确定结束位置
            endIndex = s.index(f"{startIndex}+{len(word)}c")
            # 添加标记
            s.tag_add(tagS, startIndex, endIndex)
            s.tag_config(tagS, foreground=color, background=gColor)
            # 移动到文本的下一个部分
            startIndex = endIndex
    s.tag_raise("sel")  # 使选择突出显示始终位于顶部


if __name__ == "__main__":
    main()
    logging.info("app end")
