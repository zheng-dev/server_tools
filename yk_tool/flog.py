#
# coding=utf-8
#py3.11
# 运行方式：python flog.py 
import os,shutil
import sys

def main():
   sig_hand()
   if len(sys.argv)>1:
       if sys.argv[1]=="-line":
           d_line()
       elif sys.argv[1]=="-fx":
           analyse()    
       else:
           Find().find()
   else:
       print(os.get_terminal_size())
       print('''
从匹配的文件中查找内容，显示所在文件名和行数
py -m flog log/fight.l* {use_mill }      
显示指定文件的行数的内容
py -m flog -line xxxx.log 3     
调用日志分析事务                                               
py -m flog -fx              
             ''')
   return
#检查
class Find:
    retList=[]
    allPage=0#总页数
    currPage=1#当前页码
    rowNum4Page=20#每页显示条数
    page=[]#当前页内容
    def find(self):
        import glob,time
        files=glob.glob(sys.argv[1])   
        startStr= sys.argv[2]
        endStr=sys.argv[3]
        print(sys.argv[1],startStr,endStr,files)
        c,row=os.get_terminal_size()
        self.rowNum4Page=row-4
        #整理出结果[(sortField,findStr，file,lineNum)]
        pro=Progress()
        for f in files:
            with open(f,'r',-1,'utf8') as fPtr:
                lineNum=0
                while fPtr:
                    line=fPtr.readline()
                    lineNum+=1
                    if line=="":
                        break
                    if line.find('fight_mode => 4')>-1:
                        i=line.find(startStr)
                        if i>-1:
                            i2=line.find(endStr,i)
                            if i2>-1:
                                txt=line[i:i2+1]    
                                self.retList.append((len(txt),txt,f,lineNum))
                    pro.progress_no_sum()        
        del pro
        #显示
        try:
            self.retList.sort(reverse=True)
        except:
            pass
        print(f"sort:{time.time()}")
        #print(self.retList) 
        self.display() if self.calc_page() else print("no match")

    #计算页码       
    def calc_page(self):
        if len(self.retList)<1:
            self.currPage=0
            return False
        else:
            p=int(len(self.retList)/self.rowNum4Page)
            self.allPage=p if len(self.retList) % self.rowNum4Page ==0 else p+1 
            return True
    #逐页显示
    def display(self):
        if self.currPage<=self.allPage:
            pass
        elif self.currPage>self.allPage: 
            self.currPage=self.allPage
        else:
            self.currPage=1

        self.page=self.retList[(self.currPage-1)*self.rowNum4Page:self.currPage*self.rowNum4Page]
        i=1
        for (sort,findStr,file,lineNum) in self.page:
            print(f"{i}:{findStr}-->{file}:{lineNum}")
            i+=1
        print(f"页码{self.currPage}/{self.allPage} 每页{self.rowNum4Page}条")
        #用户操作
        self.cmd()

    def cmd(self):
        cmd=input("下一页(n);前一页(b);反排序(r);显示指定原内容(d 条目id);退出(q):")
        cmd2=cmd.strip()
        if cmd2[:1]=='b' and self.currPage>1:
            try:
                line=int(cmd2[2:])
            except:
                line=1
                pass    
            self.currPage-=line
            self.display()
        elif ( cmd2=='' or cmd2[:1]=='n') and self.currPage<self.allPage:
            try:
                line=int(cmd2[2:])
            except:
                line=1
                pass    
            self.currPage+=line
            self.display()
        elif cmd2=='r':
            self.retList.reverse()
            self.display()
        elif cmd2=='q':
            pass        
        elif cmd2[:2]== 'd ':
            try:
                line=int(cmd2[2:])
                if line>=1 and line<=self.rowNum4Page:
                    (sortF,findStr,file,lineNum)=self.page[line-1]
                    d_line_(file,lineNum)
                    self.cmd()
                else:
                    raise("error")
            except:
                print(f"输入无效:{cmd2}")
                self.cmd()    
        else:
            print(f"输入无效:{cmd2}") 
            self.cmd()    

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
    save_ret(kvList)
    return
##结果存入csv
def save_ret(kvList:dict):
    import csv
    if {}!=dict:
        with open('event.csv','w+',-1,'utf-8-sig') as ePtr:
            writer=csv.writer(ePtr,quoting=csv.QUOTE_ALL,lineterminator="\n")
            writer.writerow(['事件mf','总次数','100m的次数','平均用时','最大用时','最大用时日志'])
            #writer.writerow(['事件mf | 总次数 | 100m的次数 | 平均用时 | 最大用时 | 原日志'])
            for key in kvList:
                oldTimes,old100Times,oldAccMs,oldMaxMs,oldLine=kvList.get(key)
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
        pro=Progress()
        while fPtr:
            pro.progress_no_sum()
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
                reach100=0 if useMs>100 else 1

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

class Progress:
    currIndex=0
    max=0
    __rate=0
    __sTime=0

    def __init__(self,max1:int=None,rate=10000) -> None:
        import time
        self.__rate=rate
        self.max=max1
        self.__sTime=time.time()
        pass

    ##进度-有总量的
    def Progress(self):
        curr=round(self.currIndex/self.max*self.__rate)
        print("\r"+"#"*curr+"_"*(self.__rate-curr),end="")
    ##无总量的,每100数刷一下
    def progress_no_sum(self,rate:int=10000):
        self.currIndex+=1
        if (self.currIndex % rate)==0:
            f='/' if ((self.currIndex)/rate %2)==0 else '\\'    
            print("\r\033[1;32m curr:{0}  {1}  \033[m ".format(self.currIndex,f),end="")
    ##进度完成 可手动del
    def __del__(self):
        import time
        __eTime=time.time()
    #前景：黑色30紅色31綠色32黃色33藍色34紫紅色35青藍色36白色37
    #背景：在前景值 基础上+10
        print(f"\033[1;37m \n =done={self.currIndex} use {int(__eTime)-int(self.__sTime)} second")

def test():
    print("\033[20A\033[?25l",end="")
    for i in range(60):
        s=get_single_char()
        print("\033[2J",end="")
        print("\033[31m 红色{0}{1}字 \033[m".format(i,s))

##不用回车的单次输入
def get_single_char():
    if sys.platform=='win32':
        return w__get_single_char()
    else:
        return l_get_single_char()  
def w__get_single_char():
    import msvcrt
    return msvcrt.getch().decode()
def l_get_single_char():  
    import sys,tty,termios  
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

##捕获信号
def sig_hand():
    import signal
    def a1(a,b):
            print("ctr+c exit")
            sys.exit(0) 
    signal.signal(signal.SIGINT,a1)
    
##
if __name__=='__main__':    
    main()
    #test()
    pass