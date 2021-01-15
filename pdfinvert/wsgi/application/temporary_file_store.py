from typing import List

from jivago.inject.annotation import Component, RequestScoped


@Component
@RequestScoped
class TemporaryFileStore(object):

    def __init__(self):
        self.content = []

    def add(self, filename: str):
        self.content.append(filename)

    def get(self) -> List[str]:
        return self.content
