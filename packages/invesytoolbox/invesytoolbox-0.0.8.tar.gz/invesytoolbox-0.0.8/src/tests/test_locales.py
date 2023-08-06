# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_country_language.py
"""

import sys
import unittest
import datetime
import DateTime

sys.path.append(".")

from itb_locales import \
    fetch_holidays, is_holiday, format_price

days_and_holidays = {
    '1.4.2020': False,
    '2022-05-01': True,
    '6.1.2023': True,
    '2023/6/1': False,
    '01/06/2023': True,
    '1/6/2023': True,
    '13.8.2022': False,
    datetime.date(2022, 5, 1): True,
    datetime.date(2022, 12, 11): False,
    datetime.datetime(2023, 1, 6): True,
    datetime.datetime(2023, 1, 11): False,
    DateTime.DateTime(2023, 1, 6): True,
    DateTime.DateTime(2023, 1, 11): False,
}

feiertage_2022_2023 = {
    datetime.date(2022, 1, 1): 'Neujahr',
    datetime.date(2022, 1, 6): 'Heilige Drei Könige',
    datetime.date(2022, 4, 18): 'Ostermontag',
    datetime.date(2022, 5, 1): 'Staatsfeiertag',
    datetime.date(2022, 5, 26): 'Christi Himmelfahrt',
    datetime.date(2022, 6, 6): 'Pfingstmontag',
    datetime.date(2022, 6, 16): 'Fronleichnam',
    datetime.date(2022, 8, 15): 'Mariä Himmelfahrt',
    datetime.date(2022, 10, 26): 'Nationalfeiertag',
    datetime.date(2022, 11, 1): 'Allerheiligen',
    datetime.date(2022, 12, 8): 'Mariä Empfängnis',
    datetime.date(2022, 12, 25): 'Christtag',
    datetime.date(2022, 12, 26): 'Stefanitag',
    datetime.date(2023, 1, 1): 'Neujahr',
    datetime.date(2023, 1, 6): 'Heilige Drei Könige',
    datetime.date(2023, 4, 10): 'Ostermontag',
    datetime.date(2023, 5, 1): 'Staatsfeiertag',
    datetime.date(2023, 5, 18): 'Christi Himmelfahrt',
    datetime.date(2023, 5, 29): 'Pfingstmontag',
    datetime.date(2023, 6, 8): 'Fronleichnam',
    datetime.date(2023, 8, 15): 'Mariä Himmelfahrt',
    datetime.date(2023, 10, 26): 'Nationalfeiertag',
    datetime.date(2023, 11, 1): 'Allerheiligen',
    datetime.date(2023, 12, 8): 'Mariä Empfängnis',
    datetime.date(2023, 12, 25): 'Christtag',
    datetime.date(2023, 12, 26): 'Stefanitag',
    datetime.date(2024, 1, 1): 'Neujahr',
    datetime.date(2024, 1, 6): 'Heilige Drei Könige',
    datetime.date(2024, 4, 1): 'Ostermontag',
    datetime.date(2024, 5, 1): 'Staatsfeiertag',
    datetime.date(2024, 5, 9): 'Christi Himmelfahrt',
    datetime.date(2024, 5, 20): 'Pfingstmontag',
    datetime.date(2024, 5, 30): 'Fronleichnam',
    datetime.date(2024, 8, 15): 'Mariä Himmelfahrt',
    datetime.date(2024, 10, 26): 'Nationalfeiertag',
    datetime.date(2024, 11, 1): 'Allerheiligen',
    datetime.date(2024, 12, 8): 'Mariä Empfängnis',
    datetime.date(2024, 12, 25): 'Christtag',
    datetime.date(2024, 12, 26): 'Stefanitag'
}


class TestLocales(unittest.TestCase):
    def test_fetch_holidays(self):
        holidays = fetch_holidays(
            country='AT',
            state=9,
            years=[2022, 2023, 2024]
        )
        self.assertEqual(holidays, feiertage_2022_2023)

        holidays = fetch_holidays(
            country='AT',
            state=9,
            daterange=['1.1.2022', '31.12.2024']
        )
        self.assertEqual(holidays, feiertage_2022_2023)

    def test_is_holiday(self):
        for date, check in days_and_holidays.items():
            checked = is_holiday(datum=date, country='AT', state=9)
            self.assertEqual(checked, check)

    def test_format_price(self):
        for price in (123, 2, 234234, 234100):
            print(format_price(price))


if __name__ == '__main__':
    unittest.main()

    print('finished country & language tests.')
