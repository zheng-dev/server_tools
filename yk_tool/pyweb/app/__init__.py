#
# coding=utf-8
#py3.12.5
#Auther:zhengzhichun [zheng6655@163.com]
#Date: 2024-08-29
#decription:创建app及初始,包括db的orm
import flask,logging
from flask_sqlalchemy import SQLAlchemy
db:SQLAlchemy=None
def create_app(root)->flask.Flask:
    app:flask.Flask=flask.Flask(__name__)
    app.config.from_object('config')
    app.root_path=root
    global db
    db=SQLAlchemy(app)

    
    from . import routes
    
    routes.bp.root_path=root
    routes.bp.static_url_path='/'
    app.register_blueprint(routes.bp)    

    with app.app_context():
        from . import models
        db.create_all()
        #models.add_column_to_table("user", "address", db.String(120))
        logging.info('db ok===')

    logging.info('app start ok==')

    @app.errorhandler(404)
    def err404(error):
        return  f'nginx 1.0.0 {404}<hr/>',404

    @app.errorhandler(Exception)
    def err_e(err):
        logging.warn(err)
        return f'nginx {500}<hr/>',500
    
    return app

