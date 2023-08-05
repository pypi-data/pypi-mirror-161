import unittest
import os
import os.path

from bioimageit_formats import FormatsAccess

class TestRequest(unittest.TestCase):
    def setUp(self):
        FormatsAccess(os.path.join('tests', 'formats.json'))

    def tearDown(self):
        pass

    def test_csv_table(self):
        extension = FormatsAccess.instance().get('tablecsv').extension
        self.assertEquals(extension, 'csv')

    def test_csv_array(self):
        extension = FormatsAccess.instance().get('arraycsv').extension
        self.assertEquals(extension, 'csv')        

    def test_csv_number(self):
        extension = FormatsAccess.instance().get('numbercsv').extension
        self.assertEquals(extension, 'csv')  
