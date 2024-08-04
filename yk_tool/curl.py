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


def test_curl():
    return       


if __name__=='__main__':
    test_curl()
