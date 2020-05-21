"""
    where all the magic starts
"""
from flask import Flask
from guineapigs import private, public
from guineapigs.config import Config
from guineapigs.extensions import bootstrap, db, login_manager, migrate
from guineapigs.utils import strftime


def init_flask():
    """
    Initializes Flask flask_app with and registers extentions, blueprints,
    and utils
    """
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)
    register_extensions(flask_app)
    register_blueprints(flask_app)
    register_utils(flask_app)
    return flask_app


def register_extensions(flask_app):
    """
    Registers app extensions
    """
    bootstrap.init_app(flask_app)
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)


def register_blueprints(flask_app):
    """
    Registers app blueprints
    """
    flask_app.register_blueprint(public.views.blueprint)
    flask_app.register_blueprint(private.views.blueprint)


def register_utils(flask_app):
    """
    Registers functions for access in templates
    """
    flask_app.context_processor(lambda: {"strftime": strftime})


app = init_flask()
