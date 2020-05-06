"""
    utitlities to make work easier
"""
from datetime import datetime, time, timedelta
from urllib.parse import urlparse, urljoin
import pytz
from guineapigs.app import app


def beginning_of_day_utc():
    """
    returns the timestamp for the beginning
    of current day in configured timezone
    """
    return (
        datetime.now()
        .astimezone(app.config["TIMEZONE"])
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone(pytz.utc)
        .replace(tzinfo=None)
    )


def date_to_datetime(date):
    return datetime.combine(date, time())


def beginning_of_week_utc():
    """
    same as beginning_of_day_utc but subtracts 6 days
    """
    return beginning_of_day_utc() - timedelta(days=6)


def next_day(date):
    """
    adds one day to datetime object
    """
    return date + timedelta(days=1)


def strftime(datetime_instance, str_format):
    """
    converts to correct timezone and then formats
    """
    return (
        datetime_instance.replace(tzinfo=pytz.utc)
        .astimezone(app.config["TIMEZONE"])
        .strftime(str_format)
    )


def is_safe_url(target, host_url):
    """
    checks target URL is safe to redirect to
    """
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc
