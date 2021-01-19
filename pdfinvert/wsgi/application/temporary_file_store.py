import threading
from typing import List

from jivago.inject.annotation import Component, Singleton


@Component
@Singleton
class TemporaryFileStore(object):

    def __init__(self):
        self.content = threading.local()

    def init(self):
        self.content.files = []

    def add(self, filename: str):
        self.content.files.append(filename)

    def get(self) -> List[str]:
        return self.content.files

    def clear(self):
        self.content.files = []
