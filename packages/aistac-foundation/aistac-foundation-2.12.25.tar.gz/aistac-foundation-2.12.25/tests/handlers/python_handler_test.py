import unittest
import os
import shutil

from aistac import ConnectorContract
from aistac.handlers.python_handlers import PythonSourceHandler, PythonPersistHandler
from aistac.properties.property_manager import PropertyManager


class PythonHandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # clean out any old environments
        for key in os.environ.keys():
            if key.startswith('HADRON'):
                del os.environ[key]

        os.environ['HADRON_PM_PATH'] = os.path.join('work', 'config')
        os.environ['HADRON_DEFAULT_PATH'] = os.path.join('work', 'data')
        try:
            os.makedirs(os.environ['HADRON_PM_PATH'])
            os.makedirs(os.environ['HADRON_DEFAULT_PATH'])
        except:
            pass
        PropertyManager._remove_all()

    def tearDown(self):
        try:
            shutil.rmtree('work')
        except:
            pass

    def test_change_flags(self):
        """Basic smoke test"""
        file = os.path.join(os.environ['HADRON_DEFAULT_PATH'], 'test.txt')
        open(file, 'a').close()
        cc = ConnectorContract(uri=file, module_name='', handler='')
        source = PythonSourceHandler(cc)
        self.assertTrue(source.has_changed())
        _ = source.load_canonical()
        self.assertFalse(source.has_changed())
        source.reset_changed(True)
        self.assertTrue(source.has_changed())
        source.reset_changed()
        self.assertFalse(source.has_changed())
        # touch the file
        os.remove(file)
        with open(file, 'a'):
            os.utime(file, None)
        self.assertTrue(source.has_changed())

    def test_raise(self):
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
