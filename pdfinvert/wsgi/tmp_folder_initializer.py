import os
import shutil

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.config.startup_hooks import PostInit
from jivago.lang.annotations import Inject
from jivago.lang.runnable import Runnable


@PostInit
class TmpFolderInitializer(Runnable):

    @Inject
    def __init__(self, properties: ApplicationProperties):
        self.properties = properties

    def run(self):
        directory = self.properties.get("temp_directory")

        if os.path.isdir(directory):
            shutil.rmtree(directory)

        os.mkdir(directory)
