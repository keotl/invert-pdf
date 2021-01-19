from time import time

from jivago.inject.annotation import Component
from jivago.lang.annotations import Override, Inject
from jivago.wsgi.filter.filter import Filter
from jivago.wsgi.filter.filter_chain import FilterChain
from jivago.wsgi.request.request import Request
from jivago.wsgi.request.response import Response

from pdfinvert.wsgi.metrics.telemetry_client import TelemetryClient


@Component
class RequestMetricsFilter(Filter):

    @Inject
    def __init__(self, telemetry_client: TelemetryClient):
        self.telemetry_client = telemetry_client

    @Override
    def doFilter(self, request: Request, response: Response, chain: FilterChain):
        start_time = self._now()
        self.telemetry_client.track_start()
        try:
            chain.doFilter(request, response)

            if response.status > 400:
                if response.status != 404:  # Ignore random crawlers
                    self.telemetry_client.track_failure(request.method, self._now() - start_time)
            else:
                self.telemetry_client.track_request(request.method, self._now() - start_time)
        finally:
            self.telemetry_client.track_end()

    def _now(self) -> int:
        return int(time() * 1000)
