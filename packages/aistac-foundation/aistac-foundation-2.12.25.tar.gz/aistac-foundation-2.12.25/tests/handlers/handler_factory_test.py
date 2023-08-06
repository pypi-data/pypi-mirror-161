from aistac.handlers.abstract_handlers import HandlerFactory, ConnectorContract
import unittest


class HandlerFactoryTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_runs(self):
        """Basic smoke test"""
        HandlerFactory()

    def test_exceptions(self):
        # Bad module
        connector_contract = ConnectorContract(uri='example.csv;file_type=csv',
                                               module_name='aistac.handlers.none',
                                               handler='PythonSourceHandler',
                                               kwargs={'sep': ',', 'encoding': 'latin1'})
        with self.assertRaises(ModuleNotFoundError) as context:
            HandlerFactory.instantiate(connector_contract)
        self.assertTrue("The module 'aistac.handlers.none' could not be found" in str(context.exception))
        # bad handler
        connector_contract = ConnectorContract(uri='example.csv', module_name='aistac.handlers.python_handlers',
                                               handler='none')
        with self.assertRaises(ImportError) as context:
            HandlerFactory.instantiate(connector_contract)
        self.assertTrue("The handler 'none' could not be found in the module 'aistac.handlers.python_handlers'" in str(context.exception))
        # Everything correct
        connector_contract = ConnectorContract(uri='example.csv', module_name='aistac.handlers.python_handlers',
                                               handler='PythonSourceHandler')
        handler = HandlerFactory.instantiate(connector_contract)
        self.assertEqual("<class 'aistac.handlers.python_handlers.PythonSourceHandler'>", str(type(handler)))

    def test_handler_check(self):
        # Module
        result = HandlerFactory.check_module('aistac.handlers.python_handlers')
        self.assertTrue(result)
        result = HandlerFactory.check_module('aistac.handlers.none')
        self.assertFalse(result)
        # Handdler
        result = HandlerFactory.check_handler(module_name='aistac.handlers.python_handlers', handler='PythonSourceHandler')
        self.assertTrue(result)
        result = HandlerFactory.check_handler(module_name='aistac.handlers.None', handler='PythonSourceHandler')
        self.assertFalse(result)
        result = HandlerFactory.check_handler(module_name='aistac.handlers.python_handlers', handler='None')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
