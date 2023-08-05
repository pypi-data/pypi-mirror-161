"""
Utility methods
"""

from typing import Union
from datetime import datetime

def _to_datetime(value: str, date_time_format: str) -> Union[datetime, None]:
    try:
        return datetime.strptime(value, date_time_format)
    except ValueError:
        return None

def _parse_timepoint(value: str, is_begin: bool) -> datetime:
    datetime_y = _to_datetime(value, '%Y')
    if datetime_y:
        return datetime_y.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) if is_begin \
            else datetime_y.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

    datetime_ymd = _to_datetime(value, '%Y-%m-%d')
    if datetime_ymd:
        return datetime_ymd.replace(hour=0, minute=0, second=0, microsecond=0) if is_begin else datetime_ymd.replace(hour=23, minute=59, second=59, microsecond=999999)

    datetime_dmy = _to_datetime(value, '%d.%m.%Y')
    if datetime_dmy:
        return datetime_dmy.replace(hour=0, minute=0, second=0, microsecond=0) if is_begin else datetime_dmy.replace(hour=23, minute=59, second=59, microsecond=999999)

    datetime_ymd_hms = _to_datetime(value, '%Y-%m-%d %H:%M:%S')
    if datetime_ymd_hms:
        return datetime_ymd_hms.replace(microsecond=0) if is_begin else datetime_ymd_hms.replace(microsecond=999999)

    datetime_dmy_hms = _to_datetime(value, '%d.%m.%Y %H:%M:%S')
    if datetime_dmy_hms:
        return datetime_dmy_hms.replace(microsecond=0) if is_begin else datetime_dmy_hms.replace(microsecond=999999)

    raise ValueError(f'Invalid date format or date value in "{value}"')
