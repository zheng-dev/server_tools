#
# coding=utf-8
#py3.12.5
#Auther:zhengzhichun [zheng6655@163.com]
#Date: 2024-08-29
#decription:比较a,b两个文件段,分析出b新加了哪些,老的是哪些
import os,sys

def main():
    current_path = os.path.dirname(__file__)
    os.chdir(current_path)
    a=False
    cA={}
    cB={}
    with open("a.txt",'r') as f:
        while f:
             line=f.readline()
             if line=="":
                    break
             elif line[:3]=="===":#A;B分组线c
                 a=True
             else:
                 r=line.split(',')
                 if a:
                     cA[r[2][:-2]]=r[1]
                 else:
                     cB[r[2][:-2]]=r[1]  
                 pass
    old=0
    for i in cA:
        try:
            if cB[i]!=cA[i]:
                print(f"{i}->old={cA[i]},n={cB[i]}")
        except:
            print(f"{i}only old{cA[i]}")    

    # all=len(cB)
    # add=all-old
    # print("新加{0},老的{1},总的{2}".format(add,old,len(cB)))
    return 0

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

if __name__=='__main__':
    main()
