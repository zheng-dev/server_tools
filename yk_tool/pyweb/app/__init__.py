import flask

def create_app(root)->flask.Flask:
    app:flask.Flask=flask.Flask(__name__)
    app.config.from_object('config')
    app.root_path=root
    from . import routes
    routes.bp.root_path=root
    app.register_blueprint(routes.bp)    
    return app