from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone as get_tz
from dateutil.parser import parse


def get_utc_date(date):
    utc = timezone('UTC')
    tz = get_tz()  # local timezone
    if not date.tzinfo:
        local_date = tz.localize(date)
    else:
        local_date = date
    utc_date = local_date.astimezone(utc)
    return utc_date


def get_local_date(date):
    tz = get_tz()
    if not date.tzinfo:  # if false, already localized, skip
        local_date = tz.localize(date)
    else:
        local_date = date
    return local_date


def iso8601_to_local_date(iso_str):
    if not type(iso_str) == str:
        return iso_str  # do nothing if not string, expect it to be a date already
    utc = timezone("UTC")
    utc_date = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_date = utc.localize(utc_date)
    tz = get_tz()
    return utc_date.astimezone(tz)


def get_iso8601_str(date):
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_datetime_object(datetime, format_type):
    """This function returns a datetime object.

    Args:
        datetime (str): Datetime string
        format_type (str): datetime format

    Returns:
        object: Datetime object
    """
    datetime = parse(datetime)

    if format_type == "Time":
        return datetime.time()

    elif format_type == "Date":
        return datetime.date()

    else:
        return datetime
