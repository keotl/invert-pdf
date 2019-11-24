import os
import uuid

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.inject.annotation import Component
from jivago.lang.annotations import Inject

from pdfinvert.wsgi.application.temporary_file_store import TemporaryFileStore


@Component
class TemporaryFilePathFactory(object):

    @Inject
    def __init__(self, properties: ApplicationProperties, temporary_file_store: TemporaryFileStore):
        self.temporary_file_store = temporary_file_store
        self.temp_dir = properties.get("temp_directory")

    def generate_temporary_pdf_filepath(self) -> str:
        path = os.path.join(self.temp_dir, str(uuid.uuid4())) + ".pdf"
        self.temporary_file_store.add(path)
        return path
