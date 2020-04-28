import os
import pytz

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    TIMEZONE = pytz.timezone(os.environ.get("TIMEZONE", "America/New_York"))
    TITLE = os.environ.get("TITLE", "Guinea pigs")
    SECRET_KEY = "super secret"
