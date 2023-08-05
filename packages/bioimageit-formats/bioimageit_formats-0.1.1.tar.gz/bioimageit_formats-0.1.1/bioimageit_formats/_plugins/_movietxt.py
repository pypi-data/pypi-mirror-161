import os
import numpy as np
from skimage.io import imread
from .._reader import FormatReader


class MovietxtServiceBuilder:
    """Service builder for the movietxt reader"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = MovietxtReaderService()
        return self._instance


class MovietxtReaderService(FormatReader):
    """Reader for txt movies images"""
    def __init__(self):
        super().__init__()

    @staticmethod
    def files(filename):
        dir_ = os.path.dirname(filename)
        filenames = [filename]
        with open(filename, 'r') as file_content:
            for line in file_content:
                filenames.append(os.path.join(dir_, line.strip()))
        return filenames

    @staticmethod
    def read(filename):
        files = MovietxtReaderService.files(filename)
        frames = []
        for file in files:
            if file != filename:
                frames.append(imread(file))
        return np.stack(frames)
