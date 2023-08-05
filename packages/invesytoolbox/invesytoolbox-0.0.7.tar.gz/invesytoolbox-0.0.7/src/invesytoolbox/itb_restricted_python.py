# -*- coding: utf-8 -*-
"""
=======================
restricted_python_tools
=======================

This module implements basic Python functionality missing in restricted Python.
"""


def contains_all(
    container: list,
    contained: list
) -> bool:
    """ Check if a list is contained in another list

    .. note:: 'all' is not available in restricted Python

    :param contained: the list to check if its contained
    :param container: the list to check it it containes the other one
    """

    return all(el in container for el in contained)


def contains_any(
    container: list,
    contained: list
) -> bool:
    """ Check if at list one element of a list is contained in another list

    .. note:: 'any' is not available in restricted Python

    :param contained: the list to check if its contained
    :param container: the list to check it it containes the other one
    """

    return any(el in container for el in contained)


def remove_duplicates(lst: list) -> list:
    """ Removes duplicates from a list

    .. note:: restricted Python does not allow sets
    """

    return list(set(lst))
