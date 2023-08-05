"""This module contains the management of the data format

Classes
-------


"""
from ._formats import Formats, FormatsAccess, FormatKeyNotFoundError, FormatDatabaseError
from ._factory import formatsServices

__all__ = ['Formats',
           'FormatsAccess',
           'formatsServices',
           'FormatKeyNotFoundError',
           'FormatDatabaseError'
           ]
