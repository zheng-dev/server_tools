#
# coding=utf-8
#py3.11
# 运行方式：python f.py ../
import os,shutil

import sys


_GFindRet=[]#递归遍历目录时存path用
__GAME='game.iml'#文件

def main():
   if len(sys.argv)>1:
       dir=sys.argv[1]
   else:
       dir="."
    
   #检查目录   
   check_pro_dir()
   __find_dir("",dir)
   __after_find()
   return

def check_pro_dir()->None:
    if not os.path.isfile(__GAME):
        raise "pro_dir_err"
    return

#查找出头目录到全局变量中
def __find_dir(Prent:str,path:str)->None:
    os.chdir(path)
    isHrlDir=False
    for f in os.listdir("."):
        if os.path.isdir(f):
            __find_dir(Prent+path+"/",f)
        elif isHrlDir:
            continue
        else:
           if (os.path.splitext(f)[-1])==".hrl":
                isHrlDir=True
                global _GFindRet
                _GFindRet.append("{0}{1}".format(Prent,path))
        pass
    if Prent!="":
        os.chdir("../")
    return
#使用全局变量的目录结果生成文件
def __after_find():
    global _GFindRet

    # import xml.dom.minidom 
    # tree=xml.dom.minidom.parse(__GAME)
    # collection=tree.documentElement
    # if collection.hasAttribute("shelf"):
    #     print("root {0}".format(collection.getAttribute("shelf")))
    # ms=collection.getElementsByTagName("movie")
    # for m in ms:
    #     if m.hasAttribute('title'):
    #         print("has:{0}".format(m.getAttribute('title')))
    #     type=m.getElementsByTagName('type')[0]
    #     print("t:{0}".format(type.childNodes[0].data))    

    import xml.etree.ElementTree as et
    tree=et.parse(__GAME)
    p_root=tree.getroot()
    for m in p_root.findall('movie'):
        t=m.find('type').text
        year=m.find('format').text
        print("row:{0},{1}".format(t,year))    
    

    with open("hrl.txt",mode='w+') as f:
        for i in _GFindRet:
            f.write("<sourceFolder url=\"file://$MODULE_DIR$/plugin{0}\" type=\"erlang-include\" />\n".format(i[1:]))
            pass
        pass
    return

if __name__=='__main__':
    main()
