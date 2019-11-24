import os
import uuid

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.lang.annotations import Inject
from jivago.lang.registry import Component


@Component
class TemporaryFilePathFactory(object):

    @Inject
    def __init__(self, properties: ApplicationProperties):
        self.temp_dir = properties.get("temp_directory")

    def generate_temporary_pdf_filepath(self) -> str:
        return os.path.join(self.temp_dir, str(uuid.uuid4())) + ".pdf"
