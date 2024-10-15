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
    root.title("yk db表数据----匹配内容")  # #窗口标题
    root.geometry("500x490+900+110")  # #窗口位置500后面是字母x
    root.lift()

    text = scrolledtext.ScrolledText(root, width=80, height=5)
    text.insert(tkinter.CURRENT, matchStr)
    text.pack(pady=12, fill=tkinter.BOTH, expand=True)
    highlight_word(findStr, "highlightfind", "red", text, tkinter.END)
    pass


##
def main():
    import tkinter, tkinter.messagebox as t_box

    logging.info("main start")

    dbPath: str = ""
    binPath: str = ""
    binFile = BinFile()
    dis: bool = False

    # 界面
    root = tkinter.Tk()
    root.title("yk db表数据")  # #窗口标题
    root.geometry("600x490+900+110")  # #窗口位置500后面是字母x
    root.lift()

    top = tkinter.Frame(root, width=250, height=30)
    labTabBin = tkinter.Label(root, text="-----------------------------------")
    matchStr = tkinter.Text(root, width=20, height=1)

    # 保存表kv
    add_fram = tkinter.Frame(root, width=250, height=30)
    val_src = tkinter.Text(add_fram, width=20, height=1)
    val_key = scrolledtext.ScrolledText(add_fram, width=80, height=1)
    val_text = scrolledtext.ScrolledText(add_fram, width=80, height=5)

    # 追加kv到表的最新bin文件中
    def save():
        nonlocal dis, binFile
        import os

        srcInput: str = val_key.get(1.0, tkinter.END)
        key: str = val_key.get(1.0, tkinter.END)
        val: str = val_text.get(1.0, tkinter.END)
        if "放入key串\n" == key or "放入value串\n" == val:
            return
        str_check(key)
        str_check(val)

        tab: str = os.path.dirname(os.path.dirname(os.path.abspath(binFile.fileName)))
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
            binFile.save_rows(appendFile, keyBin, valBin, src=int(srcInput))

            t_box.showinfo("sucess", "操作成功")
            print(tab, fileL[0], key, keyBin, valBin)
        finally:
            os.chdir(os.path.dirname(os.path.abspath(binFile.fileName)))
        dis = False
        val_key.delete(1.0, tkinter.END)
        val_src.delete(1.0, tkinter.END)
        val_text.delete(1.0, tkinter.END)
        add_fram.pack_forget()

    tkinter.Button(add_fram, text="追加kv到表", command=save).pack()
    val_src.pack(side="top", pady=12, anchor="w")
    val_key.pack()
    val_text.pack(pady=12)
    # width，如果你设置width=50，那么意味着ScrolledText组件的宽度大约可以容纳50个字符。这些字符是指在组件的默认字体和字号下的“0”这样的标准字符。因此，实际的像素宽度将取决于所使用的字体和屏幕的显示设置
    txtCont = scrolledtext.ScrolledText(root, width=80, height=30)

    # 选库
    def fODb():
        nonlocal dbPath
        af = askdirectory(title="选择库目录")
        dbPath = af
        print(af)

    tkinter.Button(top, text="db目录", command=fODb).pack(side="left", padx=10, pady=2)

    # 选表
    def fOTab():
        nonlocal dbPath, binPath, binFile
        # if len(dbPath) == 0:
        #     t_box.showinfo("err", "请先选择db目录")
        #     return
        selBinPath: str = askopenfilenames(title="选择表bin文件", initialdir=dbPath)
        if len(selBinPath) == 0:
            t_box.showinfo("err", "必需选择db增量bin")
            return

        # labTabBin.config(text=selBinPath)
        sp: list = list(selBinPath)
        sp.sort()
        txtCont.config()
        txtCont.delete(1.0, tkinter.END)
        for selP in sp:
            txtCont.insert(tkinter.CURRENT, f"\n===={selP}=====\n")
            termStr = binFile.open(selP).get_row()
            txtCont.insert(tkinter.CURRENT, termStr)
        highlight_word("val", "highlight", "red", txtCont, tkinter.END)
        highlight_word("key", "highlight1", "red", txtCont, tkinter.END)
        highlight_word("vsn", "highlight2", "red", txtCont, tkinter.END)
        highlight_word("row_num", "highlight3", "red", txtCont, tkinter.END)

        highlight_word("Atom", "highlight11", "blue", txtCont, tkinter.END)
        highlight_word("Binary", "highlight12", "blue", txtCont, tkinter.END)
        highlight_word("List", "highlight13", "blue", txtCont, tkinter.END)
        highlight_word("Pid", "highlight14", "blue", txtCont, tkinter.END)
        highlight_word("Port", "highlight15", "blue", txtCont, tkinter.END)
        highlight_word("Reference", "highlight16", "blue", txtCont, tkinter.END)
        highlight_word("Function", "highlight17", "blue", txtCont, tkinter.END)

    tkinter.Button(top, text="表文件", command=fOTab).pack(side="left")

    # 显示保存界面
    def disp_save():
        nonlocal dis
        if not dis:
            dis = True
            val_key.insert(1.0, "放入key串")
            val_src.insert(1.0, "放入src整数")
            val_text.insert(1.0, "放入value串")
            add_fram.pack(after=labTabBin)

    tkinter.Button(top, text="表存kv", command=disp_save).pack(side="left", padx=10)
    time_txt = tkinter.Text(top, height=1, width=47)
    time_txt.insert(1.0, "2024-11-03 20:46:00减系统当前时间的秒数差")
    time_txt.pack(pady=12)

    # 计算目标时间到当前时间的秒数差
    def time_ok1(e):
        v = time_txt.get(1.0, tkinter.END)
        time_txt.delete(1.0, tkinter.END)
        if len(v) < 19:
            return
        secondstr = diff_time(v[0:19])
        time_txt.insert(1.0, str(secondstr))

    time_txt.bind("<KeyRelease-Return>", time_ok1)
    top.pack(anchor="w")

    labTabBin.pack(side="top", anchor="w")

    # 查找
    def find():
        allStr = txtCont.get(1.0, tkinter.END)
        findStr: str = (matchStr.get(1.0, tkinter.END)).strip()
        matchStr.delete(1.0, tkinter.END)
        matchStr.insert(1.0, "输入查找字符")
        if findStr == "输入查找字符\n":
            return
        retStr: str = ""
        for i in allStr.split("\n"):
            if findStr in i:
                retStr += f"{i}\n\n"
        find_window(findStr, retStr)

    matchStr.insert(1.0, "输入查找字符")
    tkinter.Button(command=find, text="查找").pack(anchor="w")
    matchStr.pack(side="top", anchor="w", pady=10)

    # bin显示
    txtCont.insert(1.0, "选择db-->选择表-->打开增量bin文件")
    # 全屏填充
    txtCont.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

    root.mainloop()
    # tk主窗关闭后
    logging.info("main end")


# 定义一个函数来着色指定的单词
def highlight_word(word, tag, color, s: scrolledtext.ScrolledText, pos: int):
    # txtCont.tag_remove(tag, "1.0", tkinter.END)
    start_index = "1.0"
    while True:
        # 寻找单词的起始位置
        start_index = s.search(word, start_index, pos)
        if not start_index:
            break
        # 通过计算单词长度确定结束位置
        end_index = s.index(f"{start_index}+{len(word)}c")
        # 添加标记
        s.tag_add(tag, start_index, end_index)
        # 设置标记的属性来改变颜色
        s.tag_config(tag, foreground=color)
        # 移动到文本的下一个部分
        start_index = end_index
    s.tag_raise("sel")  # 使选择突出显示始终位于顶部


if __name__ == "__main__":
    main()
    logging.info("app end")
