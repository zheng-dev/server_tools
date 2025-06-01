#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2024-09-19
# decription:

import sys
from typing import Callable,Any
from . import find, event, fight_a, d_line_cmd

enter_func=Callable[[list[str]],None]
"""入口函数 fun(list[str])->None"""
def main() -> None:
    help = """
从匹配的文件中查找内容，显示所在文件名和行数
py -m flog log/fight.l* {use_mill }      
显示指定文件的行数的内容
py -m flog -line xxxx.log 3     
调用日志分析事务                                               
py -m flog -fxa fight_analysis2.log
py -m flog -fxe event.txt
                           
             """
    sig_hand()
    input()
    if len(sys.argv) > 1:
        cmdL:dict[str,enter_func]={
        "-line":d_line_cmd,
        "-fxa":fight_a.AnalyseFALog.analyse,
        "-fxe":event.Event.analyse,
        }
        cmdL.get(sys.argv[1],find.Find.go)(sys.argv)
    else:
        print(help)


##捕获信号
def sig_hand():
    import signal

    def a1(_a:int, _:Any):
        print("ctr+c exit")
        sys.exit(0)

    signal.signal(signal.SIGINT, a1)


if __name__ == "__main__":
    main()
