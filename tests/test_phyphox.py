import unittest
import unittest.mock
import os
import urllib.request
import json
import phyphox


FOLDER_NAME = os.path.dirname(__file__)

class TestPhyphoxMethods(unittest.TestCase):
    @unittest.mock.patch('urllib.request.urlopen')
    def test_meta(self, mock_urlopen):
        file_name = "/meta_1.bin"
        meta_data = None
        try:
            with open(FOLDER_NAME + file_name) as fd:
                meta_data = fd.read()
        except FileNotFoundError:
            print("File not found {} in unit test".format(file_name, FOLDER_NAME))
            raise FileNotFoundError
        cm = unittest.mock.MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = meta_data
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm
        x = phyphox.Logger("0.0.0.0",8080)
        x.get_meta()
        self.assertEqual(x.get_meta_key('deviceModel'), 'iPhone14,5')
        self.assertEqual(x.get_meta_key('build'), '17272')
        self.assertEqual(x.get_meta_key('deviceRelease'), '18.6.2')
        self.assertEqual(x.get_meta_key('fileFormat'), '1.19')

    @unittest.mock.patch('urllib.request.urlopen')
    def test_config(self, mock_urlopen):
        file_name = "/config_1.bin"
        config_data = None
        try:
            with open(FOLDER_NAME + file_name) as fd:
                config_data = fd.read()
        except FileNotFoundError:
            print("File not found {} in unit test".format(file_name, FOLDER_NAME))
            raise FileNotFoundError
        cm = unittest.mock.MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = config_data
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm
        x = phyphox.Logger("0.0.0.0",8080)
        x.get_config()
        self.assertEqual(x._Logger__experiment.get('localTitle'), 'Magnétomètre')
        self.assertEqual(x._Logger__experiment.get('buffers'), [{"size":0,"name":"mag_time"},{"name":"mag","size":0},{"size":0,"name":"magX"},{"size":0,"name":"magY"},{"size":0,"name":"magAccuracy"},{"size":0,"name":"magZ"}])
        self.assertEqual(x._Logger__experiment.get('crc32'), 'e04c0bfa')
        self.assertEqual(x._Logger__experiment.get('category'), 'Raw Sensors')

if __name__ == '__main__':
    unittest.main()