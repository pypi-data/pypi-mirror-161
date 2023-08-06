# RFC3339 https://www.ietf.org/rfc/rfc3339.txt
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

RFC_RE = re.compile(r"(\d{4})-(\d\d)-(\d\d)[ Tt](\d\d):(\d\d):(\d\d)([.,]\d+)?([zZ]|[-+](\d\d):?(\d\d)?)?")


class ParseError(ValueError):
    pass


def _tz(tzstr: str, hours: Optional[str], minutes: Optional[str]):
    if tzstr == "z" or tzstr == "Z":
        return timezone.utc
    # will raise TypeError if this are None
    h = int(hours)
    # minutes is optional
    m = int(minutes) if minutes is not None else 0
    # if not h and not m:
    #     return timezone.utc
    if h > 23 or m > 59:
        raise ParseError(f"Invalid timezone: {tzstr}")
    td = timedelta(hours=h, minutes=m)
    if tzstr.startswith("-"):
        td = -td
    return timezone(td)


def serialise(dt: datetime, *, assume_utc: bool = False):
    if dt.tzinfo is None:
        if assume_utc:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            raise ValueError("Datetime is not timezone aware")
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def deserialise(dtstr: str, *, assume_utc: bool = False):
    m = RFC_RE.match(dtstr)
    if not m:
        raise ParseError(f"Invalid RFC3339 string: {dtstr}")
    if m.endpos < len(dtstr) or m.endpos < len(dtstr.rstrip()):
        raise ParseError("Extra characters after end of datetime")
    year, month, day, hour, minute, second, frac, tzstr, tzhours, tzmins = m.groups()
    if tzstr is None:
        if assume_utc:
            tz = timezone.utc
        else:
            raise ParseError("RFC3339 string has no timezone part")
    else:
        tz = _tz(tzstr, tzhours, tzmins)
    return datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
        microsecond=int(frac[1:]) if frac is not None else 0,
        tzinfo=tz,
    )
