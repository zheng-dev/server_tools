#
# coding=utf-8
#py3.12.5
#Auther:zhengzhichun [zheng6655@163.com]
#Date: 2024-08-29
#decription:监听指定jira中的帐号是不是分配了新的jira
import threading,time,logging
  
##浏览web
##Rets:(True成功|False错误,html)
def browser(url:str,data:dict[str,any],charset='utf8',method='GET',cookiefile='browser.cookie')->tuple[bool,str]:
    import urllib.parse,urllib.request,http.cookiejar,urllib.error
    header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    #'Accept-Encoding':'gzip, deflate',
    'Connection':'keep-alive',
    'Cache-Control':'max-age=0',
    'Upgrade-Insecure-Requests':'1'
    }
    cooks=http.cookiejar.MozillaCookieJar(filename=cookiefile)
    try:
        cooks.load(ignore_discard=True,ignore_expires=True)
    except:pass
        
    cook_hand=urllib.request.HTTPCookieProcessor(cooks)
    opener=urllib.request.build_opener(cook_hand)
    #
    data1:bytes =urllib.parse.urlencode(data)
    if method=='GET':
        req=urllib.request.Request(f'{url}?{data1}', None, header,method=method)
    else:
        req=urllib.request.Request(url, bytes(data1,encoding=charset), header,method=method)    
    #
    try:
        res=(True,opener.open(req).read().decode(charset))
    except urllib.error.HTTPError as e:
        res=(False,e.getcode)
    #更新cookies  
    cooks.save(ignore_discard=True,ignore_expires=False)
    logging.debug("url=%s ;data=%s",url,data1)
    return res
##
def test_b():
    print('start')
    r=browser('http://192.168.22.9/',{'name':9996},cookiefile=AppCfg.cook_file())
    print(r)
##字典cfg
# {"user":"xx","pwd":"xx","login":"xx/login.jsp","list":"xx/secure/views/bulkedit/BulkEdit1!default.jspa"} 
class AppCfg:
    def __get_dir()->str:
         import pathlib
         return str(pathlib.Path.home())
    def cook_file()->str:
        return AppCfg.__get_dir()+'/curlc.txt'
    def cfg_json()->dict:
        import json
        try:
            with open(AppCfg.__get_dir()+'/cfg.txt','r+',-1,'utf-8-sig') as f:
                    return json.load(f)
        except:
            return {}  
## 检查jira
class MyJira:
    _instance_lock = threading.Lock()
    oldJira:list[str]=[]
    __isLogin:bool=False
    ##
    def jira(self)->None|list[str]:
        cfg=AppCfg.cfg_json()
        #没登录就先登录 如果取jira失败就再登录
        uName=cfg['user']
        cookFile=AppCfg.cook_file()
        if self.__isLogin:
            p={'reset':'true','tempMax':30}
            (isOk,reponse)=browser(cfg['list'],p,'utf-8',cookiefile=cookFile)
            if isOk and  f'<meta name="ajs-remote-user" content="{uName}">' in reponse:
                return self._do_jira_check(reponse)
            else:
                self.__isLogin=False
                logging.warning("list err:%s",reponse)
        else:
            data = {'os_username':uName,'os_password':cfg['pwd']}
            (isOk,reponse)=browser(cfg['login'],data,'utf8',method='POST',cookiefile=cookFile)
            if not isOk:
                logging.warning("login err2:%s",reponse)
            elif f'<meta name="ajs-remote-user" content="{uName}">' in reponse:
                self.__isLogin=True
                #尝试登录成功后继续
                self.jira()    

    ##检查有没有新的        
    def _do_jira_check(self,html:str)->list[str]:
        import lxml.etree
        tree=lxml.etree.HTML(html)
        #'//td[@class="issuerow"]/p/a/@href'
        matchL:list[str] = tree.xpath('//tr[@class="issuerow"]/@data-issuekey')

        newL=[]
        old=self.oldJira
        for i in matchL:
            if i not in old:
                newL.append(i)

        self.oldJira=matchL#更新
        return newL
    ##
    def _save_html(self,html:str)->None:
        with open('t.htm','w+',encoding='utf-8') as f:
                f.write(html)
                import webbrowser
                webbrowser.open('t.htm')
    ##单例用
    def __new__(cls, *args, **kwargs):
        if not hasattr(MyJira, "_instance"):
            with MyJira._instance_lock:
                if not hasattr(MyJira, "_instance"):
                     MyJira._instance = object.__new__(cls)  
        return MyJira._instance
##     
def main_win():
    import tkinter
    logging.info("main_win")
    root=tkinter.Tk()
    root.title("jira")    # #窗口标题
    root.geometry("300x190+900+110")   # #窗口位置500后面是字母x
    root.lift()
    #root.attributes('-toppost',True)
    l1=tkinter.Text(root,height=20,width=38)
    l1.pack(side=tkinter.LEFT)
    yscrollbar = tkinter.Scrollbar(root)
    yscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    yscrollbar.config(command=l1.yview)
    l1.config(yscrollcommand=yscrollbar.set)

    jira=MyJira()
    def update():
        nonlocal jira,root,l1
        r=jira.jira()
        if r ==None:pass
        elif len(r)>0:
            tStr=time.strftime(f'==%m/%d %H:%M:%S num:{len(r)}==\n',time.localtime())
            l1.insert(1.0,tStr+('\n'.join(r))+'\n')
            root.deiconify()
        root.after(120000,update)
    root.after(10,update)

    # 双击隐藏
    def duble_click(event):
        nonlocal root
        root.withdraw()
    root.bind('<Double-Button-1>',duble_click)

    # 绑定全局快捷键
    BindKey().hook(['ctrl','q','0'],root.deiconify)

    root.mainloop()
    return

##组合键
import keyboard
class BindKey:
    __keys:list[str]=[]
    __onKeys:list[str]=[]
    __call=None

    def __on_key(self,event:keyboard.KeyboardEvent):
        if event.event_type=='up':
            self.__onKeys=[]
        elif event.name in self.__keys and event.event_type=='down':
            self.__onKeys.append(event.name)
            if self.__keys==self.__onKeys:
                self.__call()

    def hook(self,keys:list[str],callback):
        self.__call=callback
        self.__keys=keys
        keyboard.hook(self.__on_key) # 锁屏回来也生效
##
if __name__=='__main__':
   logging.getLogger().setLevel(logging.DEBUG)   
   test_b()
   #main_win()




# def main():
#     print("cpu=={}".format(multiprocessing.cpu_count()))
#     t=mThread(1,"t1",5)
#     t2=mThread(2,"t2",4)
#     t.start()
#     t2.start()
#     #time.sleep(30) 2
#     t.join()
#     t.join()
#     print("exit")
#     pass

# class mThread(threading.Thread):
#     def __init__(self, tId,name,delay) -> None:
#         threading.Thread.__init__(self)
#         self.name=name
#         self.threadId=tId
#         self.delay=delay

#     def run(self) -> None:
#         print("t-start{0}".format(self.name))    
#         self.pt(5)
#         print("t-end{0}".format(self.name))

#     def pt(self,num):
#         while num:
#             time.sleep(self.delay) 
#             print("==={0}=={1}\n".format(self.name,time.ctime(time.time())))
#             num-=1  