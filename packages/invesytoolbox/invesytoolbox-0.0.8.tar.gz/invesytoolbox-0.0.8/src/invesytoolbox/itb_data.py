# -*- coding: utf-8 -*-
"""
==========
data_tools
==========
"""

from typing import Union
import DateTime
import vobject
from itb_date_time import convert_datetime
from itb_email_phone import process_phonenumber

comma_float_chars = set(',1234567890')
datetime_chars = set('1234567890.-:/+ ')


def dict_from_dict_list(
    dict_list: list,
    key,
    single_value=None,
    include_key=False
) -> dict:
    """Create a dictionary from a list of dictionaries

    .. note:: The annotated return type is not true if a single_value argument is given.

    :param dictList: the list of dictionaries to be converted
    :param key: the key of the dictionaries to use as key for the new dictionary.
                This must be a unique key, otherwise the new dictionary will
                only contain the first result
    :param singleValue: only a single value for each key is provided
    :param include_key: the value used as key is also included in values dictionary
    """

    dl = [dict(d) for d in dict_list]  # we copy the list because we will change the dictionaries (except for single_value)

    new_dict = {}

    for dictionary in dl:
        if single_value:
            new_dict[dictionary.pop(key)] = dictionary.get(single_value)
        elif include_key:
            new_dict[dictionary[key]] = dictionary
        else:
            # slick: pop the id and use it as key for newDict in one line
            new_dict[dictionary.pop(key)] = dictionary

    return new_dict


def create_vcard(
    data: dict,
    returning: str = 'vcard'
) -> str:
    """create a vCard from a dictionary

    .. note:: The serialized vcard has Windows line-breaks, which is fine, I guess
    .. note:: colons in notes are escaped in vobject

    :param data: keys:

        - prename
        - surname
        - email
        - phone
        - street
        - city
        - region (eg. federal state)
        - zipcode
        - country
    """

    prename = data.get('prename', '')
    surname = data.get('surname', '')
    if not prename and not surname:
        return None

    vcard = vobject.vCard()
    vcard.add('n')
    vcard.n.value = vobject.vcard.Name(
        family=surname,
        given=prename
    )
    vcard.add('fn')
    vcard.fn.value = f'{prename} {surname}'
    vcard.add('email')
    vcard.email.value = data.get('email', '')
    vcard.email.type_param = 'INTERNET'
    vcard.add('tel')
    phone = process_phonenumber(
        data.get('phone', ''),
        empty_if_invalid=True
    )
    if phone:
        vcard.tel.value = phone
        vcard.tel.type_param = ['CELL', 'VOICE']
    vcard.add('adr')
    vcard.adr.type_param = ['HOME', 'pref']
    vcard.adr.value = vobject.vcard.Address(
        street=data.get('street', ''),
        city=data.get('city', ''),
        region=data.get('region', ''),
        code=data.get('zipcode', ''),
        country=data.get('country', '')
    )
    vcard.add('note')
    vcard.note.value = data.get('note', '')

    if returning == 'pretty':
        return vcard.prettyPrint()
    else:
        return vcard.serialize()


def dict_2unicode(
    d: dict,
    encoding: str = 'utf-8'
) -> dict:
    """ Converts all keys and values in a dictionary from bytes to unicode

    All keys and values are changed from bytes to unicode, if applicable.
    Other data types are left unchaged, including other compound data types.

    :param d: dictionary
    :param encoding: default is utf-8
    """

    return {
        k.decode(encoding) if isinstance(k, bytes) else k:
            (v.decode(encoding) if isinstance(v, bytes) else v)
            for k, v in d.items()
    }


def dict_2datatypes(
    d: dict,
    json_data: str = None,
    convert_keys: bool = False,
    convert_to_unicode: bool = False,
    dt: str = 'datetime'
) -> dict:
    """ convert all data of a dictionary to specific (json metadata) or guessed types """

    if convert_keys:
        return {
            value_2datatype(
                value=key,
                convert_to_unicode=convert_to_unicode,
                dt=dt
            ): value_2datatype(
                value=val,
                json_data=json_data,
                key=key,
                convert_to_unicode=convert_to_unicode,
                dt=dt
            )
            for key, val in d.items()
        }  # dict comprehension
    else:
        return {
            key: value_2datatype(
                value=val,
                json_data=json_data,
                key=key,
                convert_to_unicode=convert_to_unicode,
                dt=dt
            )
            for key, val in d.items()
        }  # dict comprehension


def sort_dictlist(
    dictlist: list,
    keys: (str, list),
    reverse: bool = False
) -> list:
    """ Sorts a list of dictionaries

    :param dictList: list of dictionaries
    :param keys: sort by these keys
    :param reverse: True reverses the sorting order
    """

    if isinstance(keys, str):
        if ',' in keys:
            keys = keys.replace(
                ' ', ''
            ).split(',')
        else:
            keys = [keys]

    if len(keys) == 1:
        key = keys[0]
        sorted_dictlist = sorted(
            dictlist,
            key=lambda i: i[key],
            reverse=reverse
        )
    else:
        sorted_dictlist = sorted(
            dictlist,
            key=lambda i: [i[key] for key in keys]
        )

    return sorted_dictlist


def value_2datatype(
    value,
    json_data: str = None,
    key: str = None,
    convert_to_unicode: bool = False,
    encoding: str = 'utf-8',
    dt: str = 'datetime'
) -> Union[str, int, float]:
    """ Convert a value to a datatype

    this function has two modes:

    1. it uses a json file with the metadata (types of variables by name)
    2. it makes educated guesses in converting a string (don't feed bytes to this function!)

    :param value:
    :param json_data: metadata
    :param key: key in the json_data (value name)
    :param convert_to_unicode: convert all bytes to unicode in the process
    :param encoding: if bytes are present, use this encoding to convert them to unicode
    :param dt: use datetime or DateTime as time format (default: datetime)
    """

    if json_data:
        typ = json_data.get(key)
        if not typ:
            return value
        else:
            if typ == 'int':
                try:
                    return int(value)
                except ValueError:
                    return value
            if typ == 'float':
                value = value.replace(',', '.')
                try:
                    return float(value)
                except ValueError:
                    return value
            if typ == 'datetime':
                value = value.strip()
                try:
                    return DateTime(
                        value,
                        datefmt='international'
                    )
                except DateTime.interfaces.SyntaxError:
                    return value
    else:
        original_value = value

        if isinstance(value, bytes):
            value = value.decode('utf-8')

        if isinstance(value, str):
            value = value.strip()

            if value == 'False':
                return False

            if value == 'True':
                return True

            try:
                if (
                    len(value) >= 8
                    and set(value[:16]).issubset(datetime_chars)
                ):  # there could be a TimeZone
                    return convert_datetime(date=value, convert_to=dt)

            except Exception:
                # in case it's a subset of datetime_chars but not a date or datetime
                pass

            try:
                return int(value)
            except (ValueError, TypeError):
                pass

            if set(value).issubset(comma_float_chars):
                value = value.replace(',', '.')

            try:
                return float(value)
            except (ValueError, TypeError):
                pass

            if (
                not convert_to_unicode
                and isinstance(value, str)
            ):  # portentionally restore bytes
                value = original_value

        return value
