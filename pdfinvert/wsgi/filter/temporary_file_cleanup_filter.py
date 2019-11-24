import os
from glob import glob

from jivago.inject.annotation import Component
from jivago.lang.annotations import Override, Inject
from jivago.lang.stream import Stream
from jivago.wsgi.filter.filter import Filter
from jivago.wsgi.filter.filter_chain import FilterChain
from jivago.wsgi.request.request import Request
from jivago.wsgi.request.response import Response

from pdfinvert.wsgi.application.temporary_file_store import TemporaryFileStore


@Component
class TemporaryFileCleanupFilter(Filter):

    @Inject
    def __init__(self, temporary_file_store: TemporaryFileStore):
        self.temporary_file_store = temporary_file_store

    @Override
    def doFilter(self, request: Request, response: Response, chain: FilterChain):
        try:
            self.temporary_file_store.init()
            chain.doFilter(request, response)
        finally:
            files = self.temporary_file_store.get()
            Stream(files) \
                .map(lambda f: glob(f"{f}*")) \
                .flat() \
                .forEach(os.remove)
            self.temporary_file_store.clear()
