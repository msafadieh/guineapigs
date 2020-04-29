"""
    utitlities to make work easier
"""
from datetime import datetime
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


def is_safe_url(target):
    """
    checks target URL is safe to redirect to
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc
