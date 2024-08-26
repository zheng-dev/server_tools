import flask,logging

bp=flask.Blueprint('main',__name__)

@bp.route('/')
def home():
    return flask.render_template('index.html',title='Welcome Page', name='fish')

svrEtag:str=''
@bp.route('/favicon.ico')
def favicon():
    import os
    etag:str=flask.request.headers.get('If-None-Match','no').strip('"')
    global svrEtag
    if etag==svrEtag:
        logging.debug('etag ok {0},{1}'.format(etag,svrEtag))
        return '',304
    txt=flask.send_from_directory('static','favicon.ico', mimetype='image/vnd.microsoft.icon')
    response = flask.make_response(txt)
    #response.cache_control.max_age = 3600  # 设置缓存时间为1小时
    nEtag,isWeek=response.get_etag()
    svrEtag=nEtag

    logging.debug('etag no {0},{1},{2}'.format(etag,nEtag,svrEtag))
    
    return response

@bp.route('/info/<name>',methods=['get','post'])
def info(name):
    logging.debug('info access')
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