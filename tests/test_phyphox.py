import unittest
import os
import json
import phyphox


FOLDER_NAME = os.path.dirname(__file__)


class TestPhyphoxMethods(unittest.TestCase):
    def test_meta(self):
        file_name = "/meta_1.bin"
        meta_data = None
        try:
            with open(FOLDER_NAME + file_name) as fd:
                meta_data = fd.read()
        except FileNotFoundError:
            print("File not found {} in unit test".format(file_name, FOLDER_NAME))
            raise FileNotFoundError
        x = phyphox.PhyphoxLogger("127.0.0.1",8080)
        x._PhyphoxLogger__req_answers["meta"] =  json.loads(meta_data)
        x.get_meta()
        self.assertEqual(x.get_meta_key('deviceModel'), 'iPhone14,5')

    def test_config(self):
        file_name = "/config_1.bin"
        config_data = None
        try:
            with open(FOLDER_NAME + file_name) as fd:
                config_data = fd.read()
        except FileNotFoundError:
            print("File not found {} in unit test".format(file_name, FOLDER_NAME))
            raise FileNotFoundError
        x = phyphox.PhyphoxLogger("127.0.0.1",8080)
        x._PhyphoxLogger__req_answers["config"] =  json.loads(config_data)
        x.get_config()
        self.assertEqual(x._PhyphoxLogger__experiment.get('title'), 'Magnetometer')

if __name__ == '__main__':
    unittest.main()