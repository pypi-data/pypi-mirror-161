from abc import abstractmethod


class CustomException(Exception):

    @property
    @abstractmethod
    def status_code(self):
        pass

    @property
    @abstractmethod
    def message(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def serialize_exception() -> dict:
        pass
