#
# coding=utf-8
#py3.11
# 运行方式：python f.py ../
import os,shutil

import sys


_GFindRet=[]#递归遍历目录时存path用

def main():
   if len(sys.argv)>1:
       dir=sys.argv[1]
   else:
       dir="."

   _find_dir("",dir)
   _after_find()
   return

#查找出头目录到全局变量中
def _find_dir(Prent:str,path:str)->None:
    os.chdir(path)
    isHrlDir=False
    for f in os.listdir("."):
        if os.path.isdir(f):
            _find_dir(Prent+path+"/",f)
        elif isHrlDir:
            continue
        else:
           if (os.path.splitext(f)[-1])==".hrl":
                isHrlDir=True
                global _GFindRet
                _GFindRet.append("{0}{1}".format(Prent,path))
        pass
    os.chdir("../")
    return
#使用全局变量的目录结果生成文件
def _after_find():
    global _GFindRet
    with open("hrl.txt",'w+') as f:
        for i in _GFindRet:
            f.write("<sourceFolder url=\"file://$MODULE_DIR$/plugin{0}\" type=\"erlang-include\" />\n".format(i[1:]))
            pass
        pass
    return

if __name__=='__main__':
    main()
