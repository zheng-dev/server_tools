#
# coding=utf-8
#py3.11
# 运行方式：python f.py ../
import os,shutil

import sys


_G_find_ret=[]#遍历目录时存path用

def main():
   """安装或执行清理"""
   if len(sys.argv)>1:
       dir=sys.argv[1]
   else:
       dir="."

   find_dir("",dir)
   global _G_find_ret
   with open("hrl.txt",'w+') as f:
       for i in _G_find_ret:
           f.write("<sourceFolder url=\"file://$MODULE_DIR$/plugin{0}\" type=\"erlang-include\" />\n".format(i[1:]))
           pass
       pass
   return


def find_dir(Prent:str,path:str)->None:
    os.chdir(path)
    isHrlDir=False
    for f in os.listdir("."):
        if os.path.isdir(f):
            find_dir(Prent+path+"/",f)
        elif isHrlDir:
            continue
        else:
           if (os.path.splitext(f)[-1])==".hrl":
                isHrlDir=True
                global _G_find_ret
                _G_find_ret.append("{0}{1}".format(Prent,path))
        pass
    os.chdir("../")
    return




main()
