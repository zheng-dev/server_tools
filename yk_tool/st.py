#
# coding=utf-8
#py3.11
# 运行方式：python st.py
import os,shutil

import sys



def main():
    #os.system("clear")
    current_path = os.path.dirname(__file__)
    os.chdir(current_path)
    a=False
    cA=[]
    cB=[]
    with open("a.txt",'r') as f:
        while f:
             line=f.readline()
             if line=="":
                    break
             elif line[:3]=="===":#A;B分组线c
                 a=True
             else:
                 if a:
                     cA.append(line.split()[4])
                 else:
                     cB.append(line.split()[4])    
                 pass
    old=0
    for i in cA:
        if i in cB:
            old+=1
            print("{}".format(i))
        # try:
        #     cB.index(i)
        #     old+=1
        #     print("{}".format(i))
        #     pass
        # except:
        #     pass
    all=len(cB)
    add=all-old
    print("新加{0},老的{1},总的{2}".format(add,old,len(cB)))
    return 0



if __name__=='__main__':
    main()
