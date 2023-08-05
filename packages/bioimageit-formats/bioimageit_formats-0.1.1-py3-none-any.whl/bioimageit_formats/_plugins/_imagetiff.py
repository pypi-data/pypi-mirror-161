from skimage.io import imread
from .._reader import FormatReader


class ImagetiffServiceBuilder:
    """Service builder for the imagetiff reader"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = ImagetiffReaderService()
        return self._instance


class ImagetiffReaderService(FormatReader):
    """Reader for Tiff images

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(filename):
        return imread(filename)
