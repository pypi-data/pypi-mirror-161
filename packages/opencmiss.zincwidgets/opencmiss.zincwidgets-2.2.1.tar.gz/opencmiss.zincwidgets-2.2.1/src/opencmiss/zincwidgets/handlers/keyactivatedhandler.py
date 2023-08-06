
from abc import ABC

from opencmiss.zincwidgets.handlers.abstracthandler import AbstractHandler


class KeyActivatedHandler(AbstractHandler, ABC):

    def __init__(self, key_code):
        super(KeyActivatedHandler, self).__init__()
        self._key_code = key_code

    def get_key_code(self):
        return self._key_code
