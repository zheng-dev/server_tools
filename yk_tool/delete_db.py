#
# coding=utf-8
#py3.12.5
#Auther:zhengzhichun [zheng6655@163.com]
#Date: 2024-08-29
#decription:删除文件db的增量bak文件
import os,shutil

import sys

_DB_CFG_="db_path.cfg"
def main():
   """安装或执行清理"""
   if len(sys.argv)>1:
       install_timer()
   else:
       current_path = os.path.dirname(__file__)
       r=os.chdir(current_path)
       sys.stdout = open('output.txt', 'w+')
       del_cfg_tab()#定时清理中
   

def del_cfg_tab():
    """从配置中读取要清的db所在目录,遍历清除增量目录"""
    try:
        with open(_DB_CFG_,'r',encoding='utf-8') as f:
            while f:
                line=f.readline()
                if line=="":
                    break
                #去掉空行
                line=line.strip()
                if line=="" or line[0]=="#":
                    continue
                del_tab_bak_dir(line)
    except FileNotFoundError as e:
        print("err:{0},{1}".format(e.strerror,e.filename))
    return 0

def del_tab_bak_dir(dbPath:str):
    """删除表目录下的备份文件夹"""
    # 强行到指定的db目录去操作
    try:
        os.chdir(dbPath + "/db")
    except OSError as e:
        print("path_no_db-->{0}".format(e.filename))
        return -1    
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
            os.chdir("../")
        os.chdir("../")
    return

def init_cfg(r:int|str,osStr:str):
    #初始配置
    with open(_DB_CFG_,'w+',encoding='utf-8') as f:
        if f:
            f.writelines(["#配置注释可以是#开头的行\n","#本配置必需是utf8文件\n","#db所在路径的配置,可以是多个项目如\n","#F:\\snk_work\\server_code\\alpha\\game_alpha\n"])
    print("{2} timer ok:{0},请手动修改db配置=>{1}".format(r,_DB_CFG_,osStr))
    return None



def install_timer():
    """根据系统安装定时器安装"""
    if sys.platform=="win32":
        #currentPath = os.getcwd().replace('\\','/')    # 获取当前路径
        #SCHTASKS /DELETE /TN "yk_db_bak_del"
        (path,exeName)=os.path.split(sys.executable)
        exePath=path+"/pythonw.exe"
        if not os.path.exists(exePath):
            exePath=sys.executable

        r=os.system("schtasks /create /sc minute /mo 30 /tn \"yk_db_bak_del\" /tr {0}\" {1}\"".format(exePath,__file__))
        if r==1:
            print("定时器失败,确认是否管理员权限:{0}".format(r))
        else:            
            init_cfg(r,"win")

       
        pass
    else:
        print("*/10 * * * * {0} {1}\n".format(sys.executable,__file__))
        print("请手动执行命令在定时器中增加上面内容->contab -e")
        init_cfg(0,"linux")
        pass
    return 1

if __name__=='__main__':
    main()
