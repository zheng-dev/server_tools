import flask
bp=flask.Blueprint('main',__name__)

@bp.route('/')
def home():
    return 'my home <hr>'

@bp.route('/info/<name>',methods=['get','post'])
def info(name):
    a:str=flask.request.args.get('name2',type=str)
    b:int=flask.request.form.get('name',type=int,default=0)
    html:str= f'<h1>file={name},a={a},b={b}</h1><img src="/static/room.png"/>'
    res: flask.Response=flask.make_response(html)
    return res

@bp.route('/upload',methods=['post'])
def up():
    file=flask.request.files.get('file')
    if file:
        fileName=file.filename
        #注意 1写权限2容量问题3重名覆盖
        file.save(f'./up/{fileName}')
        return 'success'
    return 'no_file'