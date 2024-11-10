#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-29
# decription: db增量bin的读、增

import logging, struct, ahocorasick
from io import FileIO
from erlang import *
from datetime import *
import tkinter, time
import tkinter.messagebox
from tkinter.filedialog import *
from tkinter.scrolledtext import ScrolledText

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
        self.fileName: str = None

    def __del__(self):
        logging.info("close")

    def open_read(self, file: str) -> str:
        self.fileName: str = file  # 表追加kv时要用此找目录
        with open(file, "rb") as f:
            return self.get_row(f)
        return ""

    def get_row(self, fileHand: FileIO) -> str:
        """取出N条数据\n已经格式化成str\n多条以换行分隔"""
        # TODO 定长文件格式为：[2字节键长+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        # TODO 变长文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+2字节血源+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        termStr = ""
        fileHand.seek(0)
        row_num = 0  # 行计数
        while True:
            b = fileHand.read(4)
            if len(b) != 4:
                break
            kl = fileHand.read(2)
            # (block_size,) = struct.unpack(b">I", b)
            (key_len_num,) = struct.unpack(b">H", kl)
            row_num += 1
            if key_len_num == 0:
                # 空块,加位移
                continue
            k_txt = fileHand.read(key_len_num)
            logging.debug(f"bnum:{b},k-len:{kl},k:{k_txt}")
            key = binary_to_term(k_txt)
            (
                src,
                vsn,
            ) = struct.unpack(b">HI", fileHand.read(6))
            (t1,) = struct.unpack(b">Q", bytes([0, 0]) + fileHand.read(6))
            (val_len,) = struct.unpack(b">I", fileHand.read(4))

            # print(val_len, key_len_num, vsn, t1)

            bContext = fileHand.read(val_len)
            try:
                if len(bContext) > 0:
                    r = binary_to_term(bContext)
                else:
                    r = None  # 此key已经del
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

        self.hash = hash(termStr)
        return termStr

    def get_max_id_file(self) -> str:
        if self.fileName is None:
            raise (Exception("must_select_tab"))
        import os

        tab: str = os.path.dirname(os.path.dirname(os.path.abspath(self.fileName)))
        # os.chdir(tab)
        dirl = os.listdir(tab)
        dirl.sort()
        dirl.reverse()
        maxDir: str = f"{tab}{os.sep}{dirl[0]}"
        fileL = os.listdir(maxDir)
        fileL.sort()
        fileL.reverse()
        appendFile: str = f"{maxDir}{os.sep}{fileL[0]}"  # 在最新的文件追加
        return appendFile

    def save_rows(self, key: bytes, val: bytes, src: int = 1001):
        """追加块到文件"""
        appendFile: str = self.get_max_id_file()
        # steam文件格式为：[4字节块长+2字节键长（0表示空块）+键数据+2字节血源+4字节版本（0表示已删除）+6字节时间+4字节数据长度+数据]
        vsize = len(val)
        ksize = len(key)
        blockSize = 22 - 4 + vsize + ksize  # 去掉4字节块长
        # db加载用的时间最新的
        time = struct.pack(b">Q", now_second() * 1000)
        r = struct.pack(b">IH", blockSize, ksize) + key
        r += struct.pack(b">HI", src, 3)
        r += time[2:]  # 8byte变6
        r += struct.pack(b">I", vsize) + val

        with open(appendFile, "rb+") as f:
            f.seek(0, 2)  # 跳到文件末尾
            f.write(r)
            f.flush()

    def start_time_server(self, gPath: str, timeStr: str) -> str:
        import os, sys

        try:
            files = os.listdir(gPath)
            if "db" not in files or "boot" not in files:
                return "游戏目录错误"
        except:
            return "找不到目录"
        defference = 0
        try:
            tFormat = "%Y-%m-%d %H:%M:%S"
            dt = time.strptime(timeStr, tFormat)
            utc = int(time.mktime(dt))
            defference = utc - int(time.time())
        except:
            return f"time_err:{time}"

        s = os.sep
        # 改表
        try:
            # 已知规则取巧拼接目录
            self.fileName = f"{gPath}{s}db{s}util{s}difference_time{s}00000{s}00000"
            keyBin = parse("0")  # 固定
            valBin = parse(str(defference))
            self.save_rows(keyBin, valBin, src=0)
        except Exception as a:
            return f"改表时间失败-{a.args}"
        # 启服
        if sys.platform.startswith("win"):
            # os.chdir(f"{gPath}{s}boot")
            os.system(f"cd /d {gPath}{s}boot{s} && start start.bat")
            return "操作成功"
        else:
            return "时间修改成功-非window系统,需手动启动"


def now_second() -> int:
    return int(time.time())


def str_check(str1: str):
    l = ["os.system(", "import ", "quit", "exit", "halt"]
    for i in l:
        if i in str1:
            raise (Exception("txt_illegal"))


def parse(str1: str):
    # 避免os的引入
    #   File "<string>", line 1, in <module>
    #    NameError: name 'os' is not defined. Did you forget to import 'os'
    return term_to_binary(eval(str1))


# 点击时选中内容方便覆盖
def on_select(e, Ele: tkinter.Entry):
    l = len(Ele.get())
    Ele.select_from(0)
    Ele.select_to(l)


# 定义一个函数来着色指定的单词
def highlight_word(wordColor: list[tuple[str, str, str]], s: ScrolledText):
    A = ahocorasick.Automaton()

    for idx, (word, color, gColor) in enumerate(wordColor):
        A.add_word(word, (idx, word, color, gColor))
    A.make_automaton()

    # 清理所有之前的标记
    s.tag_remove("highlight", "1.0", "end")

    # 配置新的标记样式
    for idx, (_, color, gColor) in enumerate(wordColor):
        tagS = f"highlight_{idx}"
        s.tag_config(tagS, foreground=color, background=gColor)

    # 在文本中查找所有的词并标记
    text = s.get("1.0", "end-1c")
    for end_index, (idx, word, color, gColor) in A.iter(text):
        start_index = end_index - len(word) + 1
        start_index_tk = f"1.0 + {start_index} chars"
        end_index_tk = f"1.0 + {end_index + 1} chars"
        tagS = f"highlight_{idx}"
        s.tag_add(tagS, start_index_tk, end_index_tk)

    s.tag_raise("sel")  # 使选择突出显示始终位于顶部


## 查找窗口
def find_window(parent, findStr: str, matchStr: str):
    root = tkinter.Toplevel(parent)
    root.title(f"yk db表数据-->{findStr}")  # #窗口标题
    root.geometry("1000x490")  # #窗口位置500后面是字母x
    # root.iconbitmap("a.ico")
    root.iconphoto(True, tkinter.PhotoImage(None, data=PNG))
    root.lift()

    text = ScrolledText(root, width=80, height=5)
    text.insert(tkinter.CURRENT, matchStr)
    text.pack(pady=12, fill=tkinter.BOTH, expand=True)
    highlight_word([(findStr, "white", "royalblue")], text)
    pass


## 时间工具
class TimeToolWindow(tkinter.Tk):
    GAME = "game>"
    cmdHelp = f"可输入如下cmd运行:\n    按指定时间启服: {GAME}D:\\zzc\\game_alpha>2024-11-03 20:46:00\n    执行4则运算: 6+6"

    def display(self):
        self.logNum: int = 0
        self.title("yk工具")
        self.geometry("600x400+500+110")
        # self.iconbitmap("a.ico")
        self.iconphoto(True, tkinter.PhotoImage(None, data=PNG))

        row1 = tkinter.Frame(self, height=3)
        self.timeTxt = tkinter.Text(row1, height=1, width=20)
        self.timeTxt.insert(1.0, "2024-11-03 20:46:00")
        self.timeTxt.pack(side="left")
        tkinter.Button(row1, text="转utc", command=self.to_utc).pack(
            side="left", anchor="w", padx=5
        )
        tkinter.Button(row1, text="当前utc", command=self.now_utc).pack(
            side="left", anchor="w", padx=5
        )
        tkinter.Button(row1, text="db工具", command=self.db_tool).pack(
            side="left", ipadx=10
        )
        row1.pack(fill=tkinter.BOTH, padx=5)

        row2 = tkinter.Frame(self, height=3)
        self.timeUtc = tkinter.Entry(row2, width=20)
        self.timeUtc.insert(tkinter.END, f"{time.time()}")
        self.timeUtc.bind("<FocusIn>", lambda e: on_select(e, self.timeUtc))
        self.timeUtc.pack(side="left")
        tkinter.Button(row2, text="转本地时间", command=self.to_local).pack(
            side="left", anchor="w", padx=5
        )
        row2.pack(fill=tkinter.BOTH, padx=5, pady=5)

        row3 = tkinter.Frame(self, height=3)
        self.cmdTxt = tkinter.Entry(row3, width=60)
        self.cmdTxt.insert(tkinter.END, "help")
        self.cmdTxt.bind("<FocusIn>", lambda e: on_select(e, self.cmdTxt))
        self.cmdTxt.pack(side="left")
        tkinter.Button(row3, text="执行cmd", command=self.cmd2).pack(
            side="left", anchor="w", padx=5
        )
        row3.pack(fill=tkinter.BOTH, padx=5)

        self.log = ScrolledText(self)
        self.log.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        # self.protocol("WM_DELETE_WINDOW", self.quit_any)  # 窗口点右叉时
        return self

    def cmd2(self):
        cmdStr: str = self.cmdTxt.get().strip()
        self.logNum += 1
        if cmdStr == "help":
            rets = self.cmdHelp + "\n"
        elif cmdStr.startswith(self.GAME):
            rets = f"start>{self.time_start_game(cmdStr)}\n"
        else:
            try:
                str_check(cmdStr)
                rets: str = f"{eval(cmdStr)}\n"
            except Exception as a:
                rets: str = f"err:{a.args}"
        rets: str = f"{self.logNum}>> cmd_ret --> {rets}\n"
        self.log.insert("0.0", rets)

    def time_start_game(self, cmdStr: str) -> str:
        r = cmdStr.split(">")
        if len(r) != 3:
            return "格式错误"
        else:
            [_c, gPath, timeStr] = r
            return BinFile().start_time_server(gPath, timeStr)

    def to_utc(self):
        self.logNum += 1
        stime: str = self.timeTxt.get(1.0, tkinter.END).strip()

        tFormat = "%Y-%m-%d %H:%M:%S"
        dt = time.strptime(stime, tFormat)
        utc = int(time.mktime(dt))
        rets: str = f"{self.logNum}>> {stime} --> {utc}\n\n"
        self.log.insert("0.0", rets)

    def now_utc(self):
        self.logNum += 1
        rets: str = f"{self.logNum}>> now --> {time.time()}\n\n"
        self.log.insert("0.0", rets)

    def to_local(self):
        self.logNum += 1
        stime: str = self.timeUtc.get().strip()
        t = int(float(stime))
        utc = datetime.fromtimestamp(t)  # int(time.mktime(dt))
        rets: str = f"{self.logNum}>> {stime} --> {utc}\n\n"
        self.log.insert("0.0", rets)

    # 打开表工具
    def db_tool(self):
        DbWindow(self).display().fOTab()


class DbWindow(tkinter.Toplevel):
    size: int = 1024
    lineNum: int = 2000

    def __init__(self, parent: tkinter.Tk):
        super().__init__(parent)
        self.title("yk db表数据")  # #窗口标题
        self.geometry("1200x490")  # #窗口位置500后面是字母x
        # self.iconbitmap("a.ico")
        self.iconphoto(True, tkinter.PhotoImage(None, data=PNG))
        self.binPath: str = ""
        self.binFile = BinFile()
        self.dis: bool = False
        self.lift()

    def display(self):
        self.top = tkinter.Frame(self, width=250, height=30)
        self.findFram = tkinter.Frame(self, width=250, height=30)
        self.fB = tkinter.Button(self.findFram, command=self.find, text="查找")
        self.fB.pack(side="left", padx=3)
        self.matchStr = tkinter.Entry(self.findFram, width=20)
        self.matchStr.insert(tkinter.END, "输入查找字符")
        self.matchStr.bind("<FocusIn>", lambda e: on_select(e, self.matchStr))
        self.matchStr.pack(side="left", pady=10, padx=5, after=self.fB)

        # 保存表kv
        self.addFram = tkinter.Frame(self, width=250, height=30)
        self.valSrc = tkinter.Text(self.addFram, width=20, height=1)
        self.valKey = ScrolledText(self.addFram, width=80, height=1)
        self.valText = ScrolledText(self.addFram, width=80, height=5)
        tkinter.Button(self.addFram, text="追加kv到表", command=self.save).pack()
        self.valSrc.pack(side="top", pady=12, anchor="w")
        self.valKey.pack()
        self.valText.pack(pady=12)
        # 显示表bin内容
        # width，如果你设置width=50，那么意味着ScrolledText组件的宽度大约可以容纳50个字符。这些字符是指在组件的默认字体和字号下的“0”这样的标准字符。因此，实际的像素宽度将取决于所使用的字体和屏幕的显示设置
        self.txtCont = ScrolledText(self, wrap="none")
        hscroll = tkinter.Scrollbar(
            self, orient=tkinter.HORIZONTAL, command=self.txtCont.xview
        )

        self.txtCont.configure(xscrollcommand=hscroll.set)
        hscroll.pack(side="bottom", fill=tkinter.X)
        tkinter.Button(self.top, text="打开表文件", command=self.fOTab).pack(
            side="left"
        )
        tkinter.Button(self.top, text="表追加存kv", command=self.disp_save).pack(
            side="left", padx=10
        )

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

    # 查找
    def find(self):
        allStr = self.txtCont.get(1.0, tkinter.END)
        findStr: str = self.matchStr.get()
        if findStr == "输入查找字符":
            return
        retStr: str = ""
        for i in allStr.split("\n"):
            if findStr in i:
                retStr += f"{i}\n\n"
        find_window(self, findStr, retStr)

    # 追加kv到表的最新bin文件中
    def save(self):
        srcInput: str = self.valSrc.get(1.0, tkinter.END)
        key: str = self.valKey.get(1.0, tkinter.END)
        val: str = self.valText.get(1.0, tkinter.END)
        if "放入key串\n" == key or "放入value串\n" == val:
            return
        try:
            str_check(key)
            str_check(val)
            keyBin = parse(key)
            valBin = parse(val)
            self.binFile.save_rows(keyBin, valBin, src=int(srcInput))
        except Exception as a:
            tkinter.messagebox.showinfo("err", f"错误:{a.args}")
            pass

        self.dis = False
        self.valKey.delete(1.0, tkinter.END)
        self.valSrc.delete(1.0, tkinter.END)
        self.valText.delete(1.0, tkinter.END)
        self.addFram.pack_forget()

    # 选表
    def fOTab(self):
        selBinPath: str = askopenfilenames(
            parent=self, title="选择表bin文件(可多选)", initialdir=""
        )
        if len(selBinPath) == 0:
            tkinter.messagebox.showinfo("err", "必需选择db增量bin")
            return

        # labTabBin.config(text=selBinPath)
        sp: list = list(selBinPath)
        sp.sort()
        self.txtCont.config()
        self.txtCont.delete(1.0, tkinter.END)
        accStr: str = ""
        logging.info(f"read start1")
        for selP in sp:
            # self.txtCont.insert(tkinter.CURRENT, f"\n===={selP}=====\n")
            accStr += f"\n===={selP}=====\n" + self.binFile.open_read(selP)

        # 单行大数据会卡--ScrolledText性能现状
        lineNum: int = accStr.count("\n")
        logging.info(f"read start2a  num={lineNum}")
        import os

        tab = os.path.basename(os.path.dirname(os.path.dirname(sp[0])))
        self.title(f"yk db表数据-->{tab}")
        if len(accStr) // lineNum > DbWindow.size or lineNum > DbWindow.lineNum:
            with open(f".{tab}.json", "w") as f:
                f.write(accStr)
                f.flush()
            logging.info(f"read start2a1=")
            rFile = f"{os.getcwd()}{os.sep}.{tab}.json"
            os.startfile(rFile)
            logging.info(f"read start2a2=")
            self.txtCont.insert(
                tkinter.CURRENT,
                f"单条有大数据 或 总条数太多:{lineNum}，请打开\n{rFile}.json\n查看",
            )
        else:
            self.txtCont.insert(tkinter.CURRENT, accStr)
            wordColor: list = [
                ("val", "red", ""),
                ("key", "red", ""),
                ("vsn", "red", ""),
                ("row_num", "red", ""),
                ("Atom", "blue", ""),
                ("Binary", "blue", ""),
                # ("List", "blue", ""),
                # ("Pid", "blue", ""),
                # ("Port", "blue", ""),
                # ("Reference", "blue", ""),
                # ("Function", "blue", ""),
            ]
            highlight_word(wordColor, self.txtCont)
        logging.info(f"read start2")

    # 显示保存界面
    def disp_save(self):
        if not self.dis:
            self.dis = True
            self.valKey.insert(1.0, "放入key串")
            self.valSrc.insert(1.0, "放入src整数")
            self.valText.insert(1.0, "放入value串")
            self.addFram.pack(after=self.labTabBin)


##
def main():
    logging.info("main start1")
    # rec_check()
    TimeToolWindow().display().mainloop()
    # tk主窗关闭后
    logging.info("main end")


def rec_check():
    from pathlib import Path
    import hashlib

    md5: str = hashlib.md5(Path("a.ico").read_bytes()).hexdigest()
    # print(Path("a.png").read_bytes())
    if md5 != "a4dfc53fac3366b23277e599fdac2a95":
        logging.error("file error")
        raise (Exception("file_err"))


# 窗体ico
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xb2\x00\x00\x00w\x08\x06\x00\x00\x00\xa7\xaf\x1ao\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc1\x00\x00\x0e\xc1\x01\xb8\x91k\xed\x00\x00\x0e IDATx^\xed\x9c\x0br$7\x0eD5>\xca\xeeu\xf6sF\xdf\xc0\xfb9\x88/\xe0\r\xdfd\xb7!+\xb5\xd9)\x00\x04X\x9f\xee.\xf1E\xc8\xaa\"\x81D\x92\x85\xa2z4\x13\xfe\xf1\xdf\x1bo\x8b\xc5\x8b\xf3\xd3\xc7\xf7\xc5\xe2\xa5Y\x8d\xbc\xb8\x04\xeb\xa3\xc5$?~\xfc\xf8\xb8\xba.\xaf\xd4\x1a\xab\x91\x1d*M\xfa\x1d\xb6m\xcb\xcbz\xf6\xfe\xacF\xbe\xa1\x0flm\xc9v\xce\xde\xd3o\xd9\xc8\xabq\xcf\xe7\xe8=\xffv\x8d\x8c\r]\xcd\xfbX\xf6n\xeco\xd3\xc8\xcf\xd2\xc0\xfa\x00\x8f\xe4\x95\x1e\xed\xd6\xc6\xbe|#?[\x03\x9f\xe9\x83\x9b\xe3\xd5\x1es\xb7\xb1/\xdb\xc8\xcf\xd0\xc0\xcf\xd4H\xcf\xb0\x1f[\x185\xf6\xe5\x1a\xf9\xd1\x0f\xec\x99\x9a\xd7\xe3\xd5\x1b\x1ahc_\xa6\x91\x9f\xa5\x81_e;\xcd\xefE\x1e\xfd;/\xdf\xc8\xab\x81\xe7\xb9R3\xbft#?\xf2A\xbcr\x033Wi\xe6\x97\xfdGC\x8fnb\xab}\x85\x06\xb8\n/\xd9\xc8\xcf\xd0\xc4W\xc1\xd6bkzu^\xea\xa3\x056|O\xcbWx\x88`\xcb\xbe\xbc\xfa\x0b\xfa2\x8d\xdc\xd9\xe8Nsv4_a\xabFk\xcf\xd6\xf0\xca\xcd\xfc\x12\x8d\x8c\r\xae6\xe8\xdeKz\xc4\x03\xae\xae\xf5\xaat\xf7\xfb)\x1a\xb9\xf2\xd0\x1ee\xf3\x88&\xee6\xa9\xd6\x1f\xe5\xcf\xf8U\xcd\xd95G\xde\xbaz\x9eN\xa6qJ#\xcfn\xbc\xe5\xcd\xda\x1b\xd5\\\xcc3\xf3L\xf4y\xec\xad\xb1{#{\r\xb4s\x89\x14\xd4\xdfc\xa3\xaa\xdcmh\xa2q\xe6>(Y\x130\x16\x87\xb9('Zcg}U?\x19\xac\xb1\xb9\x91\xf70\xe4a\xba]\xad(G=\x8e0\r\xd5\xeaj,\xce\xa5\xd5\xc8\xde\xc3l\xa4\x97\x89\x1a\x92\xe94\x16\xb48\x87\xf5+Z\xddxp\xc4\xfe\x1cE\xb4.o\r\x1a\xdb\x89\x19\xd5\xe1\xf9\xea\xfe\xa5\x8d\\1\xbb\x07\xd1\xc2\x16=\xf6z>\xf6<\xa0U\xed\x81J\xf3\x8db\xbcZ\x18\x8b4\xc1]#WMoE\xebxTjWt\xc0\x16\xbd\xa3\xf6ao\xf6z~\xa6\x83\\\xbe6\xbc=\xd2:\x1c\x13y@L\xe6\xb1\xa2\x03,\xf23b\x14<\x8b\xb7x\x06u-N=d\xb9\x16\xeb\xcd\xb3FG\x13z\x1aod>^\x05o]\x11\xd8\x87h?\x98\xd1~2\xaa\x85\xf9N\r/\xb6\xfc\x1992\xbbX\x18ns\rz\x86sF\rm\xf3\x98\xf3b\xbf4rT\xdc+0\x8a\xe5\xe2\x8c\xe6YL\x14[\xc1\xcb\x8d\xbc\x01\xcf\xe3\x16\x0f\xaf\x02\xf6%Z'\xef\x9b\xc5T\xf7\xa4\x13\xe7Q\xa9\xa5\xf3|o\xaaw\x99\x91\x90g`\x14k\xf3Q\xde\x9d\t\xba\xee\xe2\xe9\x1bQ\xed\xa3\xe8\xf8?\xd3\xd7+\x12\xed\xa5\xd7'\x18s?Zx\x1b\x1d\x893\xc8C\xac\xde\x035\xa4\xf7#<\x7f\x1e#M\xae\xdb\xf5\xa0T=\x19[\xea\xec\r|\xab'o\x9c\xd7\x98\xad\xa1\xba\x97\x88\xf3\xbe\x03\xd5\xf1\xb4m\xec\xb3\x91\xb3\xe4\x11\xc8\xb5\xbc\x91\x8e\x1a\xd1\xfb\x0c\xd6V\xba\x9e\r\xd4\xde\xcb\x83\xd2\xf1\xd4\xd1\xbd\n\xd8{\\\x1b\xfa,F\xf3\xc0\xa2\xdeG\xbd\xc9\x11\\D\x0bF\xb0\x91\xd0\xd4\x87VD\x943\xaa\xcd\xa8\x8f\nU\xfd\xaa\x1e\x93iGz\x9d\xf5V\xd0:3\xeb\xe5\x1c\xcfw4\x8fq\x1b\x8b\xeaFu\x8c\xf2o-\x18\x08Z*_\x8fP\x93l,\xa2S\xa3\xa2\xb7\xb8&\xa5F\xd6\x06\xd1f\x9cm0\xd5\x01\x18\xc7\x98\xa7\x1fiV0=\xf8\xc6w&\xd2\xf6|d\x8c<\xb2\xde\xccz\xba~\xaa\xc0\xcbH\x9f=\x8f\xf60\xd2\x8a\xd6\x9d\xd5\xf6r\xc2F\xceL\x02\x8b\xd1\xb9\xccX4\xb7\x17\x91O\x8f\xccKE\xa7\xb2\x16Og6\xefl\xcc'\xfb8\xfa\xd9\xcd`\xfe\xe0\xf3K#\xc3\xb0\x0c\xbb|\x8a\xd0\"\xf5\x9e\x81\xa6\xc6\x83h|+\x91\x1f#\xaa\x93\xe5\x18[\xf2\xbcubl\xcfu\xcf\x10\xf9\xef\xf8\x8a\xd6\xe2\x8dW\xc6F1v}\xd7\xc86\xc0\xc1# \xb6\xf8\x9e\x8czE\xfb\x03M\x87kC\xef\r\xf4!\xbe\x83H\xef\xfd\xfb\xed?\xef\x91\x9adhb\x86\xe62\x91\x0er\xbc\xda\xca\xc8\x0bk\x8d\xb0X\xaeY\xc9aF^\x15]\x9f\xde{\xc0\x93\xc6Ur#\xbcuFZ\\'\xaa\xe9\xe9\x19\x99f\x04\xe7\xa0^T\xd7P-\xbb\xf3#\x03 \x9c\x15\x01ZL\xcda\x1e\xe3\x19\\+\x8bUO#\xddE\x0c?'\xdd\xd7\x8c\xd9=\xf7\xeaE\xb55\xc6*\xde\xee\xff?\xe01\x12b2\r\xe4x1\x9e\x96\x11\xe9-\x16\xe0\xbd\xa7\xfe\xf8\xfe\xb5\x91\xa3\xc6\x02QS\xb2\x96\xa7\x0b<\xfd(\xce\x1b7\xaa\x1a\x80\xe3\xd9\xdf^\xa0\xf6HwK\xed\xa8\x06\xaf\xbb\xab\xcd\xb9\x0c\xebT\xd7\xc6x96\xe6\xe9*Y\x8e\xf1E\xe7\xf6u\x17\xa1\tFTl\xb1x\x16\xde\x1b\x19\xcd[y[\xf6htO\xc3`\x1d\xf6\xe4a\xf3\xdd\xba\x1e\x91\x97\x0e\xe6\xa3\xa3\x93\xc5\xcf\xaci\x8f5\x18\xa3u\xc0\x9b\xc5\xcc\xf8\xcc@]\xd6\xe51\xf5\xa5c\x96u\xbb\xff*\x02<\x81\x11QQ\xce\x9d\xd1\x9dEk\x01\xf8\x9a\xe5\x08\xcf\xec\xe7\xc8=\xd9\x93l\x0f\xabk\xd0u\xdb=?\x9f\xe8\x1a\xbc\xff\xfaM\x8b}\t\x92y\xc6\x8b\xc5\x18\xe7q\\\xa6\xa7\xa8\x96\xd6\xab\xa0\xf5X3\xd3\xab\xf8\xac\xf8\xf1t\xbc\xbcJ\xbd\x11[\xf6\xc7r\xb3=\xc1\x9c\xc6t|k\x1e\xf42\xb8\xa6\xd66l\xcc\x14\x86+G\"\n\xaa\x10\xe0\"\x88\xad\x00\x83\x8bk\xc1\xcfu\xf4\x8c\xb9\xa7\xd0G\xfc=\xe3=\xe6\xf6\x1f\xf7D\xf6\x92m<\xc2\xd30\"\x13<\xef]\x9fA\xe49#Z\x0f3Z;3\xbb\xdel\xafPW\xe7\xbd\xf5BG\xbf{\xf0\\\x16g\xd8\xbcQ\xd5RlNk\xb0\xa6\xe6\xd8\xdd{$'r\x10\x844Q\xe1|\xa09\xde\x1c\xeb\xf3\xfc\x0c#\x8f\x8b\xc7\xe0=W~\xde\xfa\xec\xf59j\x1c\xcf\xe3\xbe\xf4\x19\x99\xd1\xd8\x11\x91\x16t0o\xf7Y\xdd\x0c\xd5R<\xcfQ]/\x16X\\6o\x8c<@#\x8ac\xa2Z3\x1a^,48Fu\xbd\x18\xc0\xb1\xde\xbc\xa1z\x86\x8eE\xf7\xfc]A\xfcg\x8c\x8d\xd9@\x94\xa0@\x00\xcc\xe4\x180\xa0\xd7U\xb8\xee\xc8;\xcfs\x9d(\xa7\x1b\x93\xd1\xa9\xabd5L\xa3\xea\xc1\xd0\xf8\xe8>\x1b7x\xce\x88\xc6\x01\xebe\x1a<\x86{\xc4W\xb0\xc8w\x05\x15b\xb2\xb9\x0c\xe4Ur\xb8FD\xa6\x13\xe5#\xc7\xe6G>\xbc\x98J\xde\xe2x\xf0\x1c\xa2\xe7a#n\x07X\x82\x07D\xbc\xf9\xac\x10\xc7s\x9c~\xef\xc0\x9aJ\xa4\xe5\xe5T\xeaFy\x99\xef,\x07\xd7#F\x1aU\xb4\x96\xe6W\xbc\x00\xcb\x1d\xad\x83c8\xd6\xa3\xaa\x05<-\x9b\x8d+,\x16/\xc2\x97\x7f\x8f\xec\xbd\x11\x8a\xf7F\x18\xd9[S\xd1\xcd\x88j\x1a\xc3\xb7u\xa26t,\x97\xaf\x19o\x8d<\xe6\xd5\xb5y\x8d\xf3\xf0r=\xb2zY\x8d\xc8\x9b\x01\x7f\x88\xe1\xf1.\x9d\\\xae\t0\xc6\xdf\x19\xc4\x7f6\xb2\x81A\x0c\xa9\xe8\xde\xb0\xa9\xa3k-b\xec9x\xfb\x8f\xf1#\xfb\xc1\xab\xad\xf5\xf8\xde\x8b7\xdcF\xeeR)t$\x95\x9a\xb4\xcc;\xe0\x99\x99\xf1\x1f\xe9{x5\x15\x8e\xf1\xfct\xea\x01\xe8p.k\xdb8\xeaz5\r\xcd\xf5b#\xfd\x11\xc8CNE\xe73\xc7\xae\xdf\xaf\x12X\xd0\xa8\x98\xb3\x1c\x8b\xd3\\C\x8dV\xf4\x16\x8b\x8c\xcf\xbf\x10\xf1\x1a\x0eT\xe6\x81\xc5ic\"7k\xd8Q\xcc\xac\xae\xa29\xb87<\x1d\x9d\xf7|\x18\x1c7\x82u\x90\xe7iv\xe9j\xb1\x87YO\x9a\xdb!\xab\xe3\xcda\xcc\xc3\xa2n\xf3q\x00\x80\xd9\x11\x9d\xc5\x98\x9e\xc6\xa3FGgq\x1e\xde3\xf3\xc8\xe2Fs\x06\xe6\x11\x8b\xf1\x88\xbb\xcf\xc8#X02\x02Xv\x14\x9ba:\xba(\x80{\xae\xa5hm\xc4F\x9e\xaaZY\xdc\x08o\r\x0c\xc6\xb4F\xe49\x03\x1a3\xb9#X\xdb\xab\xd3\xa9m\xb1Q.\xae3J\x8d\xec\x19\xc9\xd2\xb8xe\x11\x8b\xef\x89\xd7#\xdcW\xd5&6L\xe1\x16{\x1f\xac\xcd\xe7\x89U\x1bt\x94\x1b\x19\x8d\xf49\x1e1\x91\x86\x11\xad\xc5\xc6\xf9\xda\xc8t\x0c\xce\x89\xc8b0\x87z\xc6(\x96\xe1<F5\xbb\xa0\x0e4\xbc\xba\x1c\xb3W=Cu\xb4N\x95\xcf?\xec1#\x81\xee\"<=\xd6\xd0\xf9\xaa>\xf2T\xcb\xcb\xc78\xe7x\xd7\x11\xd0\xac\xc4\xa1\x96\xa2\xf5\xb8\xae\x17\xbf\x15\xf5\xca5\xbc\xbaGz\x82v\x15\xf5>\xc2\x94{\x19\x8b\xd3\xe8>Lc\xcf\xe6\x8b`_3\xf5t]xy\xb64\xfa{#{\xc60\xa6\xf7\x15`L\xaf\r5\xabu\x18\xadY\x89a\xbcx\xc3r\xe0\x0b\xdf38\xd6\x83\xf3\xbbz^lE\x03x\x9e\x90\xcb:^\x9c\x01\x1f\xb3d\xfa\xbc\x06\x9d\x8f\xe6x<C\xf5\xdc?\xec\xcd\x083\x96\xef\x19\xf5\xc6\x16\xd7a\xd4+\xe8\x8b\xec\xd9\xcf\xf4\x9b\xf1\xd9\xc8,\xceb(\xde!\xcaA\r\xcce\x0b\xca\xa8\xf8\x81\x87-^x\xce\xd3\x8a\xb4\rO\xafJ\xa4\t2m\xf8\xd4\xeb\xadxZ#\x9f`\xe4\x01:\xd58\x0f\xcb\xac\xb9Y,v\x82\x1b\xd2\x9a\x17/\xc9\xe8\xc5\xf0\x1a\xfd\xf3%\xb8]\xb4\x1a9\x13\x03#S<\x0f=\xbe\xb7k\xfd\x9e\x01\x8d\x08/\xbf\xa2\x0b:^*\xb0^\xc6\xa8\xd6(\xdf`\x8d(^\xd7\xc6q\xec3\xf2\xa3\xf1\xcch\x8ekF\xfa\x11\xacmW\xbd\xec\x1b\\\x90\xc5\x0c\x9b\xab\x9a\xd2\x85\x00\xd6\xd0\xf1*\x9c\xb78\x16~.\xba\xef\xd13\xc3\xf3\xd5\xeb\x08\xefy\xde\xd5\xbd\xdd\xdc)T\x8dD\x8c\xf2G\x0b\xe0|\x9b\xd3x\xa0y\n\xf2\xbc\x1aF4\x1e\x81\xda\x95\xba\x19\x9c_\xf1\x10\xe9\xa9\x8e\x12\xcd{\xf50\x8f9\xbd\xf7\xa8\xf8\x8a\xb0\\\xaee\xd7\x91\x1e\x18\xe9\x0e?Zh\x81\x91\xa0\xa1F#<\xad\xea\xc2\xbe\x1b\x7f\xfa\xc7_>\xae\x16\x1e\x9b?#g\xcd\xa8\xf0x\xd6\xa8\x9c\x1biU\xc9jvu=\xcf{h\x18\xa6\x13\xcd\x81\xac\xd6(\xd7\xf0\xf6\x81\xebz\xf3\x86\xd6\xfd\xf3?\xff\xfa\xf6\xdb\xdf\xfe\xf5q\xf7\x07\x15\xef\x16\xc3\xdfg\x88\xbc\xfd\xf4\xfe\xdf\x06\x96\xc8_&\xac_F4\xce\xa8\x96}\x19\x9a\xc3\xf7\xd1W\x85\xacN\xe5\xcb\xc3\x8b\xcb\xbe\"\xb29\xa0Z\xfcU\xc1\x8b\xe5\xfbH\x0b\xe3<\xafc\xbc\xb7\xde\x17\xe7\xd9}\x15\xae\x81\\\xfe\x02\xed\x13\xb9Bd\xd6\xc6\x17\xcfG\xd6\x02v\xfa*z\x1aG\xe8\xf3\xae\xb4\x9a\x97\xe3yPNod\x8cWb\x8c(\xae\x83ixD\xbaQ|F\xe6\x11z\xb3\xf5F\xeb\xd7|\x8b\xf7\xc6:\xa0y\xaaMkD5m\xbc\xba\xf6\xaeO`*s\x99\x17\xa6\xba\x99\xfa\x10f\xd9Z\xcf\xf2\xbd\xb9NS\xe8\xa9Wi\xe0J\x13Z\x0c\x8fWrf\xb8;\x91\xf7*\xa2\xe6A4\xcex\x0b\xef\xf8\xd05x\x98^W\xd7\xa3R\xcb\xe8\xd6\x89t\xa13\x9a\xcf\x88~Lg\x8d;[\xcf\xcb\xdb\xba\xe7\x11\xe9G\x8bh\x01\xebWA\x8bg\xa3\xf4\x19\xb9\xfbc\xc7^\x00\x93\x8d^\x84*\xd0(X|\x1at\xcd\x15\xef\x95}\x82N\xe5\x0f>F\xe7\xb3\xad\xc1\x1e\xd4s\xc7\x1fb\xf5>\xa2\xb2?\x15~\xdcN\xd7}\x94\x16\x8b\x07b\xafK\xd8\xc8\xb3o\x8b\xbd\x85{\xbci\xfav?\x1b\xde\xe9\xc8'\xa1\xcd\xf3}t:\x9d\xf1Q\xed?\x7f\xff\xf7\xc7\xd5=[\xf7v\xf6\x19U\x7f\xb2(\xd1O\x9au\"/.A\xda\xc8\xdd\xcfY`\xaf\x13\xd9\xd8Kk\xf6\x04\xc8\xc0\xfe\x98\xc7\xd1\xa9\xda\xdd\xcb\xc8\xaf\xeaD\xa7\xfc\x19'\xe4l\x7f\x1cA\xf8\x87\xbd\xca\xc39\n\xde\xa0\xbd\x1a0\xfa\xd1\xda!\xdb\x0f\xd5\x7f\xd4\xde}W\x86\xbf\xb5\xd07\xbe\xfa\xa6\xebIz\xc4\x89\x985g\xd5\xa7\x92\xf9|\xe4\t\xb4\xe5\xc4\xb4\xdcY\xefx\xfe\xb3\xfby\x16\xe6\xb2\xecp\xcb)\xb3\xc7\x89ht_\x0e~\x98\x15\xcen\xd6-\r:\x82\xb5\xbb\xebz\x95\x06\x06\xad?\xecy\x9b\x91\x9d\xd8z*\x1f\xcdLS<\x1b{\xbcH\xb3\r\xcc\xcf\xf2\xd5\x9e[\xe9/D:hc\x1bgl\x8am\xc6\xdeM\x00ft\xa3\x87\x13imy\x98\xd0\x84\xc6\xb36owO:\xac_\xbf-.\xc1\xee'r\x04>f\xe8\x89}R\xf9MtN\x92j\xec\x91\xa7\xd3\x08<\x83h\xef#oU\x8eZC\xb6g\xebD^\\\x82\xd3Nd\x80\x939\xc2\xe6\xa3\xdf\x8e\x8c\xde\xf4-'\tko=\x91\x94\xee\t\xd5\xa9\xcf\xda\xfc\xd3\x8e\xf7X\xf5t\xad\xb8\xcf\xe2\x98\xbd\xf7\xa7C\xe4i\x9d\xc8\x8bKp\xc8\x89<\xf3\xc6Fo\x9a\x12}\xc6\x8ejVt\xb7\x9e0U\xefF\xb7VG\xbb\xcb^'\xeb\x11\x1e\xbb\xde\xd6\x89\xbc\xb8\x04w'r\xe5-8\xf2\x84\xf0\xf0<e\x1e\xa2\x13{O\xf68\xc9\xbc5\xa8ne\xaf\xf7\xf0\xb273=2Z\xc7H\xf3a'r\xe5A\x1a3\x9b\xc2\xec\xdd\xd8\xcf\xd88\x8b\xf5\xd1bq\x11\x0e\xfb\xf5\xdb#N.=\xbd\x8f\xf20[\x07y3\xbe,\xf7Q?\r\xb6\xfeT\x8c\xe8\xac'\xf3`:\xebD^\\\x82C\xffB\x84\xdf\xb8\xd1\x1b5C\xe7\xa4x\xd4i\x06\xd4\xab\xe7\xc7b\x1e\xe93\xda\xcf\xae\xa7\xces\xf1\x88\xfeR\x0c\xff\x14\xd8k\xd9u\"/.A\xe9D\xdezJl}Cg8\xfad\xcb\xd6\x84\xdf\x94x\xa7\xca#\xe8\xec\xff^\xcfZ\x7f[dt\xf6c\xe4Y}\xb6Nd\x16?\xbaQ\x16\x8b\x0eS\x9f\x91\xad\x89;o\xf9\xa38\xeae\xdbk\xed\xd1>^\xe5\x908\xb3G\xd6g\xe4\xc5%p\x1b9;%\x9e\xfd$\x9e9\xcd\x1e\xb5\xa6\x8a\xd7\xad\xde\xa2S_\xc9\xbcd\xf9\x9a\xc7\xb1g>\x8bu\"/.A\xfa\x19\xb9\xfa6W\xe8\xbe\x9d\xd5\xba\x91\xee^\xbe\xcf\x80\xf7y\xe6\x14\xf3\x98\xd9?\xcd\xc9\xbcd\xfa\xa35\x1c\x91{Z#w\x19-\xa8\xcb\xcc:\xf6\xf6P\xe1\x8c\xfd>z]\x955\xcc6l\xc4\xfah\xb1\xb8\x04O{\"\x1fA\xf5$\xdac\xcd\x9dZ\xb3\xfb\\\xad\xe1\x81z[4\x8cg\xe9\x8f\xe1\xef\x91\xb7.t\xb18\x83\xa9\xbf\x10y4\xd1\xcb\xa5\xa7\xc3(\xae\xfb\x92VN\x9fG\xbe\xf8\xe6\xcf\xab\xbf\xe5\xd4|\xe4z<\xa2\xff\x87\xe0\xfa\x8c\xbcxj\xaa\xff\xf3\xcb\x97:\x91gO\x87\xe8\xa4\x1a1sr\xeb\xe97\xca\xddrZ\x1e\x85z>\xca\xe3\xaf\xbf\xfe\xfa\xf6\xf3\xcf?\xbf\xfd\xf2\xcb/o\xbf\xff\xfe\xfb\xc7\xe8\x0coo\xff\x03\xd1zR[\x94\xcf&\x14\x00\x00\x00\x00IEND\xaeB`\x82"

if __name__ == "__main__":
    main()
    logging.info("app end")
