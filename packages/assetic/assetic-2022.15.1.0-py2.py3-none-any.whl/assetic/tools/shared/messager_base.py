import abc
import logging

import six


@six.add_metaclass(abc.ABCMeta)
class MessagerBase:

    def __init__(self):
        self._logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger("assetic")

            if self._logger is None:
                self._logger = logging.getLogger(__file__)

        return self._logger

    @abc.abstractmethod
    def new_message(self, msg, *args):
        pass
