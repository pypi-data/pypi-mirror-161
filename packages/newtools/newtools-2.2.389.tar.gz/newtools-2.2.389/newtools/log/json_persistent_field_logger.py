import logging
import re as regex_extractor
import traceback
from newtools.optional_imports import json_log_formatter

CLASS_NAME = 'ClassName'
ERROR_MESSAGE = 'ErrorMessage'
ERROR_STACK_TRACE = 'ErrorStackTrace'
DEFAULT_CLASS_NAME = 'None'

CLASS_NAME_SEARCH_PATTERN = "<class '([^\'>]+)"


class JSONLogger:
    """
    This is a wrapper of logging library where the logs are displayed in the json format.

    This wrapper has the feature of Persistent logging and can be used optionally as well.
    """
    log_instance = None
    persistent_fields = dict()

    json_formatter = None

    def __init__(self, logger_name, logging_level=logging.INFO, log_file_path=None):
        """
        This class creates a logging instance with json formatted messages and adds an optional feature
        for persisting any fields onto the log messages as and when required.

        :param logger_name: Any string with valid understandable name.
        :param logging_level: Any kind of logging level from where the lowest prioritized log level is required
            if used logging.DEBUG - All levels Debug, Info, Warning and Error logs are logged.
            if used logging.INFO - levels Info, Warning and Error logs are logged.
            if used logging.WARNING - levels Warning and Error logs are logged.
            if used logging.ERROR - Only Error logs are logged.
        :param log_file_path: In case to save the logs onto a json file.
        """
        self.persistent_fields = dict()
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers.clear()
        logger_instance.setLevel(logging_level)

        self.json_formatter = json_log_formatter.JSONFormatter()

        if log_file_path is None:
            generic_handler = logging.StreamHandler()
        else:
            generic_handler = logging.FileHandler(log_file_path)
        generic_handler.setFormatter(self.json_formatter)

        logger_instance.addHandler(generic_handler)
        self.log_instance = logger_instance

    def remove_persistent_field(self, field_name):
        """
        This function helps in removing a key value pair to the persistent field dictionary.

        :param field_name: key to be removed from the persistent field dictionary.

        :return: None
        """
        self.persistent_fields.pop(field_name, None)

    def add_persistent_field(self, field_name, field_value):
        """
        This function helps in adding a key value pair to the persistent field dictionary.

        :param field_name: key to be saved in the persistent field dictionary.
        :param field_value: value to be saved for the given key

        :return: None
        """
        self.persistent_fields[field_name] = field_value

    def add_persistent_fields(self, **fields):
        """
        This function helps in adding a set of key value pairs to the persistent field dictionary.

        :param fields: A set of keyword arguments to be saved to the persistent field dictionary.

        :return: None
        """
        self.persistent_fields = {**self.persistent_fields, **fields}

    def _handle_log_parameters(self, excess_persistent_dict, kwargs):
        """
        This function adds excess persistent fields provided to the debug, info, error, warning. Apart from that
        any excess non-persistent fields passed to the below methods will be logged but not persisted.

        :param excess_persistent_dict: excess persistent dict to be added to instance persistence dictionary.
        :param kwargs: Excess non-persistent dict to be logged with the log message called for with below methods.

        :return: All persistent and non-persistent key value pairs which are to be logged.
        """
        if excess_persistent_dict is not None:
            self.add_persistent_fields(**excess_persistent_dict)
        logging_params = {**self.persistent_fields, **kwargs}
        return logging_params

    def _extract_and_persist_exception(self, persist_exception_object):
        """
        This function adds the exception extracted details to the Persistent Field Dictionary. This function
        overrides the current exception stack details persisted with the new exception stack details if
        provided any.

        :param persist_exception_object: exception object to retrieve exception details and stack trace.
        """
        class_name_search = regex_extractor.search(CLASS_NAME_SEARCH_PATTERN, str(type(persist_exception_object)))

        self.add_persistent_field(CLASS_NAME, class_name_search.group(1) if class_name_search else DEFAULT_CLASS_NAME)
        self.add_persistent_field(ERROR_MESSAGE, str(persist_exception_object))
        self.add_persistent_field(ERROR_STACK_TRACE, str(traceback.format_exc()))

    def debug(self, message, excess_persistent_dict=None, **kwargs):
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.debug(message, extra=logging_params)

    def info(self, message, excess_persistent_dict=None, **kwargs):
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.info(message, extra=logging_params)

    def warning(self, message, excess_persistent_dict=None, **kwargs):
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.warning(message, extra=logging_params)

    def error(self, message, excess_persistent_dict=None, persist_exception_object=None, **kwargs):
        if persist_exception_object is not None:
            self._extract_and_persist_exception(persist_exception_object)
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.error(message, extra=logging_params)
