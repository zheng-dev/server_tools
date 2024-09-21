# from . import *


# 显示行
def d_line_cmd(argv: list[str]):

    file = argv[2]
    lineNumArg = int(argv[3])
    with open(file, "r", -1, "utf8") as fPtr:
        lineNum = 0
        while fPtr:
            line = fPtr.readline()
            if line == "":
                break
            lineNum += 1
            if lineNum == lineNumArg:
                print(line)
                return
