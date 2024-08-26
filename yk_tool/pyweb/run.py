import app
from waitress import serve
import logging

if __name__=='__main__':
    # 配置日志记录-大小？日志切片？
    logging.basicConfig(filename='waitress.log', level=logging.ERROR)
    app1=app.create_app('./')
    #app1.run(host='192.168.22.9',port=80)
    serve(app1,port=80,threads=4,host='192.168.22.9',ident='nginx 1.0.0',log_socket_errors=True)