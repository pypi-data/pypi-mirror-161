"""Define the interface of a format reader class

Classes
-------
FormatReader

"""


class FormatReader:
    """Class that implements a format read function

    """
    def __init__(self):
        pass

    @staticmethod
    def files(filename):
        """Get the list of all the datafile

        Some data formats have a main file and sub files. This method aims
        at getting all the sub files for one data

        Parameters
        ----------
        filename: str
            Path of the file

        Returns
        -------
        A list of all the sub files path
        """

        return [filename]

    @staticmethod
    def read(filename):
        """Read a file data into a python object

        Parameters
        ----------
        filename: str
            Path of the file

        Returns
        -------
        The file data in a python object
        """
        return None
