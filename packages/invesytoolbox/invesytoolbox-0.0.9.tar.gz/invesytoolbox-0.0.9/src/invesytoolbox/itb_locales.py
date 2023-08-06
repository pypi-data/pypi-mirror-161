# -*- coding: utf-8 -*-
"""
=============
locales_tools
=============
"""

from typing import Union
import locale
import pycountry
from babel import Locale
import gettext
import holidays
import datetime
import DateTime
from functools import lru_cache
from babel.numbers import format_currency, get_territory_currencies

from itb_text_name import map_special_chars
from itb_date_time import convert_datetime

countries = pycountry.countries
keys_to_translate = ('name', 'official_name')


@lru_cache
def get_locale(
    loc: locale = None
) -> dict:
    """ Get system locale or transform locale provided as argument into a dictionary"""

    loc_dict = {}

    if not loc:
        loc = locale.getlocale()
        loc_dict['locale'] = loc

    locale_str = loc[0]
    loc_dict['locale_str'] = locale_str

    language, country = locale_str.split('_')
    loc_dict['language'] = language
    loc_dict['country'] = country

    currency = get_territory_currencies(country)[0]
    loc_dict['currency'] = currency

    return loc_dict


def translation_needed(
    keys: (list, tuple),
    language: str
) -> bool:
    """Check if translation is needed

    :param keys: keys that may need translation
    :param language: translate if language is not en
    """

    trans_needed = False

    if not language == 'en':
        for k in keys:
            if k in keys_to_translate:
                trans_needed = True

    return trans_needed


@lru_cache
def fetch_all_countries(
    keys: (list, tuple) = ['alpha_2', 'name'],
    returning: str = 'list',
    language: str = get_locale().get('language'),
    sort_key: str = 'name'
) -> (list, tuple, dict):
    """Fetch all countries

    :param keys: default is ['alpha_2', 'name'], possible values are:

        - alpha_2
        - alpha_3
        - name
        - official_name
        - numeric

    :param returning: list, tuple, dict, dictdict (dictionary of dictionaries) are possible
    :param language: default is de
    :param sort_key: name of the key
    :raises ValueError: if sort_key is not in keys
    """

    get_translation = translation_needed(
        keys=keys,
        language=language
    )

    if get_translation:
        language_trans = gettext.translation(
            'iso3166',
            pycountry.LOCALES_DIR,
            languages=[language]
        )
        gettext_translate = language_trans.gettext

    def translate(
        text: str,
        key: str
    ) -> str:
        if not get_translation:
            return text
        elif key not in keys_to_translate:
            return text
        elif not text:
            return ''
        else:
            return gettext_translate(text)

    if returning in ('list', 'tuple'):
        # makes only sense for lists and tuples
        key = keys[0] if len(keys) == 1 else None

        if key:
            base_list = [
                translate(
                    getattr(country, key, ''), key
                ) for country in countries
            ]

        else:
            base_list = [tuple(
                [translate(
                    getattr(country, key, ''),
                    key
                ) for key in keys]
                + [map_special_chars(
                    translate(
                        getattr(country, sort_key, ''),
                        sort_key
                    ),
                    sort=True
                )]) for country in countries]

        try:
            base_list.sort(key=lambda tup: tup[-1])
        except ValueError:
            raise ValueError(
                f'sort_key value (which is {sort_key}) must be in keys (currently {keys})!'
            )

        if returning.startswith('tuple'):
            all_countries = tuple(base_list)
        else:
            all_countries = base_list

    elif returning == 'dict':
        all_countries = {
            getattr(
                country,
                keys[0]
            ): tuple(
                [
                    translate(
                        getattr(country, key, ''),
                        key
                    ) for key in keys[1:]
                ]) for country in countries
        }

    elif returning == 'dictdict':
        all_countries = {
            getattr(
                country,
                keys[0]
            ): {
                key: translate(
                    getattr(country, key, ''),
                    key
                ) for key in keys[1:]
            } for country in countries}

    return all_countries


def format_price(
    price: (float, int, str),
    loc: locale = None
) -> str:

    my_locale = get_locale()

    price_str = format_currency(
        price,
        my_locale.get('currency'),
        locale=my_locale.get('locale_str')
    )

    if price_str.endswith('00'):
        price_str = price_str[:-2] + '-'

    return price_str.replace('\xa0', ' ')


@lru_cache(maxsize=5)
def get_country(
    country: str = get_locale().get('country'),
    key: str = 'alpha_2',
    language: str = get_locale().get('language')
) -> dict:
    """Get country

    Return all the data for a country
    """

    country = country.upper()  # otherwise babel Locale won't work

    my_country = countries.get(**{key: country})

    countryDict = {}

    try:
        countryDict['name'] = Locale(language).territories[country]
    except KeyError:
        countryDict['name'] = getattr(my_country, 'name')

    for k in (
        'alpha_2',
        'alpha_3',
        'numeric',
        'official_name'
    ):
        countryDict[k] = getattr(my_country, k)

    return countryDict


@lru_cache(maxsize=5)
def get_language_name(
    code: str = get_locale().get('language'),
    language: str = get_locale().get('language')
) -> str:
    """Get language name

    :param language: is the language in which the language name is returned
    """

    return Locale(code).get_language_name(language)


def fetch_holidays(
    country: str = get_locale().get('country'),
    state: (str, int) = None,
    subdiv: (str, int) = None,
    years: (list, int) = [],
    length: int = 0,
    daterange: list = [],
    fmt: str = None,
    datatype: str = 'date',
    returning: str = 'dictionary'
) -> Union[list, dict]:
    """Fetch holidays

    :param years:
    :param length: maximum to return, mit length kann man die Anzahl begrenzen
    :param daterange:
    :param fmt: default: %d.%m.%Y
    :param datatype: default: date
    :param state: this argument exists only for the sake of convenience. It actually feeds subdiv but "state" is more intuitive as a name for most countries
    :param returning: values

        - dict, dictionary (default): keys as specified in argument datatype
        - holidays: return the holidays data object
        - days, dates: return only the dates, as specified in argument datatype
        - names: only the names of the holidays, sorted chronologically
        - names_sorted: only the names of the holidays, sorted alphabetically
        - tuples

    :raises Exception: for unknown value for argument "returning"
    :raises Exception: for datatype "DateTime" and returning "holidays"
    """

    country = country.upper()

    if not subdiv and state:
        subdiv = state

    def remove_dates(holidays: list, dates_to_remove: list):
        for date_to_remove in dates_to_remove:
            holi_days.pop(date_to_remove)

    if not years and not daterange:
        years = datetime.datetime.today().year

    dates_to_remove = []

    if years:
        holi_days = holidays.country_holidays(
            country,
            subdiv=subdiv,
            years=years
        )
        if returning == 'holidays':
            pass
        if returning in ('dict', 'dictionary'):
            pass
        elif returning in ('days', 'holidays', 'dates'):
            return holi_days.keys()
        elif returning == 'names':
            return holi_days.values()
        elif returning == 'names_sorted':
            return sorted(holi_days.values())
        else:
            raise Exception(
                f'unknown value "{returning}" for argument "returning"'
            )

    elif daterange:

        daterange = [
            convert_datetime(daterange[0], 'date', fmt=fmt),
            convert_datetime(daterange[1], 'date', fmt=fmt)
        ]

        holi_days = holidays.country_holidays(
            country,
            subdiv=subdiv,
            years=[y for y in range(
                daterange[0].year,  # first year
                daterange[1].year + 1)  # last year
            ]
        )

        for datum in holi_days:
            if datum < daterange[0] or datum > daterange[1]:
                dates_to_remove.append(datum)

    remove_dates(holi_days, dates_to_remove)  # remove date outside of daterange

    dates_to_remove = []

    if length and length < len(holi_days):
        holdays_list = holi_days[:length]

        if returning in ('dict', 'dictionary'):
            for datum in holi_days:
                if datum not in holdays_list:
                    dates_to_remove.append(datum)

    remove_dates(holi_days, dates_to_remove)  # remove

    if returning == 'holidays':
        if datatype == 'DateTime':
            raise Exception('Cannot use datatype DateTime with holidays data object.')
        return holi_days

    # dict is sorted by date!
    holi_days = {date: holi_days[date] for date in sorted(holi_days)}

    if returning in ('dict', 'dictionary'):
        if datatype == 'date':
            return {date: name for date, name in holi_days.items()}
        else:
            return {
                convert_datetime(date, datatype): name
                for date, name in holi_days.items()
            }

    elif returning in ('days', 'dates'):
        if datatype == 'date':
            return [day for day in holi_days]
        else:
            return [convert_datetime(day, datatype) for day in holi_days]

    elif returning == 'names':
        # duplicates are removed, sorting remains by date
        return [name for name in set(holi_days.values())]

    elif returning == 'names_sorted':
        # duplicates are removed, sorting by name (alphabetically)
        return [name for name in sorted(set(holi_days.values()))]

    elif returning == 'tuples':
        # sorted by date, no other option available currently
        return [
            (
                convert_datetime(date, datatype), holi_days.get(date)
            ) for date in holi_days]

    else:
        raise Exception(
            f'unknown value "{returning}" for argument "returning"'
        )


def is_holiday(
    datum: (
        str,
        datetime.date,
        datetime.datetime,
        'DateTime.DateTime',
    ) = None,
    country: str = get_locale().get('country'),
    fmt: str = None,
    state: (str, int) = None,
    subdiv: (str, int) = None,
) -> bool:
    """Check if date is a holiday

    :param datum:
    :param fmt:
    :param state: subdiv
    """

    if not datum:
        datum = datetime.date.today()

    country = country.upper()

    if state and not subdiv:
        subdiv = state

    datum = convert_datetime(datum, 'date')
    year = datum.year

    holi_days = holidays.country_holidays(
        country,
        subdiv=subdiv,
        years=year
    )

    return datum in holi_days
