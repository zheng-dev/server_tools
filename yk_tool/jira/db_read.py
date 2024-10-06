#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-29
# decription: db增量bin的读、增

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
        self.fileHand = open(file, "rb+")
        return self

    def get_row(self) -> str:
        """取出N条数据\n已经格式化成str\n多条以换行分隔"""
        # TODO 定长文件格式为：[2字节键长+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        # TODO 变长文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        termStr = ""
        self.fileHand.seek(0)
        while True:
            b = self.fileHand.read(4)
            if len(b) != 4:
                break
            kl = self.fileHand.read(2)
            (block_size,) = struct.unpack(b">I", b)
            (key_len_num,) = struct.unpack(b">H", kl)

            if key_len_num == 0:
                # 空块,加位移
                break
            k_txt = self.fileHand.read(key_len_num)
            logging.debug(f"bnum:{b},k-len:{kl},k:{k_txt}")
            print("key=", binary_to_term(k_txt))

            (vsn,) = struct.unpack(b">I", self.fileHand.read(4))
            _ = self.fileHand.read(6)

            dl: bytes = self.fileHand.read(4)
            # (val_len,) = struct.unpack(b">I", dl)
            val_len = block_size - key_len_num - 20
            print(val_len, struct.unpack(b">I", dl), dl, key_len_num, vsn)

            bContext = self.fileHand.read(val_len)

            if len(bContext) > 0:
                try:
                    r = binary_to_term(bContext)
                    termStr += str(r) + "\n"
                except:
                    logging.error(f"bin_err:{bContext}")
                    termStr += "\nbin_err"
            else:
                termStr += "\nno data"
                break
            print("end", termStr)
            break
        self.hash = hash(termStr)
        return termStr

    def save_rows(self, txt: str):
        """保存修改后的内容"""
        r = b""
        for row in txt.strip().split("\n"):
            logging.debug(row)
            # 只有eval可以创建对象
            # TODO 对row作检查
            str_check(row)
            any = eval(row)
            r1 = term_to_binary(any)
            numB = struct.pack(b">I", len(r1))
            r += numB + r1
        self.fileHand.seek(0)
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

    logging.info("main start")
    root = tkinter.Tk()
    root.title("yk db表数据")  # #窗口标题
    root.geometry("600x490+900+110")  # #窗口位置500后面是字母x
    root.lift()

    top = tkinter.Frame(root, width=250, height=30)
    labTabBin = tkinter.Label(root, text="未选择表增量bin文件")
    txtCont = tkinter.Text(root, width=80, height=30)

    dbPath: str = ""
    binPath: str = ""
    binFile = BinFile()

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
        if len(dbPath) == 0:
            t_box.showinfo("err", "请先选择db目录")
            return
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

    # 保存表数据
    def fSBin():
        nonlocal binFile, txtCont
        if binFile.fileHand is None:
            t_box.showinfo("err", "必需选择db增量bin")
            return
        try:
            txt = txtCont.get(1.0, tkinter.END)
            h = hash(txt[:-1])  # 在insert到text时被系统加了\n
            if binFile.hash != h:  # 检查有修改
                binFile.save_rows(txt)
                t_box.showinfo("ok", "保存成功")
            else:
                t_box.showinfo("err", "没有内容修改")
        except Exception as e:
            logging.error(f"save_err:{e}")
            t_box.showinfo("err", "保存失败")

    tkinter.Button(top, text="保存表bin", command=fSBin).pack(side="left", padx=10)
    top.pack(anchor="w")

    labTabBin.pack(side="top", anchor="w")
    # bin显示
    txtCont.insert(1.0, "选择db-->选择表-->打开增量bin文件")
    txtCont.pack(side=tkinter.LEFT)
    yscrollbar = tkinter.Scrollbar(root)
    yscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    yscrollbar.config(command=txtCont.yview)
    txtCont.config(yscrollcommand=yscrollbar.set)

    root.mainloop()
    # tk主窗关闭后
    logging.info("main end")


if __name__ == "__main__":
    main()
    logging.info("app end")
