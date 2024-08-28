#
# coding=utf-8
#py3.11

import threading,time,multiprocessing

import logging

def main():
    print("cpu=={}".format(multiprocessing.cpu_count()))
    t=mThread(1,"t1",5)
    t2=mThread(2,"t2",4)
    t.start()
    t2.start()
    #time.sleep(30)
    t.join()
    t.join()
    print("exit")
    pass

class mThread(threading.Thread):
    def __init__(self, tId,name,delay) -> None:
        threading.Thread.__init__(self)
        self.name=name
        self.threadId=tId
        self.delay=delay

    def run(self) -> None:
        print("t-start{0}".format(self.name))    
        self.pt(5)
        print("t-end{0}".format(self.name))

    def pt(self,num):
        while num:
            time.sleep(self.delay) 
            print("==={0}=={1}\n".format(self.name,time.ctime(time.time())))
            num-=1  

##字典cfg 
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
##浏览
def browser(url:str,data:dict[str,any],charset='utf8',method='GET')->str:
    import urllib.parse,urllib.request,http.cookiejar,urllib.error
    header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    #'Accept-Encoding':'gzip, deflate',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'Priority':'u=0, i'
    }
    cooks=http.cookiejar.MozillaCookieJar(filename=AppCfg.cook_file())
    try:
        cooks.load(ignore_discard=True,ignore_expires=True)
    except Exception as e:
        print(e.args)
        
    cook_hand=urllib.request.HTTPCookieProcessor(cooks)
    opener=urllib.request.build_opener(cook_hand)

    data1:bytes =urllib.parse.urlencode(data)
    if method=='GET':
        req=urllib.request.Request(f'{url}?{data1}', None, header,method=method)
    else:
        req=urllib.request.Request(url, bytes(data1,encoding=charset), header,method=method)    
    
    logging.debug("url=%s ;data=%s",url,data1)
    try:
        res=opener.open(req).read().decode(charset)
    except urllib.error.HTTPError as e:
        res=f"http_err:{e.getcode}"    
    #更新cookies  
    cooks.save(ignore_discard=True,ignore_expires=False)
    print(cooks)
    return res


## 检查jira
class MyJira:
    _instance_lock = threading.Lock()
    oldJira:list[str]=[]
    def jira(self)->None|list[str]:
        cfg=AppCfg.cfg_json()
        p={'reset':'true','tempMax':100}
        uName=cfg['user']
        reponse=browser(cfg['list'],p,'utf-8')
        if reponse[:9]=='http_err:':
            logging.warn("%s",reponse)
        elif f'<meta name="ajs-remote-user" content="{uName}">' in reponse:
            return self._do_jira_check(reponse)
        else:    
            data = {'os_username':uName,'os_password':cfg['pwd']}
            browser(cfg['login'],data,'utf8',method='POST')
            #尝试登录后继续
            self.jira()
    ##检查有没有新的        
    def _do_jira_check(self,html:str)->list[str]:
        import lxml.etree
        tree=lxml.etree.HTML(html)
        matchL:list[str] = tree.xpath('//td[@class="summary"]/p/a/@href')

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
def win_jira():
    import tkinter,tkinter.messagebox
    root=tkinter.Tk()
    root.title("jira")    # #窗口标题
    root.geometry("300x190+900+110")   # #窗口位置500后面是字母x
    root.lift()
    #root.attributes('-toppost',True)
    l1=tkinter.Label(root,text='',anchor='w')
    l1.pack()

    jira=MyJira()
    def update():
        nonlocal jira,root,l1
        r=jira.jira()
        if r ==None:pass
        elif len(r)>0:
            l1.configure(text='\n'.join(r))
            root.deiconify()
        root.after(15000,update)
    root.after(10,update)

    root.mainloop()
    return       

if __name__=='__main__':
   logging.getLogger().setLevel(logging.DEBUG)
   logging.info("Running maintenance as %s", 3)
   win_jira()
