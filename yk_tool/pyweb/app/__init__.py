import flask

def create_app()->flask.Flask:
    app:flask.Flask=flask.Flask(__name__)
    app.config.from_object('config')
    from . import routes
    app.register_blueprint(routes.bp)
    return app