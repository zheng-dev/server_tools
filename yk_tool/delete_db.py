#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-08-29
# decription:删除文件db的增量bak文件
import os, shutil
import sys, subprocess
import time

__DB_CFG_ = "db_path.cfg"
__EXIT = "exit"


def main() -> None:
    """删除db目录的增量文件
    pyw delete_db.py
    py delete_db.py -i
    py delete_db.py ../
    """
    if len(sys.argv) < 2:
        print(sys.argv, sys.executable)
        cmd = [sys.executable, sys.argv[0]]
        subprocess.Popen(cmd, detach=True)

    elif sys.argv[1] == "-sub":
        time_do()  # 定时清理中
    elif sys.argv[1] == "-exit":
        # 加退出标记
        with open(__EXIT, "w+", encoding="utf-8") as f:
            f
    elif os.path.isdir(sys.argv[1]):
        # 传指定目录
        ret: bool = del_tab_bak_dir(sys.argv[1])
        print("del_pwd_tab done=", sys.argv[1], ret)


# 定时处理
def time_do():
    current_path = os.path.dirname(__file__)
    _r = os.chdir(current_path)
    sys.stdout = open(".output.txt", "w+")
    while True:
        if True == os.path.exists(__EXIT):
            print("exit")
            os.remove("exit")
            return
        del_cfg_tab()  # 定时清理中
        sys.stdout.flush()
        time.sleep(2)


def del_cfg_tab() -> None:
    """从配置中读取要清的db所在目录,遍历清除增量目录"""
    try:
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        with open(__DB_CFG_, "r", encoding="utf-8") as f:
            while f:
                line = f.readline()
                if line == "":
                    break
                # 去掉空行
                line = line.strip()
                if line == "" or line[0] == "#":
                    continue
                del_tab_bak_dir(line)
    except FileNotFoundError as e:
        print("err:{0},{1}".format(e.strerror, e.filename))


def del_tab_bak_dir(dbPath: str) -> bool:
    """删除表目录下的备份文件夹"""
    # 强行到指定的db目录去操作
    try:
        os.chdir(dbPath + "/db")
    except OSError as e:
        print("path_no_db-->{0}".format(e.filename))
        return False
    for db in os.listdir("."):
        os.chdir(db)  # 进库
        for table in os.listdir("."):
            os.chdir(table)  # 进表
            # 删除 表目录 下的备份文件夹(要留时间最近的一个
            dataDirL = os.listdir(".")
            if len(dataDirL) > 2:
                dataDirL.remove(".opts.run")
                dataDirL.sort()
                dataDirL.pop(-1)
                for dir in dataDirL:
                    try:
                        shutil.rmtree(dir)
                    except OSError:
                        print(("rm err:" + dir))
                        continue
            os.chdir("../")
        os.chdir("../")
    return True


def init_cfg(r: int | str, osStr: str) -> None:
    # 初始配置
    with open(__DB_CFG_, "w+", encoding="utf-8") as f:
        if f:
            f.writelines(
                [
                    "#配置注释可以是#开头的行\n",
                    "#本配置必需是utf8文件\n",
                    "#db所在路径的配置,可以是多个项目如\n",
                    "#F:\\snk_work\\server_code\\alpha\\game_alpha\n",
                ]
            )
    print("{2} timer ok:{0},请手动修改db配置=>{1}".format(r, __DB_CFG_, osStr))


def install_timer() -> None:
    """
    根据系统安装定时器安装\n
    如果频率太高,可以用常驻进程不退,以避免高频加载
    """
    if sys.platform == "win32":
        # currentPath = os.getcwd().replace('\\','/')    # 获取当前路径
        # SCHTASKS /DELETE /TN "yk_db_bak_del"
        (path, exeName) = os.path.split(sys.executable)
        exePath = path + "/pythonw.exe"
        if not os.path.exists(exePath):
            exePath = sys.executable

        r = os.system(
            'schtasks /create /sc minute /mo 30 /tn "yk_db_bak_del" /tr {0}" {1}"'.format(
                exePath, __file__
            )
        )
        if r == 1:
            print("定时器失败,确认是否管理员权限:{0}".format(r))
        else:
            init_cfg(r, "win")

        pass
    else:
        print("*/10 * * * * {0} {1}\n".format(sys.executable, __file__))
        print("请手动执行命令在定时器中增加上面内容->contab -e")
        init_cfg(0, "linux")
        pass


if __name__ == "__main__":
    main()
