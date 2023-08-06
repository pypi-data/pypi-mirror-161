from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone


def getUtcDate(date: datetime) -> datetime:
    utc = timezone('UTC')
    tz = get_localzone()  # local timezone
    local_date = date.replace(tzinfo=tz)
    utc_date = local_date.astimezone(utc)
    return utc_date
