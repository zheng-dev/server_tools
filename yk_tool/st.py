#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-08-29
# decription:比较a,b两个文件段,分析出b新加了哪些,老的是哪些
import os, sys


def main():
    current_path = os.path.dirname(__file__)
    os.chdir(current_path)
    a = False
    cA = {}
    cB = {}
    with open("a.txt", "r") as f:
        while f:
            line = f.readline()
            if line == "":
                break
            elif line[:3] == "===":  # A;B分组线c
                a = True
            else:
                r = line.split(",")
                if a:
                    cA[r[2][:-2]] = r[1]
                else:
                    cB[r[2][:-2]] = r[1]
                pass
    old = 0
    for i in cA:
        try:
            if cB[i] != cA[i]:
                print(f"{i}->old={cA[i]},n={cB[i]}")
        except:
            print(f"{i}only old{cA[i]}")

    # all=len(cB)
    # add=all-old
    # print("新加{0},老的{1},总的{2}".format(add,old,len(cB)))
    return 0


def test():
    print("\033[20A\033[?25l", end="")
    for i in range(60):
        s = get_single_char()
        print("\033[2J", end="")
        print("\033[31m 红色{0}{1}字 \033[m".format(i, s))


##不用回车的单次输入
def get_single_char():
    if sys.platform == "win32":
        return w__get_single_char()
    else:
        return l_get_single_char()


def w__get_single_char():
    import msvcrt

    return msvcrt.getch().decode()


def l_get_single_char():
    import sys, tty, termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    # 设置新终端设置：无回显，非阻塞
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        # 恢复旧的终端设置
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main2():
    import numpy as np
    import matplotlib.pyplot as plt
    from local_dir import d

    d.D.sort()
    counts = np.bincount(d.D)
    am = np.argmax(counts)
    r = f"总录像条数={len(d.D)};(内容byte统计为)-->均值={np.mean(d.D)},中位数={np.median(d.D)},min={min(d.D)},max={max(d.D)},众数={am},众数个数={d.D.count(am)}"
    print(r)

    # hist1, bin_edges1 = np.histogram(d.D, bins=11, density=False)
    # for i in range(len(hist1)):
    #     print(
    #         f"{round(bin_edges1[i],2)}kB~{round(bin_edges1[i + 1],2)}kB ==> {hist1[i]}"
    #     )
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 全局生效
    plt.hist(d.D, bins=list(range(0, 173)))
    plt.title("战斗录像容量分布")
    plt.grid()
    plt.xlabel("容量区间 (单位 kB)", fontproperties="SimHei")
    plt.ylabel("归类 (单位 条数)", fontproperties="SimHei")
    plt.show()

    # print(hist1, bin_edges1, d.D[-3:], d.D[0:3])


# from typing import NamedTuple


def main_work():
    """从xls里导出工作周报txt"""
    import csv, os

    os.chdir("local_dir")
    filePath: str = "C:\\Users\\Administrator\\Downloads\\Sheet1.csv"
    with open(filePath, newline="", encoding="utf-8-sig") as csvfile:
        ret: dict[str, list[str]] = {}
        exclude: list = ["", "周末", "请假", "事假"]
        row: list[str]  # [num,name,date,week,txt1,txt2,txt3...]

        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            oldRow: list = ret.get(row[3], [row[2], 0])
            oldRow[1] = row[2]
            for field in row[4:]:
                if field not in exclude and field not in oldRow:
                    oldRow.append(field)
            ret[row[3]] = oldRow
    # del
    os.remove(filePath)
    # 输出txt
    outFile: str = "work.txt"
    with open(outFile, "+w", encoding="utf-8") as w:
        for i in range(1, 53):
            week = ret[str(i)]
            w.writelines(f"===第{i}=周=={week[0]}--{week[1]}==\n")
            for idx, txt in enumerate(week[2:], 1):
                w.writelines(f"{idx}. {txt}\n")
    print("===done==")
    os.startfile(outFile)


def bc():
    """两行逐字对比"""
    with open("d:\\a.txt", "r", encoding="utf-8") as a:
        l1: str = a.readline()
        l2: str = a.readline()
        s2: int = len(l2)
        i = 0
        while True:
            try:
                print(i, l1[i], l2[i])
                if s2 < i and l1[i] != l2[i]:
                    print("====ok==", l1[i - 4 : 40])
                    print(l2[i - 4 : 40])
                    return
            except:
                print(i, l1[i - 6 :], l2[i - 6 :])
                return
            i += 1


if __name__ == "__main__":
    main_work()
