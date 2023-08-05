# coding=utf-8
"""
===============
date_time_tools
===============
"""

import datetime
import DateTime


def get_dateformat(
    datestring: str,
    leading_zeroes: bool = True,
    for_DateTime: bool = False
) -> str:
    """Get the format string needed to convert a datetime string to an object

    :param datestring:
    :todo: times!
    :raises ValueError: if an invalid datetime or DateTime string is provided
    """
    if '.' in datestring:  # international format
        datefmt = '%d.%m.%Y'

    elif '/' in datestring:
        if len(datestring.split('/')[0]) < 3:
            if for_DateTime:
                datefmt = 'us'
            else:
                datefmt = '%m/%d/%Y'  # US format
        else:
            if for_DateTime:
                datefmt = 'international'
            else:
                datefmt = '%Y/%m/%d'  # international format
    elif '-' in datestring:  # international format
        if for_DateTime:
            datefmt = 'international'
        else:
            datefmt = '%Y-%m-%d'
    else:  # default
        if for_DateTime:
            datefmt = 'international'
        else:
            datefmt = '%d.%m.%Y'

    if for_DateTime:
        try:
            DateTime.DateTime(datestring, datefmt=datefmt)
        except DateTime.interfaces.DateError:
            msg = datestring + ' is not a valid DateTime string.'
            raise ValueError(msg)
    else:
        try:
            datetime.datetime.strptime(datestring, datefmt)
        except ValueError:
            msg = datestring + ' is not a valid date or datetime string.'
            raise ValueError(msg)

        if not leading_zeroes:
            datefmt = datefmt.replace(
                '%d', '%-d'
            ).replace('%m', '%-m')

    return datefmt


def str_to_dt(
    datestring: str,
    fmt: (str, None) = None
) -> datetime.datetime:
    """ Convert a string to datetime.datetime

    :param datestring:
    :param fmt: default: %d.%m.%Y
    """

    fmt = fmt or get_dateformat(datestring=datestring)
    return datetime.datetime.strptime(datestring, fmt)


def str_to_DT(
    datestring: str,
    fmt: (str, None) = None
) -> DateTime.DateTime:
    """ Convert a string to Datetime.Datetime

    The conversion is made with datetime.datetime first, because
    DateTime.DateTime cannot convert a string with a given format-string

    :param datestring:
    :param fmt: default: %d.%m.%Y
    """

    if not fmt:
        datefmt = get_dateformat(datestring, for_DateTime=True)
        return DateTime.DateTime(datestring, datefmt=datefmt)
    else:
        dt = str_to_dt(datestring=datestring, fmt=fmt)
        return DateTime.DateTime(dt)


def str_to_date(
    datestring: str,
    fmt: (str, None) = None
) -> datetime.date:
    """ Convert a string to datetime.date

    :param datestring:
    :param fmt: default: %d.%m.%Y
    """

    fmt = fmt or get_dateformat(datestring=datestring)
    return datetime.datetime.strptime(datestring, fmt).date()


def DT_to_dt(
    DT: DateTime.DateTime
) -> datetime.datetime:
    """ Convert DateTime.DateTime to datetime.datetime """

    return datetime.datetime(
        DT.year(),
        DT.month(),
        DT.day(),
        DT.hour(),
        DT.minute()
    )


def DT_to_date(
    DT: DateTime.DateTime
) -> datetime.date:
    """ Convert DateTime.DateTime to datetime.date """

    return datetime.date(
        DT.year(),
        DT.month(),
        DT.day()
    )


def date_to_dt(
    date: datetime.date,
    H=None, M=None
) -> datetime.datetime:
    """ Convert datetime.date to datetime.datetime

    :param date:
    :param H: hour
    :param M: minute
    """

    if H and M:
        dt = datetime.datetime.combine(
            date,
            datetime.datetime(2000, 1, 1, int(H), int(M)).time()
        )
    else:
        dt = datetime.datetime.combine(
            date,
            datetime.datetime.min.time()
        )
    return dt


def date_to_DT(
    date: datetime.date
) -> DateTime.DateTime:
    """ Convert datetime.date to DateTime.DateTime

    :param datestring:
    :param fmt: default: %d.%m.%Y
    """

    return DateTime.DateTime(date_to_dt(date))


def DT_date(
    DT: DateTime.DateTime
) -> DateTime.DateTime:
    """ Strip a DateTime of its time """
    return DT - ( DT.time + DT.tzoffset() / 24 / 3600)


def convert_datetime(
    date: (
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    ),
    convert_to, fmt=None
) -> (datetime.datetime, datetime.date, DateTime.DateTime, str):
    """ Conversion of date and time formats

    :param date:
    :param convertTo:

        - date: datetime.date
        - datetime: datetime.datetime
        - DateTime: DateTime.DateTime
        - str, string: string

    :param fmt: is used both for converting from and converting to
    """

    if isinstance(date, DateTime.DateTime):
        if convert_to == 'DateTime':
            return date
        elif convert_to == 'date':
            return DT_to_date(date)
        elif convert_to == 'datetime':
            return DT_to_dt(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)
    elif isinstance(date, str):
        if convert_to in ('str', 'string'):
            return date
        elif convert_to == 'date':
            return str_to_date(date, fmt=fmt)
        elif convert_to == 'datetime':
            return str_to_dt(date, fmt=fmt)
        elif convert_to == 'DateTime':
            return str_to_DT(date, fmt=fmt)
    elif isinstance(date, datetime.datetime):
        # datetime.datetime has to be checked BEFORE datetime.date (isinstance(datetime.datetime, datetime.date) == True !)
        if convert_to == 'date':
            return date.date()
        elif convert_to == 'datetime':
            return date
        elif convert_to == 'DateTime':
            return date_to_DT(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)
    elif isinstance(date, datetime.date):
        if convert_to == 'date':
            return date
        elif convert_to == 'datetime':
            return date_to_dt(date)
        elif convert_to == 'DateTime':
            return date_to_DT(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)


def get_calendar_week(
    date: (
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    )
) -> int:
    """ Get calendard week (week nb of year) from a date

    :param date: can be any date, datetime, DateTime or string
    """

    date = convert_datetime(date, 'date')

    return date.isocalendar()[1]


def get_dow_number(
    date: (
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    )
) -> int:
    """ Get day of week number from a date

    :param date: should be a datetime.date or a string formatted '%d.%m.%Y'
    """

    date = convert_datetime(date, 'date')

    return date.isocalendar()[2]


def get_isocalendar(
    date: (
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    )
) -> datetime.date:
    """ Returns the isocalendar tuple: (year, woy, downb)

    Returns year, weeknb (week of year) and day of week number

    :param date: should be a datetime.date or a string formatted '%d.%m.%Y'
    """

    date = convert_datetime(date, 'date')

    return date.isocalendar()


def get_monday(
    year: int,
    week: int,
    endofweek: int = 7
) -> datetime.datetime:
    """ Returns monday as a datetime object yy

    .. warning:: xobsolete!
    """

    year = int(year)
    week = int(week)
    endofweek = int(endofweek)

    if week < 1:
        first_monday_year = datetime.date.fromisocalendar(year, 1, 1)
        monday_back = first_monday_year - datetime.timedelta(weeks=abs(week))
        year, week, _ = monday_back.isocalendar()

    ref = datetime.date(year, 6, 6)
    ref_week, ref_day = ref.isocalendar()[1:]

    monday = ref + datetime.timedelta(days=7 * (week - ref_week) - ref_day + 1)

    return monday


def daterange_from_week(
    year: int,
    week: int,
    returning: str = 'datetime',
    endofweek: int = 7,
    fmt: str = '%d.%m.%Y'
) -> tuple:
    """Get a date range from a week

    :param returning:
           - DateTime
           - datetime (default)
           - date
    :param fmt: default: '%d.%m.%Y'

    .. note:: Author: Andreas Bruhn, https://groups.google.com/forum/#!topic/de.comp.lang.python/p8LfbNMIJ5c

    .. note:: If weekday exceeds the year, then the date is from next year, even if the week is not correct then
    """
    monday = get_monday(
        year=year,
        week=week,
        endofweek=endofweek
    )

    last_day = monday + datetime.timedelta(days=endofweek - 1)

    monday = convert_datetime(monday, returning)
    last_day = convert_datetime(last_day, returning)

    return monday, last_day


def dates_from_week(
    year: int,
    week: int,
    returning: str = 'datetime',
    endofweek: int = 7,
    fmt: str = '%d.%m.%Y'
) -> list:
    """Get dates from a week

    .. note:: Author: Andreas Bruhn, https://groups.google.com/forum/#!topic/de.comp.lang.python/p8LfbNMIJ5c
    .. note:: If weekday exceeds the year, then the date is from next year, even if the week is not correct then

    :param year:
    :param week: integer
    :param returning:

        - DateTime (default)
        - datetime
        - date

    :param fmt: default: '%d.%m.%Y'
    :param endofweek: 1 to 7 (monday to sunday)
    """

    monday = get_monday(
        year=year,
        week=week,
        endofweek=endofweek
    )

    dates = []

    for i in range(0, endofweek):
        dates.append(
            monday + datetime.timedelta(days=i)
        )

    # assert dates[0].isocalendar() == (int(year), int(week), 1)
    # assert dates[-1].isocalendar() == (int(year), int(week), int(endofweek))

    return_dates = []

    for date in dates:
        return_dates.append(
            convert_datetime(date, returning)
        )

    return return_dates


def day_from_week(
    year: int,
    week: int,
    weekday: int = 1,
    returning: str = 'datetime',
    fmt: str = '%d.%m.%Y'
) -> (datetime.datetime, datetime.date, DateTime.DateTime):
    """Get day from a week

    :param year:
    :param week: integer
    :param weekday: begins with 1 = monday
    :param returning:

       - DateTime
       - datetime (default)
       - date

    :param fmt: default: '%d.%m.%Y'
    """

    return dates_from_week(
        year=year,
        week=week,
        returning=returning,
        fmt=fmt
    )[int(weekday) - 1]


def monday_from_week(
    year: int,
    week: int,
    returning: str = 'datetime',
    fmt='%d.%m.%Y'
) -> (datetime.datetime, datetime.date, DateTime.DateTime):
    """Get monday from a week

    :param year
    :param week: integer
    :param: weekday begins with 1 = monday
    :param returning:

           - DateTime
           - datetime (default)
           - date

    :param fmt: default: '%d.%m.%Y'
    """

    return day_from_week(
        year=year,
        week=week,
        returning=returning,
        fmt=fmt
    )


def last_week_of_year(
    year: int
) -> int:

    last_week = datetime.date(year, 12, 28)
    return last_week.isocalendar()[1]
