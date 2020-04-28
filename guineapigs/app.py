from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from guineapigs.config import Config

def init_flask():
    global app, db, login_manager, nav

    app = Flask(__name__)
    app.config.from_object(Config)

    db = SQLAlchemy(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    Bootstrap(app)

init_flask()

from guineapigs import models, views

@login_manager.user_loader
def user_loader(user_id):
    return models.User.query.filter(models.User.id==user_id).first()
