import os
import logging


class Logger:
    def __init__(self):
        pass

    @classmethod
    def format_message(cls, message, logging_info=None):
        formatted_message = "{} {}"
        return formatted_message.format(logging_info if logging_info else "", message)

    @classmethod
    def info(cls, message, logging_info=None):
        message_to_print = cls.format_message(message, logging_info)
        if os.getenv('IS_DEV'):
            print(message_to_print)
        else:
            logging.info(message_to_print)

    @classmethod
    def error(cls, message, logging_info=None):
        message_to_print = cls.format_message(message, logging_info)
        if os.getenv('IS_DEV'):
            print(message_to_print)
        else:
            logging.error(message_to_print)

    @classmethod
    def warning(cls, message, logging_info=None):
        message_to_print = cls.format_message(message, logging_info)
        if os.getenv('IS_DEV'):
            print(message_to_print)
        else:
            logging.warning(message_to_print)
