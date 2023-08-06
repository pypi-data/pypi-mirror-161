# -*- coding: utf-8 -*-
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from openseries.sweden_holidays import SwedenHolidayCalendar, holidays_sw
from pandas.tseries.offsets import CDay


def date_fix(d: str | dt.date | dt.datetime | np.datetime64 | pd.Timestamp) -> dt.date:
    """Function to parse from different date formats into datetime.date
    :param d: the data item to parse
    :returns : datetime.date
    """

    if isinstance(d, dt.datetime) or isinstance(d, pd.Timestamp):
        return d.date()
    elif isinstance(d, dt.date):
        return d
    elif isinstance(d, np.datetime64):
        return pd.to_datetime(str(d)).date()
    elif isinstance(d, str):
        return dt.datetime.strptime(d, "%Y-%m-%d").date()
    else:
        raise Exception(
            f"Unknown date format {str(d)} of type {str(type(d))} encountered"
        )


def date_offset_foll(
    raw_date: str | dt.date | dt.datetime | np.datetime64 | pd.Timestamp,
    calendar: CDay,
    months_offset: int = 12,
    adjust: bool = False,
    following: bool = True,
) -> dt.date:
    """Function to offset dates according to a given calendar
    :param raw_date: The date to offset from
    :param calendar: Pandas date offset business calendar
    :param months_offset: Number of months as integer
    :param adjust: Boolean condition controlling if offset should adjust for
                   business days
    :param following: Boolean condition controlling days should be offset
                      forward (following=True) or backward
    :returns : datetime.date
    """

    start_dt = dt.date(1970, 12, 30)
    end_dt = dt.date(start_dt.year + 90, 12, 30)
    local_bdays = [
        d.date() for d in pd.date_range(start=start_dt, end=end_dt, freq=calendar)
    ]
    raw_date = date_fix(raw_date)

    month_delta = relativedelta(months=months_offset)

    if following:
        day_delta = relativedelta(days=1)
    else:
        day_delta = relativedelta(days=-1)
    new_date = raw_date + month_delta

    if adjust:
        while new_date not in local_bdays:
            new_date += day_delta

    return new_date


def get_previous_sweden_business_day_before_today(today: dt.date | None = None):
    """Function to bump backwards to find the previous Swedish business day before today
    :param today: the data item to parse
    :returns : datetime.date
    """

    sweden = SwedenHolidayCalendar(rules=holidays_sw)

    if today is None:
        today = dt.date.today()

    return date_offset_foll(
        today - dt.timedelta(days=1),
        calendar=CDay(calendar=sweden),
        months_offset=0,
        adjust=True,
        following=False,
    )
