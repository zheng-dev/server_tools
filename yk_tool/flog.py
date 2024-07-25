#
# coding=utf-8
#py3.11
# 运行方式：python flog.py 
import os,shutil

import sys,glob

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

   for f in files:
       with open(f,'r+',-1,'utf8') as fPtr:
           lineNum=0
           while fPtr:
            line=fPtr.readline()
            lineNum+=1
            if line=="":
                break
            i=line.find(startStr)
            if i>-1:
                i2=line.find(endStr,i)
                print("{0}==>{1}-->{2}".format(line[i:i2+1],f,lineNum))
            pass

#显示行
def d_line():
    file=sys.argv[2]
    lineNumArg=int(sys.argv[3])
    with open(file,'r+',-1,'utf8') as fPtr:
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

if __name__=='__main__':
    main()
    pass