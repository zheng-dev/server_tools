#
# coding=utf-8
#py3.12.5
#Auther:zhengzhichun [zheng6655@163.com]
#Date: 2024-08-29
#decription:web的启动入口
import logging.handlers
import logging,config

import app
from waitress import serve


if __name__=='__main__':
    # 配置日志记录-
    #logger=logging.getLogger(app.LOG_NAME) #不用get,直接全局
    #logging.setLevel(level=logging.DEBUG)

    #设置日志格式
    fmt = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    format_str = logging.Formatter(fmt)

    #循环日志 大小,日志切片
    hand=logging.handlers.RotatingFileHandler('1waitress.log',maxBytes=10240,backupCount=3,encoding='utf-8')
    hand.setFormatter(format_str)
    #日志文件名
    hand.namer=lambda x:f'{x.split('.')[-1]}waitress.log'
    logging.basicConfig(level=logging.DEBUG,handlers=[hand])
    #logging.addHandler(hand)

    app1=app.create_app('./')
    #app1.run(host='192.168.22.9',port=80)
    serve(app1,port=80,threads=4,host='192.168.22.9',ident='nginx 1.0.0')