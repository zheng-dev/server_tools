#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-19
# decription: 分析event用时日志
from . import progress as p


class Event:
    def analyse(args: list[str]):
        f = "event.txt"
        try:
            f = args[2]
        except:
            pass

        (lineNum, condLineNum, kvList) = Event.clear_data(f)
        print("总条数{0};100ms的条数{1}".format(lineNum, condLineNum))
        Event.save_ret(kvList)
        return

    ##结果存入csv
    def save_ret(kvList: dict):
        import csv

        if {} != dict:
            with open("event.csv", "w+", -1, "utf-8-sig") as ePtr:
                writer = csv.writer(ePtr, quoting=csv.QUOTE_ALL, lineterminator="\n")
                writer.writerow(
                    [
                        "事件mf",
                        "总次数",
                        "100m的次数",
                        "平均用时",
                        "最大用时",
                        "最大用时日志",
                    ]
                )
                # writer.writerow(['事件mf | 总次数 | 100m的次数 | 平均用时 | 最大用时 | 原日志'])
                for key in kvList:
                    oldTimes, old100Times, oldAccMs, oldMaxMs, oldLine = kvList.get(key)
                    writer.writerow(
                        [
                            key,
                            oldTimes,
                            old100Times,
                            round(oldAccMs / oldTimes),
                            oldMaxMs,
                            oldLine.strip(),
                        ]
                    )
                    # print("{0} | {1} | {5} | {2} | {3} | {4}".format(key,oldTimes,round(oldAccMs/oldTimes),oldMaxMs,oldLine.strip(),old100Times))
        return

    ##整理出数据
    ##ret:(lineNum,condLineNum,kvList)
    def clear_data(logFile: str) -> tuple[int, int, dict]:
        with open(logFile, "r", -1, "utf8") as fPtr:
            lineNum = 0  # 总条数
            condLineNum = 0  # 满足过虑条件行数
            kvList = {}  # 结果
            pro = p.Progress()
            while fPtr:
                pro.progress_no_sum()
                line = fPtr.readline()
                if line == "":
                    break
                lineNum += 1
                uSIndex = line.find("{use_ms,")
                if uSIndex >= 0:
                    uEIndex = line.find("}", uSIndex)
                    useMs = int(line[uSIndex + 8 : uEIndex])
                    if useMs < 100:
                        continue  # 小于100ms的不统计

                    # 上面找到了使用时间
                    # 下面找事件mf
                    mfSIndex = line.find("{", uEIndex)
                    mfEIndex1 = line.find(",", mfSIndex)
                    mfEIndex2 = line.find(",", mfEIndex1 + 1)
                    mfStr = line[mfSIndex:mfEIndex2] + "}"

                    oldRow = kvList.get(mfStr, 0)
                    # 统一上100ms的
                    reach100 = 0 if useMs > 100 else 1

                    if oldRow == 0:
                        # (总次数,总用时ms,上100ms的总次数,单次最大用时ms,最大ms时的line)
                        kvList[mfStr] = (1, reach100, useMs, useMs, line)
                    else:
                        oldTimes, old100Times, oldAccMs, oldMaxMs, oldLine = oldRow
                        if oldMaxMs < useMs:
                            oldMaxMs = useMs
                            oldLine = line
                        kvList[mfStr] = (
                            1 + oldTimes,
                            old100Times + reach100,
                            useMs + oldAccMs,
                            oldMaxMs,
                            oldLine,
                        )

                    # print("tttt{0}==={1}----{2}".format(useMs,mfStr,kvList))
                    # if lineNum==2:
                    #     break
                condLineNum += 1
        return (lineNum, condLineNum, kvList)
