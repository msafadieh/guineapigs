from datetime import datetime
import pytz
from guineapigs.app import app

def beginning_of_day_utc():
    return (datetime.now()
                    .astimezone(app.config["TIMEZONE"])
                    .replace(hour=0, minute=0, second=0, microsecond=0)
                    .astimezone(pytz.utc)
            )