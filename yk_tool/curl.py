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
    
    logging.debug("req=%s==%s",url,data1)
    try:
        res=opener.open(req).read().decode(charset)
    except urllib.error.HTTPError as e:
        res=f"http_err:{e.getcode}"    
    #更新cookies  
    cooks.save(ignore_discard=True,ignore_expires=False)
    print(cooks)
    return res


def test_curl():
    cfg=AppCfg.cfg_json()
    uName=cfg['user']
    data = {'os_username':uName,'os_password':cfg['pwd']}
    
    r=browser(cfg['login'],data,'utf8',method='POST')
    if f'<meta name="ajs-remote-user" content="{uName}">' in r:
        reponse=browser(cfg['list'],{'selectPageId':'11706'},'utf8')
        with open('t.htm','w+',encoding='utf-8') as f:
            f.write(reponse)
            import webbrowser
            webbrowser.open('t.htm')
    return       

def loop():
    cfg=AppCfg.cfg_json()
    p={'filter':'-1'}
    reponse=browser(cfg['list'],p,'utf-8')
    if reponse[:9]=='http_err:':
        logging.info("%s",reponse)
    else:    
        with open('t.htm','w+',encoding='utf-8') as f:
            f.write(reponse)
            import webbrowser
            webbrowser.open('t.htm')

if __name__=='__main__':
   logging.getLogger().setLevel(logging.DEBUG)
   logging.getLogger("requests").setLevel(logging.INFO)
   logging.info("Running maintenance as %s", 3)
   #p={'name2':'-1'}
   #reponse=browser('http://koo66.iok.la/',p,'utf-8')
   #test_curl()
   loop()
