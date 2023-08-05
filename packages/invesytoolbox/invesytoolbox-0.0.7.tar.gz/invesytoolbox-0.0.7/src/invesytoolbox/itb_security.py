# coding=utf-8
"""
==============
security_tools
==============
"""

from os import urandom
from binascii import hexlify

from string import \
    ascii_lowercase as LOWERCASE,\
    ascii_uppercase as UPPERCASE,\
    digits as DIGITS,\
    printable as PRINTABLE,\
    whitespace as WHITESPACE


def create_secure_key(
    bits: int = 256,
    maxLen: int = None,
    key: str = None,
) -> str:
    """ generate a key """

    if not key:
        key = urandom(bits)

    key = hexlify(key)

    if maxLen and len(key) > maxLen:
        key = key[:maxLen]

    return key


def create_key(
    keyLength: int = 15,
    mode: str = 'alphaNum'
) -> str:
    """ generate a random key

    :param mode: alphanum, numbers, chars, lowerChars, upperChars, alphanumLower, alphanumUpper
    """

    from random import choice

    key = ''
    elements = ''

    if mode == 'alphaNum':
        elements = LOWERCASE + UPPERCASE
    elif mode == 'alphaNumLower':
        elements = LOWERCASE + DIGITS
    elif mode == 'alphaNumUpper':
        elements = UPPERCASE + DIGITS
    elif mode == 'lowerChars':
        elements = LOWERCASE
    elif mode == 'upperChars':
        elements = UPPERCASE
    elif mode == 'numbers':
        elements = DIGITS
    elif mode == 'all':
        prnt = set(PRINTABLE)
        wht = set(WHITESPACE)
        exclude = set(['^'])
        pwdElements = prnt - wht - exclude
        elements = ''.join(pwdElements)

    key = ''.join([choice(elements) for _ in range(keyLength)])

    return key


def check_password_security(
    pw: str,
    length: int = 8,
    check_ascii: bool = True,
    check_nonalphanum: bool = False,
    check_number: bool = False,
    check_capital: bool = False
) -> list:
    """ Check Password security

    Check if a password (or any string) meets certain criteria

    returns 0 (or False) if everything ok, otherwise an English error string

    :param length: minimum length
    :param check_ascii: make sure that it contain only ascii characters (so as to be compatible with all keyboards)
    :param check_nonalphanum: includes at least one non alpha-numeric character
    :param check_number: includes at least one number
    :param check_capital: includes at least one uppercase letter
    """

    errors = []

    if len(pw) < length:
        errors.append(
            f'The minimum password length should be {length}'
        )

    if (
        check_ascii
        and not pw.isascii()
    ):
        errors.append(
            'Only ASCII characters are allowed in the password'
        )

    if (
        check_number
        and not any(
            d in pw for d in DIGITS
        )
    ):
        errors.append(
            'The password should contain at least one digit'
        )

    if (
        check_nonalphanum
        and not any(
            d in pw.lower() for d in (LOWERCASE + DIGITS)
        )
    ):
        errors.append(
            'The password should contain at least one non alpha-numeric character'
        )

    if (
        check_capital
        and not any(
            d in pw for d in UPPERCASE
        )
    ):
        errors.append(
            'The password should contain at least one non uppercase character'
        )

    return errors
