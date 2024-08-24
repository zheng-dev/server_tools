#
# import flask
# from werkzeug.datastructures.file_storage import FileStorage
# import werkzeug.serving

# app=flask.Flask(__name__)

# @app.before_request
# def b_req():
#     werkzeug.serving.WSGIRequestHandler.server_version='nginx'
#     werkzeug.serving.WSGIRequestHandler.sys_version='0.1.0'

# @app.route('/')
# def hello():
#     return 'hello,world <hr>333355'

# @app.route('/info/<name>',methods=['get','post'])
# def info(name):
#     a:str=flask.request.args.get('name2',type=str)
#     b:int=flask.request.form.get('name',type=int,default=0)
#     html:str= f'<h1>file={name},a={a},b={b}</h1><img src="/static/room.png"/>'
#     res: flask.Response=flask.make_response(html)
#     return res

# @app.route('/upload',methods=['post'])
# def up():
#     file: FileStorage | None=flask.request.files.get('file')
#     if file:
#         fileName=file.filename
#         #注意 1写权限2容量问题3重名覆盖
#         file.save(f'./up/{fileName}')
#         return 'success'
#     return 'no_file'


from waitress import serve
import app
if __name__=='__main__':
    app1=app.create_app()
    app1.static_folder='../static/'
    # app1.run(port=80)
    serve(app1,port=80)