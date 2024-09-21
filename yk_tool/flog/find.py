#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-19
# decription: 检查日志
import sys, os
from . import progress as p


# 检查
class Find:
    retList: list[tuple[int, str, str, int, int, int]] = []
    allPage = 0  # 总页数
    currPage = 1  # 当前页码
    rowNum4Page = 20  # 每页显示条数
    page = []  # 当前页内容

    def find(self):
        import glob, time

        files = glob.glob(sys.argv[1])
        startStr = sys.argv[2]
        endStr = sys.argv[3]
        print(sys.argv[1], startStr, endStr, files)
        c, row = os.get_terminal_size()
        self.rowNum4Page = row - 4
        # 整理出结果[(sortField,findStr，file,lineNum,sPos,len1)]
        pro = p.Progress()
        for f in files:
            with open(f, "r", -1, "utf8") as fPtr:
                lineNum = 0
                while fPtr:
                    line = fPtr.readline()
                    lineNum += 1
                    if line == "":
                        break
                    if line.find("fight_mode => 4") > -1:
                        i = line.find(startStr)
                        if i > -1:
                            i2 = line.find(endStr, i)
                            if i2 > -1:
                                txt = line[i : i2 + 1]
                                len1: int = len(line)
                                sPos: int = fPtr.tell() - len1
                                self.retList.append(
                                    (len(txt), txt, f, lineNum, sPos, len1)
                                )
                    pro.progress_no_sum()
        del pro
        # 显示
        try:
            self.retList.sort(reverse=True)
        except:
            pass
        print(f"sort:{time.time()}")
        # print(self.retList)
        self.display() if self.calc_page() else print("no match")

    # 计算页码
    def calc_page(self):
        if len(self.retList) < 1:
            self.currPage = 0
            return False
        else:
            p = int(len(self.retList) / self.rowNum4Page)
            self.allPage = p if len(self.retList) % self.rowNum4Page == 0 else p + 1
            return True

    # 逐页显示
    def display(self):
        if self.currPage <= self.allPage:
            pass
        elif self.currPage > self.allPage:
            self.currPage = self.allPage
        else:
            self.currPage = 1

        self.page = self.retList[
            (self.currPage - 1) * self.rowNum4Page : self.currPage * self.rowNum4Page
        ]
        i = 1
        for sort, findStr, file, lineNum, sPos, len1 in self.page:
            print(f"{i}:{findStr}-->{file}:{lineNum}")
            i += 1
        print(f"页码{self.currPage}/{self.allPage} 每页{self.rowNum4Page}条")
        # 用户操作
        self.cmd()

    def cmd(self):
        cmd = input("下一页(n);前一页(b);反排序(r);显示指定原内容(d 条目id);退出(q):")
        cmd2 = cmd.strip()
        if cmd2[:1] == "b" and self.currPage > 1:
            try:
                line = int(cmd2[2:])
            except:
                line = 1
                pass
            self.currPage -= line
            self.display()
        elif (cmd2 == "" or cmd2[:1] == "n") and self.currPage < self.allPage:
            try:
                line = int(cmd2[2:])
            except:
                line = 1
                pass
            self.currPage += line
            self.display()
        elif cmd2 == "r":
            self.retList.reverse()
            self.display()
        elif cmd2 == "q":
            pass
        elif cmd2[:2] == "d ":
            try:
                line = int(cmd2[2:])
                if line >= 1 and line <= self.rowNum4Page:
                    (sortF, findStr, file, lineNum, sPos, len1) = self.page[line - 1]
                    self.__d_line(file, sPos, len1)
                    self.cmd()
                else:
                    raise ("error")
            except:
                print(f"输入无效:{cmd2}")
                self.cmd()
        else:
            print(f"输入无效:{cmd2}")
            self.cmd()

    def __d_line(self, file: str, sPos: int, len1: int):
        """直接显示第N行内容"""
        with open(file, "r", -1, "utf8") as fPtr:
            fPtr.seek(sPos)
            lineStr: str = fPtr.read(len1)
            print(lineStr)
