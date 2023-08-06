from .croniter import croniter
from .Logging import log, LogLevel


def get_croniter(schedule, date):
    cron_iter = None
    try:
        cron_iter = croniter(schedule, date)
    except Exception as e:
        log(LogLevel.ERROR, f'croniter error: {e}')
    return cron_iter
