import datetime

def getNowUTCTime() -> datetime.datetime:
    # datetime.now() and even datetime.utcnow() return timezone naive datetimes, that is to say datetimes with no timezone information associated.
    # To get a timezone aware datetime, you need to pass a timezone as an argument to datetime.now
    return datetime.datetime.now(datetime.timezone.utc)

def getDateIsoString(time: datetime.datetime) -> str:
    # "+00:00" is a valid ISO 8601 timezone designation for UTC.
    # If you want to have "Z" instead of "+00:00", you have to do the replacement yourself
    return time.isoformat().replace("+00:00", "Z")
