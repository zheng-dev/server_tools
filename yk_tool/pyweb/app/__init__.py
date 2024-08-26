import flask,logging

LOG_NAME='weblog'

def create_app(root)->flask.Flask:
    app:flask.Flask=flask.Flask(__name__)
    logger=logging.getLogger(LOG_NAME)
    app.config.from_object('config')
    app.root_path=root
    from . import routes
    routes.bp.root_path=root
    app.register_blueprint(routes.bp)    
    logger.info('app start ok==')
    @app.errorhandler(Exception)
    def err(err):
        # print(err) #注意打印量
        #logger.warn(err)
        return f'nginx {500}<hr/>',500
    return app

