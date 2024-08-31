#
# coding=utf-8
#py3.12.5
#Auther:zhengzhichun [zheng6655@163.com]
#Date: 2024-08-29
#decription:路由相关
import flask,logging

bp=flask.Blueprint('main',__name__)

@bp.route('/',methods=['get'])
def home():
    u=flask.request.cookies.get('u')
    a:str=flask.request.args.get('name',type=str)
    html=flask.render_template('index.html',title='Welcome Page', name=a,u=u)
    resp=flask.make_response(html)
    resp.set_cookie('u','abcde')
    return resp

svrEtag:dict[str,str]={}
@bp.route('/<filename>.<exe>')
def favicon(filename,exe):
    import os
    etag:str=flask.request.headers.get('If-None-Match','no').strip('"')
    file:str=f'{filename}.{exe}'
    global svrEtag
    if etag!='no' and etag==svrEtag.get(file,''):
        logging.debug('etag ok {0},{1}'.format(etag,svrEtag))
        return '',304
    #bin=flask.send_from_directory('static','favicon.ico', mimetype='image/vnd.microsoft.icon')
    response=flask.send_from_directory('static',file)
    #response = flask.make_response(res1)
    response.cache_control.max_age = 3600  # 设置缓存时间为1小时
    nEtag,isWeek=response.get_etag()
    svrEtag[file]=nEtag

    logging.debug('etag no {3},{0},{1},{2}'.format(etag,nEtag,svrEtag,file))
    return response

@bp.route('/db/<op>/<name>',methods=['get','post'])
def info(op:str,name:str):
    from . import models,db
    dbRet:dict[str,str]={}
    if op=='get':
         user:models.User = models.User.query.get(name)
         dbRet={user.username:user.username}
    elif op=='all':
         users:list[models.User] = models.User.query.all()  # 获取所有用户
         for user in users:
             dbRet[user.username]=user.email 
    else:
        a:str=flask.request.args.get('name2',type=str)
        b:int=flask.request.form.get('name',type=int,default=0)
        new_user = models.User(username=name, email=f'{name}@example.com')
        dbRet={'ret':'ok'}
        db.session.add(new_user)
        db.session.commit()
    res=flask.jsonify(dbRet)
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