#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-29
# decription: db增量bin的读、增

import tkinter.scrolledtext
from erlang import *
import logging, struct
from tkinter.filedialog import *


if __name__ == "__main__":
    # 这里配置log必需在脚本最前面
    logging.basicConfig(
        format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
        level=logging.DEBUG,
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
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+2字节血源+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
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

            print(val_len, key_len_num, vsn, t1)

            bContext = self.fileHand.read(val_len)

            if len(bContext) > 0:
                try:
                    r = binary_to_term(bContext)
                    ext_info: dict = {
                        "row_num": row_num,
                        "vsn": vsn,
                        "src": src,
                        "time": t1,
                        "key": key,
                        "key_bin": k_txt,
                    }
                    termStr += str(r) + "---" + str(ext_info) + "\n"
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
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+2字节血源+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        vsize = len(val)
        ksize = len(key)
        blockSize = 22 - 4 + vsize + ksize  # 去掉4字节块长
        time = struct.pack(b">Q", 0)
        r = struct.pack(b">IHH", blockSize, ksize, src) + key
        r += struct.pack(b">I", 1)
        r += time[2:]  # 8byte变6
        r += struct.pack(b">I", vsize) + val

        with open(appendFile, "rb+") as f:
            f.seek(0, 2)
            self.fileHand.write(r)
            self.fileHand.flush()

    def do_close(self):
        if self.fileHand is not None:
            self.fileHand.close()


def str_check(str1: str):
    l = ["os.system(", "import "]
    for i in l:
        if i in str1:
            raise (Exception("txt_illegal"))


##
def main():
    import tkinter, tkinter.messagebox as t_box
    from tkinter import scrolledtext

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
    labTabBin = tkinter.Label(root, text="未选择表增量bin文件")
    # 保存表kv
    add_fram = tkinter.Frame(root, width=250, height=30)
    val_key = scrolledtext.ScrolledText(add_fram, width=80, height=1)
    val_text = scrolledtext.ScrolledText(add_fram, width=80, height=5)

    # 追加kv到表的最新bin文件中
    def save():
        nonlocal dis, binFile
        import os

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

            key: str = val_key.get(1.0, tkinter.END)
            val: str = val_text.get(1.0, tkinter.END)
            keyBin = term_to_binary(eval(key))
            valBin = term_to_binary(eval(val))
            binFile.save_rows(appendFile, keyBin, valBin)

            t_box.showinfo("sucess", "操作成功")
            print(tab, fileL[0], key, keyBin, valBin)
        finally:
            os.chdir(os.path.dirname(os.path.abspath(binFile.fileName)))
        dis = False
        val_key.delete(1.0, tkinter.END)
        val_text.delete(1.0, tkinter.END)
        add_fram.pack_forget()

    tkinter.Button(add_fram, text="追加kv到表", command=save).pack()
    val_key.pack()
    val_text.pack()

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
        selBinPath: str = askopenfilename(title="选择表bin文件", initialdir=dbPath)
        if len(selBinPath) == 0:
            t_box.showinfo("err", "必需选择db增量bin")
            return

        labTabBin.config(text=selBinPath)

        termStr = binFile.open(selBinPath).get_row()
        txtCont.config()
        txtCont.delete(1.0, tkinter.END)
        txtCont.insert(1.0, termStr)

    tkinter.Button(top, text="表文件", command=fOTab).pack(side="left")

    # 显示保存界面
    def disp_save():
        nonlocal dis
        if not dis:
            dis = True
            val_key.insert(1.0, "放入key串")
            val_text.insert(1.0, "放入value串")
            add_fram.pack(after=labTabBin)

    tkinter.Button(top, text="表存kv", command=disp_save).pack(side="left", padx=10)
    top.pack(anchor="w")

    labTabBin.pack(side="top", anchor="w")

    # bin显示
    txtCont.insert(1.0, "选择db-->选择表-->打开增量bin文件")
    txtCont.pack(side=tkinter.LEFT)
    # yscrollbar = tkinter.Scrollbar(root)
    # yscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    # yscrollbar.config(command=txtCont.yview)
    # txtCont.config(yscrollcommand=yscrollbar.set)

    root.mainloop()
    # tk主窗关闭后
    logging.info("main end")


if __name__ == "__main__":
    main()
    logging.info("app end")
