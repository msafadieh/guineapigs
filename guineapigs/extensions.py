"""
    Extensions that add extra functions to Flask
"""
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
