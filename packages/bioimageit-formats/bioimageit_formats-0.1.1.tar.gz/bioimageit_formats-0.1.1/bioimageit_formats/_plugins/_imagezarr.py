import zarr
from .._reader import FormatReader


class ImagezarrServiceBuilder:
    """Service builder for the imagetiff reader"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = ImagezarrReaderService()
        return self._instance


class ImagezarrReaderService(FormatReader):
    """Reader for zarr images

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(filename):
        return zarr.open(os.path.join(filename,"0", "0"), mode = 'r')
