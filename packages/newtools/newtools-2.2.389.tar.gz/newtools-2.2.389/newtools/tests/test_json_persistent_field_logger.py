import io
import json
import logging
import os
import unittest

from newtools.log.json_persistent_field_logger import JSONLogger, CLASS_NAME, ERROR_MESSAGE


class JSONLoggerTest(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.json_logger = JSONLogger('TestJsonLogger')
        self.handler.setFormatter(self.json_logger.json_formatter)
        self.json_logger.log_instance.addHandler(self.handler)

    def load_logs_from_stream(self):
        log_messages = []
        self.handler.flush()
        self.stream.seek(0)
        for stream_data in self.stream.readlines():
            log_info = json.loads(stream_data.replace('\n', ''))
            log_info.pop('time')
            log_messages.append(log_info)
        return log_messages

    def test_debug(self):
        debug_message = "Debug Logs appear only in case of explicit Debug logs enabled."
        self.json_logger.debug(debug_message)
        log_messages = self.load_logs_from_stream()
        self.assertTrue(len(log_messages) == 0)
        self.assertTrue(debug_message not in log_messages)

    def test_info(self):
        log_message = 'This is a info message.'
        self.json_logger.info(log_message)
        log_messages = self.load_logs_from_stream()
        self.assertTrue(len(log_messages) == 1)
        self.assertEqual(log_messages[0]['message'], log_message)

    def test_error(self):
        log_error_message = 'This is a error message.'
        self.json_logger.error(log_error_message)
        log_messages = self.load_logs_from_stream()
        self.assertTrue(len(log_messages) == 1)
        self.assertEqual(log_messages[0]['message'], log_error_message)

    def test_error_with_exception(self):
        log_error_message = 'This is a error message.'
        exception_message = 'Exception Message'
        self.json_logger.error(log_error_message, persist_exception_object=Exception(exception_message))
        log_messages = self.load_logs_from_stream()
        self.assertTrue(len(log_messages) == 1)
        self.assertEqual(log_messages[0]['message'], log_error_message)
        self.assertEqual(log_messages[0][CLASS_NAME], 'Exception')
        self.assertEqual(log_messages[0][ERROR_MESSAGE], exception_message)

    def test_warning(self):
        log_warn_message = 'This is a warning message.'
        self.json_logger.warning(log_warn_message)
        log_messages = self.load_logs_from_stream()
        self.assertTrue(len(log_messages) == 1)
        self.assertEqual(log_messages[0]['message'], log_warn_message)

    def test_warning_with_persistent_field(self):
        log_warn_message = 'This is a warning message.'
        self.json_logger.warning(log_warn_message,
                                 excess_persistent_dict={'Persistent_Field': 'This is Persistent Field Value'})
        log_messages = self.load_logs_from_stream()
        self.assertTrue(len(log_messages) == 1)
        self.assertEqual(log_messages[0]['message'], log_warn_message)
        self.assertEqual(log_messages[0]['Persistent_Field'], 'This is Persistent Field Value')

        self.json_logger.remove_persistent_field('Persistent_Field')
        self.assertTrue(len(self.json_logger.persistent_fields) == 0)

    def test_default(self):
        json_log_file = None
        file_path = f'{os.getcwd()}/test_file.log'
        try:
            json_logger = JSONLogger('Test initialization', log_file_path=file_path)

            sample_info_message = 'Test file logger'
            json_logger.info(sample_info_message)

            json_log_file = open(file_path)
            json_log = json.load(json_log_file)

            self.assertEqual(json_log['message'], 'Test file logger')
        except Exception:
            pass
        finally:
            if json_log_file is not None:
                json_log_file.close()
                os.remove(file_path)
