import logging
import os
import sys


class AMLLogger:
    def __init__(self):
        # initializing logger
        level = os.getenv("AZUREML_LOG_LEVEL", "INFO")
        formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        azureml_logger = logging.getLogger("azureml")
        azureml_logger.setLevel(level)
        azureml_logger.addHandler(stream_handler)

        # NOTE: This doesn't get the actual root logger. Instead, it creates a new logger called "root"
        # in Python < 3.9.
        # See https://github.com/python/cpython/issues/81923. There are two problems here:
        #   1) We don't end up configuring the root logger
        #   2) We will see duplicated logs in Python >= 3.9 because the root logger will end up
        #      with two StreamHandlers.
        self.logger = logging.getLogger("root")
        self.logger.setLevel(level)
        self.logger.addHandler(stream_handler)
        self.logger.propagate = False

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
