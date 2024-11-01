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
        self.log.insert(tkinter.CURRENT, rets)

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
        self.log.insert(tkinter.CURRENT, rets)

    def now_utc(self):
        self.logNum += 1
        rets: str = f"{self.logNum}>> now --> {time.time()}\n\n"
        self.log.insert(tkinter.CURRENT, rets)

    def to_local(self):
        self.logNum += 1
        stime: str = self.timeUtc.get().strip()
        t = int(float(stime))
        utc = datetime.fromtimestamp(t)  # int(time.mktime(dt))
        rets: str = f"{self.logNum}>> {stime} --> {utc}\n\n"
        self.log.insert(tkinter.CURRENT, rets)

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
    TimeToolWindow().display().mainloop()
    # tk主窗关闭后
    logging.info("main end")


if __name__ == "__main__":
    main()
    logging.info("app end")
