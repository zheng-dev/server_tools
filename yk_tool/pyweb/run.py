import app
from waitress import serve
import logging

if __name__=='__main__':
    # 配置日志记录
    logging.basicConfig(filename='waitress.log', level=logging.INFO)
    app1=app.create_app()
    app1.static_folder='../static/'
    # app1.run(port=80)
    serve(app1,port=80,threads=4)