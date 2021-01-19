from jivago.config.properties.application_properties import ApplicationProperties
from jivago.inject.annotation import Component, Singleton
from jivago.lang.annotations import Inject


@Component
@Singleton
class ConversionConfig(object):
    max_dpi: int
    temp_directory: str

    @Inject
    def __init__(self, application_properties: ApplicationProperties):
        self.max_dpi = application_properties.get("max_dpi") or 300
        self.temp_directory = application_properties.get("temp_directory") or "/tmp/pdfinvert"
