#
# coding=utf-8
#py3.11
# 运行方式：python flog.py 
import os,shutil

import sys,glob,signal

def sig_hand(a,b):
    print("ctr+c exit")
    sys.exit(0)

def main():
   if len(sys.argv)>1:
       if sys.argv[1]=="-line":
           d_line()
           pass
       else:
           find()
   else:
       print('''
从匹配的文件中查找内容，显示所在文件名和行数
py -m flog log/fight.l* {use_mill }      
显示指定文件的行数的内容
py -m flog -line xxxx.log 3                                       
             ''')
   return
#检查
def find():
   files=glob.glob(sys.argv[1])   
   startStr= sys.argv[2]
   endStr=sys.argv[3]
   print(sys.argv[1],startStr,endStr,files)

   disNum=0
   for f in files:
       with open(f,'r',-1,'utf8') as fPtr:
           lineNum=0
           while fPtr:
            line=fPtr.readline()
            lineNum+=1
            if line=="":
                break
            i=line.find(startStr)

            if disNum==20:
                while True:
                    moreOrLine=input("more or line")
                    try:
                        LNum=int(moreOrLine.strip())
                        if LNum<=lineNum and LNum>0:
                            d_line_(f,LNum)
                        else:
                            break    
                    except:
                        break    
                disNum=0
            if i>-1:
                disNum+=1
                i2=line.find(endStr,i)
                print("{0}==>{1}-->{2}".format(line[i:i2+1],f,lineNum))
            pass

#显示行
def d_line():
    file=sys.argv[2]
    lineNumArg=int(sys.argv[3])
    d_line_(file,lineNumArg)
    return

def d_line_(file:str,lineNumArg:int):
    with open(file,'r',-1,'utf8') as fPtr:
        lineNum=0
        while fPtr:
            line=fPtr.readline()
            if line=="":
                break
            lineNum+=1
            if lineNum==lineNumArg:
                print(line)
                return 
    return

def analyse():
    (lineNum,condLineNum,kvList)=clear_data()

    print("总条数{0};100ms的条数{1}".format(lineNum,condLineNum))
    #print(kvList)  
    #print('事件mf | 总次数 | 100m的次数 | 平均用时 | 最大用时 | 原日志')
    save_ret(kvList)
    
    return
def save_ret(kvList:dict):
    import csv
    if {}!=dict:
        with open('event.csv','w+',-1,'utf-8-sig') as ePtr:
            writer=csv.writer(ePtr,quoting=csv.QUOTE_ALL,lineterminator="\n")
            writer.writerow(['事件mf','总次数','100m的次数','平均用时','最大用时','最大用时日志'])
            #writer.writerow(['事件mf | 总次数 | 100m的次数 | 平均用时 | 最大用时 | 原日志'])
            for key in kvList:
                oldTimes,old100Times,oldAccMs,oldMaxMs,oldLine=kvList.get(key)
                #事件mf,总次数（大于100MS)，总用时(大于100ms的)不用显示,平均用时，最大用时
                writer.writerow([key,oldTimes,old100Times,round(oldAccMs/oldTimes),oldMaxMs,oldLine.strip()])  
                #print("{0} | {1} | {5} | {2} | {3} | {4}".format(key,oldTimes,round(oldAccMs/oldTimes),oldMaxMs,oldLine.strip(),old100Times))    
    return        

##整理出数据
##ret:(lineNum,condLineNum,kvList)
def clear_data()->tuple[int, int, dict]:
    with open('event.txt','r',-1,'utf8') as fPtr:
        lineNum=0 #总条数
        condLineNum=0 #满足过虑条件行数
        kvList={} #结果
        pro=progress()
        while fPtr:
            pro.progress_no_sum(lineNum)
            line=fPtr.readline()
            if line=="":
                break
            lineNum+=1
            uSIndex=line.find('{use_ms,')
            if uSIndex>=0:
                uEIndex=line.find('}',uSIndex)
                useMs=int(line[uSIndex+8:uEIndex])
                if useMs<100:
                    continue #小于100ms的不统计

                #上面找到了使用时间
                #下面找事件mf
                mfSIndex=line.find('{',uEIndex)
                mfEIndex1=line.find(',',mfSIndex)
                mfEIndex2=line.find(',',mfEIndex1+1)
                mfStr=line[mfSIndex:mfEIndex2]+'}'

                oldRow=kvList.get(mfStr,0)
                #统一上100ms的
                reach100=0
                if useMs>100:
                    reach100=1

                if oldRow==0:
                    #(总次数,总用时ms,上100ms的总次数,单次最大用时ms,最大ms时的line)
                    kvList[mfStr]=(1,reach100,useMs,useMs,line)
                else:
                    oldTimes,old100Times,oldAccMs,oldMaxMs,oldLine=oldRow
                    if oldMaxMs<useMs:
                        oldMaxMs=useMs
                        oldLine=line
                    kvList[mfStr]=(1+oldTimes,old100Times+reach100,useMs+oldAccMs,oldMaxMs,oldLine)    

                #print("tttt{0}==={1}----{2}".format(useMs,mfStr,kvList))
                # if lineNum==2:
                #     break
            condLineNum+=1
    return (lineNum,condLineNum,kvList)         

##进度-有总量的
def progress(max:int,currIndex:int):
    #求10分之N
    rate=100
    curr=round(currIndex/max*rate)
    print("\r"+"#"*curr+"_"*(rate-curr),end="")

class progress:
    ##无总量的,每100数刷一下
    def progress_no_sum(self,currIndex:int):
        rate=10000
        if (currIndex % rate)==0:
            if ((currIndex)/rate %2)==0:
                f='/'
            else:
                f='\\'    
            print("\r\033[1;32m curr:{0}  {1}  \033[m ".format(currIndex,f),end="")

    def end(self):
        del self        
    ##进度完成
    def __del__(self):
    #     字色              背景              颜色
    # ---------------------------------------
    # 30                40              黑色
    # 31                41              紅色
    # 32                42              綠色
    # 33                43              黃色
    # 34                44              藍色
    # 35                45              紫紅色
    # 36                46              青藍色
    # 37                47              白色
        print("\033[1;37m \n=done=")

def test():
    import time
    
    print("\033[20A\033[?25l",end="")
    for i in range(60):
        time.sleep(1)
        print("\033[2J",end="")
        print("\033[31m 红色{0}字 \033[m".format(i))
##不用回车        
import tkinter
from tkinter import ttk
 
 
def xFunc1(event):
    print(f"事件触发键盘输入:{event.char},对应的ASCII码:{event.keycode}")
 
def win():
    win = tkinter.Tk()
    win.title("Kahn Software v1")    # #窗口标题
    win.geometry("600x500+200+20")   # #窗口位置500后面是字母x
    '''
    响应所有事件(键盘)
    <Key>   所有键盘按键会触发
    '''
    xLabel = tkinter.Label(win, text="KAHN Hello world")
    xLabel.focus_set()
    xLabel.pack()
    xLabel.bind("<Key>", xFunc1)
    
    win.mainloop()   # #窗口持久化

#win
def cmd():
    import msvcrt  
    print("按任意键继续...")  
    while True:  
        if msvcrt.kbhit():  # 检查是否有按键被按下  
            char = msvcrt.getch().decode()  # 读取按键并解码为字符  
            if char == '\r':  # 处理回车键  
                break  
            print("你按了:", char)
def shell():
        
    # 使用函数  
    char = get_single_char()  
    print(f"You pressed: {char}")
  
def get_single_char():  
        import sys  
        import tty  , termios  
        # 保存旧的终端设置  
        fd = sys.stdin.fileno()  
        old_settings = termios.tcgetattr(fd)  
    
        # 设置新终端设置：无回显，非阻塞  
        try:  
            tty.setraw(sys.stdin.fileno())  
            ch = sys.stdin.read(1)  
        finally:  
            # 恢复旧的终端设置  
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  
    
        return ch  


##
if __name__=='__main__':
    signal.signal(signal.SIGINT,sig_hand)
    #main()
    #analyse()
    #test()
    cmd()
    pass