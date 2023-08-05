# -*- coding: utf-8 -*-
"""BioImageIT formats module.

This module contains classes that allows to read
avaliable data format in BioImageIT

Example
-------
    You need to use the ConfigAccess which is a singleton to read config

    >>> # first call to load the configuration
    >>> FormatsAccess("formats.json")
    >>> # or
    >>> FormatsAccess.instance().load("formats.json")
    >>>
    >>> # then to access the config variables
    >>> format_ = FormatsAccess.instance().get('format_name')

Classes
-------
Formats
FormatsAccess

"""

import os
import json


class FormatKeyNotFoundError(Exception):
    """Raised when key is not found in the config"""

    pass


class FormatDatabaseError(Exception):
    """Raised when key is not found in the config"""

    pass


class Format:
    """Container for a data format information

    Attributes
    ---------
    name: str
        Name (unique ID) of the format
    extension: str
        File extension (ex: csv)
    reader: str
        Name of the data reader plugin (for viewer)
    viewer:
        Name of the Viewer plugin for this format

    """
    def __init__(self):
        self.name = ""
        self.extension = ""
        self.reader = ""
        self.viewer = ""

    def print(self):
        print('format information:')
        print(f'    name: {self.name}')
        print(f'    extension: {self.extension}')
        print(f'    reader: {self.reader}')
        print(f'    viewer: {self.viewer}')


class Formats:
    """Allows to access data formats dictionary

    The format object can be instantiate manually but the
    usage is to instantiate it with the singleton FormatAccess

    Parameters
    ----------
    formats_file
        File where the formats information are stored in JSON format

    Attributes
    ----------
    formats
        Dictionary containing the formats information

    """

    def __init__(self, formats_file: str = ''):
        self.formats_file = formats_file
        self.formats = []
        self.formats_names = []
        if formats_file != '':
            self.load(formats_file)

    def load(self, formats_file: str):
        """Read the metadata from the a json file"""
        self.formats_file = formats_file
        if os.path.getsize(self.formats_file) > 0:
            with open(self.formats_file) as json_file:
                tmp = json.load(json_file)
                if 'formats' in tmp:
                    for format_ in tmp['formats']:
                        format_data = Format()
                        format_data.name = format_['name']
                        format_data.extension = format_['extension']
                        format_data.reader = format_['reader']
                        format_data.viewer = format_['viewer']
                        self.formats.append(format_data)
                        self.formats_names.append(format_data.name)
                else:
                    raise FormatKeyNotFoundError('No key formats'
                                                 ' in the format base')
        # print('formats=', self.formats)

    def names(self):
        """Get all the formats names

        Returns
        -------
        list of the formats names

        """
        return self.formats_names

    def is_format(self, name: str) -> bool:
        """Check if a name exists in the format dictionary

        Parameters
        ----------
        name
            Key to check

        Returns
        -------
        bool
            True if the key exists, False otherwise

        """
        if name in self.formats_names:
            return True
        else:
            return False

    def get(self, name: str) -> dict:
        """Read a variable from the config dictionary

        Parameters
        ----------
        name
            Name of the format to query

        Returns
        -------
        dict of the format information

        Raises
        ------
        FormatKeyNotFoundError: if the name key does not exists

        """
        for format_ in self.formats:
            if format_.name == name:
                return format_
        else:
            raise FormatKeyNotFoundError('No key ' + name +
                                         ' in the format base')


class FormatsAccess:
    """Singleton to access the Formats

    Parameters
    ----------
    formats_file
        JSON file where the formats is stored

    Raises
    ------
    Exception: if multiple instantiation of the Formats is tried

    """

    __instance = None

    def __init__(self, formats_file: str):
        """ Virtually private constructor. """
        if os.path.exists(formats_file):
            FormatsAccess.__instance = Formats(formats_file)
        else:
            raise FormatDatabaseError(f'The format database file {formats_file} cannot be not found')    

    @staticmethod
    def instance():
        """ Static access method to the Config. """
        if FormatsAccess.__instance is None:
            FormatsAccess.__instance = Formats()
        return FormatsAccess.__instance
