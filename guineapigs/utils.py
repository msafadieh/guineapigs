from collections import OrderedDict
from datetime import datetime, timedelta
import pytz

def start_of_day_and_week(timezone):
    day_begin = datetime.now(pytz.timezone(timezone)).replace(hour=0,
                                                              minute=0,
                                                              second=0,
                                                              microsecond=0)
    week_begin = day_begin - timedelta(days=6)
    return day_begin, week_begin

def split_dates(entries):
    days = OrderedDict()

    for entry in entries:
        date = entry["time"].strftime("%A, %B %d").lower()
        days.setdefault(date, [])
        days[date].append(entry)

    return days

