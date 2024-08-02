#
# coding=utf-8
#py3.11
# 运行方式：python f.py ../
import os,shutil,sys

GAME='game.iml'#文件

# def main():
#    if len(sys.argv)>1:
#        dir=sys.argv[1]
#    else:
#        dir="."
#    FindHrlDir.go(dir)

#    return

class FindHrlDir:
    _GFindRet=[]#递归遍历目录时存path用
    def go(dir):
        os.chdir(dir)
        a=FindHrlDir()
        os.chdir('plugin')
        a._find_dir("","./")
        os.chdir('../')
        a._after_find()

    def __init__(self) -> None:
        #检查目录是否是idea项目
        if not os.path.isfile(GAME):
            raise Exception("pro_dir_err")
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

class AppCfg:
    last_dir=""
    data={}

    def go():
        import pathlib
        print(pathlib.Path.home())
        a=AppCfg()
        return a
    def serialize(self):  
         # 使用instance的__dict__属性来获取实例的所有属性  
         return {key: value for key, value in self.__dict__.items()}  
    def __get_cfg(self):
        import pathlib
        return str(pathlib.Path.home())+'/.find_hrl_dir.cfg'
    
    def __init__(self) -> None:
        import json
        with open(self.__get_cfg(),'r+',-1,'utf-8-sig') as f:
            try:
                r=json.load(f)
                self.last_dir=r['last_dir']
            except:
                self.last_dir=os.path.dirname(__file__)    
        pass
    def save(self):
        import json
        with open(self.__get_cfg(),'w+',-1,'utf-8-sig') as f:
            data=self.serialize()#{'last_dir':self.last_dir}
            json.dump(data,f)
    def __del__(self):
        self.save()
        pass

def win():
    import tkinter,tkinter.messagebox
    win = tkinter.Tk()
    win.title("iml-hrl目录增加")    # #窗口标题
    win.geometry("300x90+900+110")   # #窗口位置500后面是字母x

    

    l1=tkinter.Label(win,text='项目路径')
    l1.pack()
    dir=tkinter.Entry(win,width=40)
    
    dir.cfg=AppCfg.go()
    dir.insert(0,dir.cfg.last_dir)
    dir.pack()
    dir.focus_set()
    def goBack():
        pathStr=dir.get()
        print(f"=={pathStr}")
        global cfg
        try:
            #__test_xml()
            dir.cfg.last_dir=pathStr
            FindHrlDir.go(pathStr)
            dir.cfg.save()
            tkinter.messagebox.showinfo("成功","生成完毕")
        except OSError as a:
            tkinter.messagebox.showinfo("err","文件错误信息:\n{0}\n{1}".format(a.strerror,a.filename))
        except Exception as a:
            tkinter.messagebox.showinfo("err","错误信息:\n{0}".format(a.args))
                    
    go=tkinter.Button(win,text="  go  ",command=goBack)
    go.pack()

    
    # xLabel = tkinter.Label(master=win, text="KAHN Hello world")
    # xLabel.focus_set()
    # xLabel.pack()
    # def xFunc1(event):
    #     print(f"事件触发键盘输入:{event.char},对应的ASCII码:{event.keycode}")
    # xLabel.bind("<Key>", xFunc1)
    
    win.mainloop()   # #窗口持久化

if __name__=='__main__':
    #main()
    win()
    
    pass
