# -*- coding: utf-8 -*-
"""
=================
email_phone_tools
=================
"""

from typing import Union
import phonenumbers
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

from itb_locales import get_locale

mycountry = get_locale().get('country')


def create_email_message(
    mail_from: str,
    subject: str,
    text: str,
    mail_to: str = None,
    cc: str = None,
    bcc: str = None,
    html: str = None,
    attachments: list = None,
    encoding: str = 'utf-8'
) -> str:
    """ Create a valid email message

    .. note:: it is possible to not have a **mail_to**, if there is a **cc** or **bcc**.
    """

    if attachments:
        msg = MIMEMultipart('mixed')
    elif text and html:
        msg = MIMEMultipart('alternative')
    else:
        msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = mail_from

    if not (mail_to or cc or bcc):
        raise Exception(
            'mailMessage needs mail_to or cc or bcc!'
        )

    if mail_to:
        msg['To'] = mail_to
    if cc:
        msg['CC'] = cc
    if bcc:
        msg['BCC'] = bcc

    parts = []
    parts.append(MIMEText(text, 'plain', encoding))

    if html:
        parts.append(MIMEText(html, 'html', encoding))

    for attachment in attachments or []:
        attPart = MIMEBase(
            'application',
            'octet-stream'
        )
        attPart.set_payload(attachment['data'])
        encoders.encode_base64(attPart)
        attPart.add_header(
            'Content-Disposition',
            f"attachment; filename={attachment['filename']}"
        )
        parts.append(attPart)

    for part in parts:
        msg.attach(part)

    return msg


def process_phonenumber(
    phonenumber: str,
    numberfmt: str = 'international',
    checkonly: bool = False,
    empty_if_invalid: bool = False,
    country=mycountry
) -> Union[str, bool]:
    """ Checks if a phonenumber is valid returns in specified format.

    :param phonenumber: phone number string to be processed
    :param numberfmt: format in which the number is returned

        * international (default)
        * national
        * E164 (international, condensed)

    :param checkonly: only check if the number is valid (returns boolean)
    :param empty_if_invalid: returns an empty string if the number is not valid
        (only if checkonly is False)
    """

    phonenumber = ''.join(c for c in phonenumber if c in '01234567890+')

    try:
        pn = phonenumbers.parse(phonenumber, country)  # country code will be parsed nonetheless
    except phonenumbers.phonenumberutil.NumberParseException:
        error_str = ' (not a phone number)'
        return phonenumber + error_str

    error_str = ''

    if not phonenumbers.is_possible_number(pn):
        if checkonly:
            return False
        else:
            error_str = ' (impossible)'

    elif not phonenumbers.is_valid_number(pn):
        if checkonly:
            return False
        else:
            error_str = ' (invalid)'

    if checkonly:
        return True
    else:
        if empty_if_invalid and error_str:
            return ''

        try:
            phonefmt = getattr(phonenumbers.PhoneNumberFormat, numberfmt.upper())
        except AttributeError:
            raise AttributeError('numberfmt must be "international", "national" or "E164"!')

        return phonenumbers.format_number(
            pn,
            phonefmt
        ) + error_str
