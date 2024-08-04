#
# coding=utf-8
#py3.11

import threading,time,multiprocessing

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
def cfg_json()->dict:
    import json
    try:
        with open('cfg.txt','r+',-1,'utf-8-sig') as f:
                return json.load(f)
    except:
        return {}    
##浏览
def browser(url:str,data:dict,charset='utf8',method='GET')->str:
    import urllib.parse,urllib.request,http.cookiejar
    header = {
    'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    cooks=http.cookiejar.MozillaCookieJar(filename='.curlc')
    try:
        cooks.load(ignore_discard=True,ignore_expires=True)
    except Exception as e:
        print(e.args)
        
    cook_hand=urllib.request.HTTPCookieProcessor(cooks)
    opener=urllib.request.build_opener(cook_hand)

    data = urllib.parse.urlencode(data).encode(charset)
    req=urllib.request.Request(url, data, header,method=method)
    res=opener.open(req).read().decode(charset)
    #更新cookies  
    cooks.save(ignore_discard=True,ignore_expires=False)
    print(cooks)
    return res


def test_curl():
    cfg=cfg_json()
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
    cfg=cfg_json()
    reponse=browser(cfg['list'],{'filter=':'-1'},'utf8')
    with open('t.htm','w+',encoding='utf-8') as f:
        f.write(reponse)
        import webbrowser
        webbrowser.open('t.htm')

if __name__=='__main__':
   #test_curl()
   loop()
