#
# coding=utf-8
#py3.11
# 运行方式：python delete_db.py ../
import os, sys, shutil


def main():
   # 参数是db文件夹所在的路径
   try:
    args = sys.argv[1]
    print(("=start args=:"+args))
    del_tab_bak_dir(args)
    print("=success====")
   except  FileNotFoundError as e:
      print("err:%s %s"%(e.strerror,e.filename))
      return -1


def del_tab_bak_dir(dbPath):
    """删除表目录下的备份文件夹"""
    # 强行到指定的db目录去操作
    os.chdir(dbPath + "/db")
    for db in os.listdir("."):
        os.chdir(db)# 进库
        for table in os.listdir("."):
            os.chdir(table)# 进表
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
            # print(table, dataDirL)
            os.chdir("../")
        os.chdir("../")
    return


main()
