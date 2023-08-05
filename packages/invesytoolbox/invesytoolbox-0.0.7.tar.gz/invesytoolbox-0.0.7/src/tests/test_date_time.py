# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_date_time.py
"""

import sys
import unittest
import datetime
import DateTime

sys.path.append(".")

from itb_date_time import \
    convert_datetime, \
    date_to_dt, \
    date_to_DT, \
    DT_to_dt, \
    DT_to_date, \
    daterange_from_week, \
    dates_from_week, \
    day_from_week, \
    get_calendar_week, \
    get_dateformat, \
    get_dow_number, \
    get_isocalendar, \
    last_week_of_year, \
    monday_from_week, \
    str_to_dt, \
    str_to_date, \
    str_to_DT

get_dateformat_error_str_part = ' is not a valid date or datetime string.'

dates_for_checking = {
    '2.4.2020': {
        'convert_fmt': '%d.%m.%Y',
        'datetime': datetime.datetime(2020, 4, 2),
        'date': datetime.date(2020, 4, 2),
        'DateTime': DateTime.DateTime(2020, 4, 2),
        'week': 14,
        'dow_number': 4,
        'monday': datetime.datetime(2020, 3, 30),
        'sunday': datetime.datetime(2020, 4, 5),
        'isocalendar': datetime.date(2020, 4, 2).isocalendar(),
        'last_week': 53
    },
    '21.5.1980': {
        'convert_fmt': '%d.%m.%Y',
        'datetime': datetime.datetime(1980, 5, 21),
        'date': datetime.date(1980, 5, 21),
        'DateTime': DateTime.DateTime(1980, 5, 21),
        'week': 21,
        'dow_number': 3,
        'monday': datetime.datetime(1980, 5, 19),
        'sunday': datetime.datetime(1980, 5, 25),
        'isocalendar': datetime.date(1980, 5, 21).isocalendar(),
        'last_week': 52
    },
    '05.05.2001': {
        'convert_fmt': '%d.%m.%Y',
        'datetime': datetime.datetime(2001, 5, 5),
        'date': datetime.date(2001, 5, 5),
        'DateTime': DateTime.DateTime(2001, 5, 5),
        'week': 18,
        'dow_number': 6,
        'monday': datetime.datetime(2001, 4, 30),
        'sunday': datetime.datetime(2001, 5, 6),
        'isocalendar': datetime.date(2001, 5, 5).isocalendar(),
        'last_week': 52
    },
    '2000/5/6': {
        'convert_fmt': '%Y/%m/%d',
        'datetime': datetime.datetime(2000, 5, 6),
        'date': datetime.date(2000, 5, 6),
        'DateTime': DateTime.DateTime(2000, 5, 6),
        'week': 18,
        'dow_number': 6,
        'monday': datetime.datetime(2000, 5, 1),
        'sunday': datetime.datetime(2000, 5, 7),
        'isocalendar': datetime.date(2000, 5, 6).isocalendar(),
        'last_week': 52
    },
    '3/4/1970': {
        'convert_fmt': '%m/%d/%Y',
        'datetime': datetime.datetime(1970, 3, 4),
        'date': datetime.date(1970, 3, 4),
        'DateTime': DateTime.DateTime(1970, 3, 4),
        'week': 10,
        'dow_number': 3,
        'monday': datetime.datetime(1970, 3, 2),
        'sunday': datetime.datetime(1970, 3, 8),
        'isocalendar': datetime.date(1970, 3, 4).isocalendar(),
        'last_week': 53
    },
    '2022-05-31': {
        'convert_fmt': '%Y-%m-%d',
        'datetime': datetime.datetime(2022, 5, 31),
        'date': datetime.date(2022, 5, 31),
        'DateTime': DateTime.DateTime(2022, 5, 31),
        'week': 22,
        'dow_number': 2,
        'monday': datetime.datetime(2022, 5, 30),
        'sunday': datetime.datetime(2022, 6, 5),
        'isocalendar': datetime.date(2022, 5, 31).isocalendar(),
        'last_week': 52
    },
    '31-05-2022': {
        'convert_fmt': '31-05-2022' + get_dateformat_error_str_part,
        'datetime': None,
        'date': None,
        'DateTime': None,
        'week': None,
        'dow_number': None,
        'monday': None,
        'sunday': None,
        'isocalendar': None,
        'last_week': None
    },
    '13/7/2000': {
        'convert_fmt': '13/7/2000' + get_dateformat_error_str_part,
        'datetime': None,
        'date': None,
        'DateTime': None,
        'dow_number': None,
        'monday': None,
        'sunday': None,
        'isocalendar': None,
        'last_week': None
    }
}


class Test_date_time(unittest.TestCase):

    def test_get_dateformat(self):

        for d, f in dates_for_checking.items():
            f = f.get('convert_fmt')
            try:
                df = get_dateformat(datestring=d)
            except ValueError as e:
                if get_dateformat_error_str_part in str(e):
                    df = str(e)  # for assert check
                else:
                    raise ValueError(e)
            try:
                self.assertEqual(df, f)
                if get_dateformat_error_str_part in df:
                    print(f'- {df} (test OK)')
                else:
                    pass
            except AssertionError as e:
                print(f'- ASS error on {d}: {e}')

    def check_convert_from_to(self, func, convert_from, convert_to):
        for k, v in dates_for_checking.items():
            fmt = v.get('convert_fmt')

            if convert_from == 'string':
                value_to_convert = k
                fmts = [fmt]
            else:
                value_to_convert = v.get(convert_from)
                fmts = [None]

            if not value_to_convert:
                continue

            check_dt = v.get(convert_to)

            for f in fmts:
                kwargs = {}
                if f:
                    kwargs = {'fmt': f}
                try:
                    dt = func(value_to_convert, **kwargs)
                except ValueError as e:
                    if not check_dt:
                        continue  # there should be an error, so it's ok
                    else:
                        raise ValueError(e)

                try:
                    self.assertEqual(dt, check_dt)
                except AssertionError as e:
                    raise AssertionError(e)

    def test_str_to_dt(self):
        self.check_convert_from_to(func=str_to_dt, convert_from='string', convert_to='datetime')

    def test_str_to_date(self):
        self.check_convert_from_to(func=str_to_date, convert_from='string', convert_to='date')

    def test_str_to_DT(self):
        self.check_convert_from_to(func=str_to_DT, convert_from='string', convert_to='DateTime')

    def test_DT_to_dt(self):
        self.check_convert_from_to(func=DT_to_dt, convert_from='DateTime', convert_to='datetime')

    def test_DT_to_date(self):
        self.check_convert_from_to(func=DT_to_date, convert_from='DateTime', convert_to='date')

    def test_date_to_dt(self):
        self.check_convert_from_to(func=date_to_dt, convert_from='date', convert_to='datetime')

    def test_date_to_DT(self):
        self.check_convert_from_to(func=date_to_DT, convert_from='date', convert_to='DateTime')

    def test_convert_datetime(self):
        convert_tos = ('string', 'datetime', 'date', 'DateTime')
        converts = set()

        for s, v in dates_for_checking.items():
            for k in convert_tos:
                if k == 'string':
                    t = s
                else:
                    t = v.get(k)

                if not t:
                    continue

                converts.add((s, t))

        for date_string, conv_from in converts:
            dates_for_checking_val = dates_for_checking.get(date_string)

            for conv_to in convert_tos:
                check_obj = dates_for_checking_val.get(conv_to)
                convert_fmt = dates_for_checking_val.get('convert_fmt')

                if check_obj is not None:

                    try:
                        res_obj = convert_datetime(date=conv_from, convert_to=conv_to, fmt=convert_fmt)
                    except ValueError as e:
                        if 'is not a valid date or datetime string.' in str(e):
                            # Exception in get_dateformat, validity is tested in the appropriate test function
                            continue
                        elif 'does not match format' in str(e):
                            continue
                        else:
                            raise ValueError(e)

                    self.assertEqual(res_obj, check_obj)

    def test_get_calendar_week(self):
        for s, v in dates_for_checking.items():
            correct_week = v.get('week')

            if not correct_week:
                continue

            for some_date in (s, v.get('date'), v.get('datetime'), v.get('DateTime')):
                week = get_calendar_week(some_date)

                self.assertEqual(week, correct_week)

    def test_get_dow_number(self):
        for s, v in dates_for_checking.items():
            correct_dow_number = v.get('dow_number')

            if not correct_dow_number:
                continue

            for some_date in (s, v.get('date'), v.get('datetime'), v.get('DateTime')):
                dow_number = get_dow_number(some_date)

                self.assertEqual(dow_number, correct_dow_number)

    def test_get_isocalendar(self):
        for s, v in dates_for_checking.items():
            correct_isocalendar = v.get('isocalendar')

            if not correct_isocalendar:
                continue

            for some_date in (s, v.get('date'), v.get('datetime'), v.get('DateTime')):
                iso_calendar = get_isocalendar(some_date)

                self.assertEqual(iso_calendar, correct_isocalendar)

    def test_day_from_week(self):
        for s, v in dates_for_checking.items():
            correct_day = v.get('datetime')

            if not correct_day:
                continue

            year = correct_day.year
            week = v.get('week')
            dow = v.get('dow_number')

            day = day_from_week(year=year, week=week, weekday=dow)

            self.assertEqual(day, correct_day)

    def test_monday_from_week(self):
        for s, v in dates_for_checking.items():
            correct_monday = v.get('monday')

            if not correct_monday:
                continue

            year = correct_monday.year
            week = v.get('week')

            monday = monday_from_week(year=year, week=week)

            self.assertEqual(monday, correct_monday)

    def test_last_week_of_year(self):
        for s, v in dates_for_checking.items():
            correct_last_week = v.get('last_week')

            if not correct_last_week:
                continue

            last_week = last_week_of_year(v.get('datetime').year)

            self.assertEqual(last_week, correct_last_week)

    def test_daterange_from_week(self):
        for s, v in dates_for_checking.items():
            week = v.get('week')

            if not week:
                continue

            correct_monday = v.get('monday')
            correct_sunday = v.get('sunday')
            year = v.get('datetime').year

            daterange = daterange_from_week(year=year, week=week)

            self.assertEqual(daterange, (correct_monday, correct_sunday))

    def test_dates_from_week(self):
        for s, v in dates_for_checking.items():
            week = v.get('week')

            if not week:
                continue

            year = v.get('datetime').year

            monday = v.get('monday')

            correct_dates = [monday]

            for i in range(1, 7):
                correct_dates.append(monday + datetime.timedelta(days=i))

            dates = dates_from_week(year=year, week=week)

            self.assertEqual(dates, correct_dates)


if __name__ == '__main__':
    unittest.main()

    print('finished date_time tests.')
