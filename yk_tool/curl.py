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

def test_curl():
    import urllib.parse,urllib.request,http.cookiejar
    header = {
    'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    cook_jar=http.cookiejar.MozillaCookieJar(filename='.curlc')
    cook_hand=urllib.request.HTTPCookieProcessor(cook_jar)
    opener=urllib.request.build_opener(cook_hand)

    cfg=cfg_json()
    uName=cfg['user']
    data = urllib.parse.urlencode({'os_username':uName,'os_password':cfg['pwd']}).encode('utf8') 
    login_request=urllib.request.Request(cfg['login'], data, header,method='POST')   
    r=opener.open(login_request).read().decode('utf-8')


    if f'<meta name="ajs-remote-user" content="{uName}">' in r:
        cook_jar.save(ignore_discard=True,ignore_expires=True)
        print(cook_jar)
        url2=cfg['list']
        data2 = urllib.parse.urlencode({'selectPageId':'11706'}).encode('utf8') 
        c_r=urllib.request.Request(url2,data2,header)
        reponse=opener.open(c_r).read()
        print(cook_jar)

        with open('t.htm','w+',encoding='utf-8') as f:
            f.write(reponse.decode('utf-8'))
            import webbrowser
            webbrowser.open('t.htm')
        return       

def loop():
    import urllib.parse,urllib.request,http.cookiejar
    header = {
    'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        cook_jar=http.cookiejar.MozillaCookieJar()
        cook_jar.load(filename='.curlc',ignore_discard=True,ignore_expires=True)
    except Exception as e:
        print('err',e.args)
        cook_jar=http.cookiejar.MozillaCookieJar(filename='.curlc')
    cook_hand=urllib.request.HTTPCookieProcessor(cook_jar)
    opener=urllib.request.build_opener(cook_hand)

    cfg=cfg_json()
    data2 = urllib.parse.urlencode({'selectPageId':'11706'}).encode('utf8') 
    c_r=urllib.request.Request(cfg['list'],data2,header)
    reponse=opener.open(c_r).read()

    with open('t.htm','w+',encoding='utf-8') as f:
        f.write(reponse.decode('utf-8'))
        import webbrowser
        webbrowser.open('t.htm')

if __name__=='__main__':
   # test_curl()
   loop()
