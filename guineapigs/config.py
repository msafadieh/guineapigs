"""
    loads configuration variables and default ones
"""
import os
import pytz


class Config:
    """
        Flask config class
    """

    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS", False
    )
    TIMEZONE = pytz.timezone(os.environ.get("TIMEZONE", "America/New_York"))
    TITLE = os.environ.get("TITLE", "Guinea pigs")
    REMEMBER_COOKIE_DURATION = os.environ.get(
        "REMEMBER_COOKIE_DURATION365", 365 * 24 * 60 * 60
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "super secret")
