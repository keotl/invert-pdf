from jivago.config.properties.application_properties import ApplicationProperties
from jivago.config.properties.system_environment_properties import SystemEnvironmentProperties
from jivago.inject.annotation import Component, Singleton
from jivago.lang.annotations import Inject


@Component
@Singleton
class ConversionConfig(object):
    max_dpi: int
    temp_directory: str
    cleanup_enabled: bool

    @Inject
    def __init__(self, application_properties: ApplicationProperties, env: SystemEnvironmentProperties):
        self.max_dpi = application_properties.get("max_dpi") or 300
        self.temp_directory = application_properties.get("temp_directory") or "/tmp/pdfinvert"
        self.cleanup_enabled = (application_properties.get("cleanup_job") or env.get("CLEANUP_JOB") or "false") in ("true", "True", "yes", "enabled")
