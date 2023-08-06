import unittest
import io
import logging
import json
from datetime import datetime
from newtools import log_to_stdout, PersistentFieldLogger


class PersistentFieldLoggerTest(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        # This line will give _coverage_ to the code in logger.py, but it does not in any way test the intent
        self.pfl = PersistentFieldLogger(log_to_stdout(), {"filename": "something.csv"})
        self.pfl.logger.addHandler(self.handler)

    def test_basic_logging(self):
        self.pfl.debug("This will not appear")
        self.pfl.info("message", "suffix",  **{"message": "prefix"}, )
        self.pfl.info("info", **{"reason": "testing info"})
        self.pfl.warning("warning", **{"filename": "override val"}, )
        # self.pfl.warning({"message": "test dict as arg", "filename": "override val 2"})
        self.pfl.error(**{"message": "error", "filename": "override val"}, )
        self.handler.flush()
        self.stream.seek(0)
        a = self.stream.readlines()

        a = [json.loads(d) for d in a]
        expected_vals = [
            # demos behaviour if you specify a message prefix
            {"message": "prefix message suffix", "filename": "something.csv"},
            # persistent args are present
            {"message": "info", "reason": "testing info", "filename": "something.csv",},
            # reason is gone - not assigned here
            {"message": "warning", "filename": "override val"},
            # filename overriden again
            {"message": "error", "filename": "override val"},
            ]

        for index, expected_val in enumerate(expected_vals):
            self.assertEqual(a[index], expected_val)

    def test_dict_should_fail(self):
        """if you let it accept dictionaries as args, it can break in weird ways, hence this"""
        with self.assertRaises(ValueError):
            self.pfl.info({"message": "this would result in weird behaviour, so crash instead"})

    def test_set_field_value(self):
        # set new value
        self.pfl.set_field_value("some_new_field", "value")
        self.pfl.info("message_value")
        # set existing value
        self.pfl.set_field_value("filename", "override")
        self.pfl.info("message_value2")
        pass

    def test_non_serializable_single_value(self):
        with self.assertRaises(TypeError):
            self.pfl.set_field_value("this should crash", datetime.now())

    def test_set_multiple_values(self):
        self.pfl.set_multiple_values({"some_new_field": "", "field2": ""})

    def test_non_serializable_multiple_values(self):
        with self.assertRaises(TypeError):
            self.pfl.set_multiple_values({"this should crash": datetime.now()})
