#
# coding=utf-8
#py3.11
# 运行方式：python f.py ../
import os,shutil

import sys



GAME='game.iml'#文件

def main():
   if len(sys.argv)>1:
       dir=sys.argv[1]
   else:
       dir="."
   FindHrlDir.go(dir)

   return

class FindHrlDir:
    _GFindRet=[]#递归遍历目录时存path用
    def go(dir):
        a=FindHrlDir()
        os.chdir('plugin')
        a._find_dir("",dir)
        os.chdir('../')
        a._after_find()

    def __init__(self) -> None:
        #检查目录是否是idea项目
        if not os.path.isfile(GAME):
            raise "pro_dir_err"
        pass
    #查找出头目录到全局变量中
    def _find_dir(self,Prent:str,path:str)->None:
        os.chdir(path)
        isHrlDir=False
        for f in os.listdir("."):
            if os.path.isdir(f):
                self._find_dir(Prent+path+"/",f)
            elif isHrlDir:
                continue
            else:
                if (os.path.splitext(f)[-1])==".hrl":
                        isHrlDir=True
                        self._GFindRet.append("{0}{1}".format(Prent,path))
                pass
        if Prent!="":
            os.chdir("../")
        return
    #使用全局变量的目录结果生成文件
    def _after_find(self):
        with open("hrl.txt",mode='w+') as f:
            for i in self._GFindRet:
                f.write("<sourceFolder url=\"file://$MODULE_DIR$/plugin{0}\" type=\"erlang-include\" />\n".format(i[1:]))
                pass
            pass
        return

def __test_xml():
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
    tree=et.parse(GAME)
    p_root=tree.getroot()
    # for m in p_root.findall('movie'):
    #     t=m.find('type').text
    #     year=m.find('format').text
    #     print("row:{0},{1}".format(t,year))    
    
    m=p_root.find('component')
    print(m)
    test=et.SubElement(m,"test",{'cc':'2024','e':'07'},z='hello',z2='2')
    test.text='33'
    test.attrib['bb']='c'
    tree.write('aa.iml',"UTF-8",True,None,'xml')

if __name__=='__main__':
    #main()
    __test_xml()
    pass
