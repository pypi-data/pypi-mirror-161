# -*- coding: utf-8 -*-
"""
===============
www_tools
===============
"""
import urllib.parse

def change_query_string(
    url: str = None,
    query_string: str = None,
    params: dict = None,
    delete_remaining: bool = False,
    returning='auto'
):
    """
    Change arguments in a query string

    :param returning: values: url, query_string or auto
    """
    if not params:
        raise TypeError('change_query_string needs a "params" argument!')

    if returning == 'auto':
        if url:
            returning = 'url'
        elif query_string:
            returning = 'query_string'

    if url:
        url_parts = urllib.parse.urlparse(url)
        query = dict(urllib.parse.parse_qsl(url_parts.query))
    elif query_string:
        if not url and returning == 'url':
            raise Exception('an url is needed to return an url (only query string provided)')
        query = dict(urllib.parse.parse_qsl(query_string))
    else:
        raise TypeError('change_query_string needs an "url" or "query_string" argument!')

    if delete_remaining:
        query = params
    else:
        query.update(params)

    new_query_string = urllib.parse.urlencode(query)

    if returning == 'query_string':
        return new_query_string

    if returning == 'url':
        new_url = url_parts._replace(query=urllib.parse.urlencode(query)).geturl()
        return new_url
