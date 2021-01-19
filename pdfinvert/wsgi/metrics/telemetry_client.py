import logging
import os
import shutil

from jivago.config.properties.system_environment_properties import SystemEnvironmentProperties
from jivago.inject.annotation import Component, Singleton
from jivago.lang.annotations import Inject, Override
from jivago.lang.runnable import Runnable
from jivago.scheduling.annotations import Scheduled, _Interval
from prometheus_client import Counter, CollectorRegistry, Histogram, Gauge
from prometheus_client.exposition import push_to_gateway

from pdfinvert.wsgi.config.conversion_config import ConversionConfig


@Component
@Singleton
class TelemetryClient(object):

    @Inject
    def __init__(self, environment: SystemEnvironmentProperties):
        self.endpoint = environment.get("PROMETHEUS_GATEWAY_ENDPOINT")
        self.registry = CollectorRegistry()
        self.get_request_counter = Counter("invertpdf_get_request_count", "Number of successful GET requests",
                                           registry=self.registry)
        self.post_request_counter = Counter("invertpdf_post_request_count", "Number of successful POST requests",
                                            registry=self.registry)
        self.duration_histogram = Histogram("invertpdf_request_duration_ms", "Request duration",
                                            registry=self.registry,
                                            buckets=[0, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 30000, 60000,
                                                     1800000, 3600000]
                                            )
        self.failure_counter = Counter("invertpdf_failed_requests", "Number of failed requests",
                                       registry=self.registry)

        self.requests_in_progress = Gauge("invertpdf_requests_in_progress", "Number of pending requests",
                                          registry=self.registry)
        self.free_disk = Gauge("invertpdf_free_disk_space", "Free disk space on tmpfs", registry=self.registry)
        self.logger = logging.getLogger(self.__class__.__name__)

    def track_request(self, method: str, duration: int):
        self.logger.info(f"Request took {duration}ms.")
        self.duration_histogram.observe(duration)
        if method == "GET":
            self.get_request_counter.inc()
        elif method == "POST":
            self.post_request_counter.inc()

    def track_failure(self, method: str, duration: int):
        self.failure_counter.inc()
        self.duration_histogram.observe(duration)

    def track_start(self):
        self.requests_in_progress.inc()

    def track_end(self):
        self.requests_in_progress.dec()

    def submit(self):
        push_to_gateway(self.endpoint, "invertpdf", self.registry)


@Scheduled(every=_Interval(15))
@Component
class TelemetryUploadWorker(Runnable):
    # TODO remove and serve metrics directly from a resource instead - keotl - 2021-01-19
    @Inject
    def __init__(self, telemetry_client: TelemetryClient, config: ConversionConfig):
        self.telemetry_client = telemetry_client
        self.temp_dir = config.temp_directory
        self.logger = logging.getLogger(self.__class__.__name__)

    @Override
    def run(self):
        try:
            if os.environ.get("PROMETHEUS_GATEWAY_ENDPOINT"):
                try:
                    self.telemetry_client.free_disk.set(shutil.disk_usage(self.temp_dir).free)
                except Exception as e:
                    self.logger.warning(f"Error while reading free disk space. {e}")
                self.telemetry_client.submit()
        except Exception as e:
            self.logger.warning(f"Could not push telemetry data. {e}")
