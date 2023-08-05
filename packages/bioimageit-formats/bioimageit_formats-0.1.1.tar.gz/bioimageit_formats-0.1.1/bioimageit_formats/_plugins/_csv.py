import os

import pandas as pd
import numpy as np
from .._reader import FormatReader


class TableCSVServiceBuilder:
    """Service builder for the tablecsv reader"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = TableCSVReaderService()
        return self._instance


class TableCSVReaderService(FormatReader):
    """Reader for Tiff images

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(filename):
        return pd.read_csv(filename)


class ArrayCSVServiceBuilder:
    """Service builder for the arraycsv reader"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = ArrayCSVReaderService()
        return self._instance


class ArrayCSVReaderService(FormatReader):
    """Reader for Tiff images

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(filename):
        return pd.read_csv(filename, nrows=1)


class NumberCSVServiceBuilder:
    """Service builder for the numbercsv reader"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = NumberCSVReaderService()
        return self._instance


class NumberCSVReaderService(FormatReader):
    """Reader for Tiff images

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(filename):
        return pd.read_csv(filename, nrows=1)    
              