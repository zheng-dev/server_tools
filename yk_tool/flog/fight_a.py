#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-19
# decription: 分析战报日志
import os


class AnalyseFALog:
    __tab_skill_eff_do: dict[str, list[tuple[str, list, int]]] = (
        {}
    )  # 技能生效触发的效果sid
    __fileName = ""

    def analyse(argsv: list[str]):
        a = AnalyseFALog(argsv[2])

        a.do()
        a.save_ret()

        print("===done==")
        return

    def __init__(self, fName: str) -> None:
        self.__fileName = fName

    def do(self):
        print("===start_log:", self.__fileName)
        # 匹配主动技开始
        flagSkillS = "====主动技开始:主动技uid:"
        flagSkillSid = "主动技sid:"
        flagSidLen = len(flagSkillSid)
        # 匹配主动技结束
        flagSkillE = '"=======end_skill",no_key:'
        # 匹配技能耗时
        flagTime = ",no_key:"
        flagTimeLen = len(flagTime)
        # 匹配效果sid
        flagEffS = "效果器:效果器sid:{"
        flagEffSLen = len(flagEffS)
        flagEffE = ","

        with open(self.__fileName, "r", -1, "utf8") as fPtr:
            currSkill = ""
            ret: dict[str, list[tuple[str, list, int]]] = {}
            while fPtr:
                line = fPtr.readline()
                if line == "":
                    break
                if flagSkillS in line:  # 开始技能
                    i1 = line.find(flagSkillSid)
                    i2 = line.find(",", i1)
                    currSkill = line[i1 + flagSidLen : i2]  # 技能sid
                    list1: list = ret.get(currSkill, [])
                    list1.append((line, [], -1))
                    ret[currSkill] = list1
                elif flagEffS in line and currSkill != "":
                    i1 = line.find(flagEffS)
                    i2 = line.find(flagEffE, i1)

                    list1: list[(str, list, int)] = ret.get(currSkill, [("", [], 0)])
                    nowIndex = len(list1) - 1
                    r: tuple[str, list, int] = list1[nowIndex]
                    (oLine, oEffL, u) = r
                    row1: str = line[i1 + flagEffSLen : i2]
                    row2: str = row1 if row1[-1] != "}" else row1[:-1]
                    oEffL.append(row2)
                    list1[nowIndex] = (oLine, oEffL, u)
                elif flagSkillE in line:
                    list1: list = ret.get(currSkill, [])
                    nowIndex = len(list1) - 1
                    (oLine, oEffList, u) = list1[nowIndex]
                    i1 = line.find(flagTime)
                    i2 = line.find(flagTime, i1 + flagTimeLen)
                    i4 = line.find(",", i2 + flagTimeLen)
                    useTime = line[i2 + flagTimeLen : i4]  # 耗时
                    list1[nowIndex] = (oLine, oEffList, useTime)
                    currSkill = ""  # 重置
            self.__tab_skill_eff_do = ret

    ##结果存入csv
    def save_ret(self):
        import csv

        if [] != list:

            with open(f"{self.__fileName}.csv", "w+", -1, "utf-8-sig") as ePtr:
                writer = csv.writer(ePtr, quoting=csv.QUOTE_ALL, lineterminator="\n")

                ret = self.__tab_skill_eff_do
                writer.writerow(
                    ["技能sid", "技能用时", "效果个数", "技能信息", "期间效果sid"]
                )
                for k in ret:

                    row = [""] * 20
                    for oLine, oEffList, useTime in ret[k]:
                        row[0] = f"\t{k}"
                        row[1] = useTime
                        row[2] = len(oEffList)
                        row[3] = oLine[:-49]
                        row[4] = f"\t{','.join(oEffList)}"
                        writer.writerow(row)


##分析战斗buff
class AnalyseFightBuff:
    t_buff_uid = []
    t_buff = []
    t_add_buff = []
    max_line = 0  # 最大行数

    def analyse():
        a = AnalyseFightBuff()

        def l(line: str) -> list[str, str, str, str]:
            ret = line[1:].split(",")
            ret[2] = ret[2][1:]
            ret[3] = ret[3][:-2]
            return ret

        a.do(
            "fight_log_触发buffuid",
            ["耗时", "总执行次数", "buffUid", "buffSid"],
            "t_buff_uid",
            l,
        )
        a.do(
            "fight_log_触发被动和buff",
            ["耗时", "总执行次数", "buff或者被动sid"],
            "t_buff",
        )
        a.do("fight_log_挂载buff", ["耗时", "buff_add次数", "buff_sid"], "t_add_buff")

        a.save_ret()
        print("===done====")
        return

    ##结果存入csv
    def save_ret(self):
        import csv

        if [] != list:
            with open("event.csv", "w+", -1, "utf-8-sig") as ePtr:
                writer = csv.writer(ePtr, quoting=csv.QUOTE_ALL, lineterminator="\n")

                i = 0
                maxLine = self.max_line
                while i <= maxLine:
                    row = [""] * 20
                    try:
                        row[0] = self.t_buff_uid[i][0]
                        row[1] = self.t_buff_uid[i][1]
                        row[2] = self.t_buff_uid[i][2]
                        row[3] = self.t_buff_uid[i][3].strip()
                    except:
                        pass
                    # 空3列
                    try:
                        row[6] = self.t_buff[i][0]
                        row[7] = self.t_buff[i][1]
                        row[8] = self.t_buff[i][2].strip()
                    except:
                        pass

                    # 空3列
                    try:
                        row[11] = self.t_add_buff[i][0]
                        row[12] = self.t_add_buff[i][1]
                        row[13] = self.t_add_buff[i][2].strip()
                    except:
                        pass

                    writer.writerow(row)
                    i += 1
        return

    ##整理出数据
    ##ret:[[时间,次数,buff]]
    def d_t_buff_uid(self) -> None:
        os.chdir("fight_log_触发buffuid")
        f = os.listdir("./")
        print(f"==={f}")
        with open(f[0], "r", -1, "utf8") as fPtr:
            lNum = 0
            ret = [["耗时", "总执行次数", "buffUid", "buffSid"]]
            while fPtr:
                line = fPtr.readline()
                if line == "":
                    break
                lNum += 1
                if lNum == 1:
                    continue
                row = line[1:].split(",")
                ret.append([row[0], row[1], row[2][1:], row[3][:-2]])
        self.t_buff_uid = ret
        self.max_line = max(len(ret), self.max_line)
        os.chdir("../")

    ##
    def do(self, dir: str, head: list[str], key: str, rowFun=None) -> None:
        os.chdir(dir)
        f = os.listdir("./")
        print(f"==={f}")
        with open(f[0], "r", -1, "utf8") as fPtr:
            lNum = 0
            ret = [head]
            while fPtr:
                line = fPtr.readline()
                if line == "":
                    break
                lNum += 1
                if lNum == 1:
                    continue
                if rowFun is None:
                    row = line[1:].split(",")
                else:
                    row = rowFun(line)
                ret.append(row)
        setattr(self, key, ret)
        self.max_line = max(len(ret), self.max_line)
        os.chdir("../")
