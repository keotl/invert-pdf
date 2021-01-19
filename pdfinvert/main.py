import logging
import os

from jivago.config.production_jivago_context import ProductionJivagoContext
from jivago.config.router.filtering.filtering_rule import FilteringRule
from jivago.config.router.router_builder import RouterBuilder
from jivago.jivago_application import JivagoApplication
from jivago.wsgi.routing.routing_rule import RoutingRule
from jivago.wsgi.routing.serving.static_file_routing_table import StaticFileRoutingTable

import pdfinvert.wsgi
from pdfinvert import static
from pdfinvert.wsgi.filter.request_metrics_filter import RequestMetricsFilter
from pdfinvert.wsgi.filter.temporary_file_cleanup_filter import TemporaryFileCleanupFilter


class InvertPdfContext(ProductionJivagoContext):
    LOGGER = logging.getLogger("InvertPdfContext")

    def create_router_config(self) -> RouterBuilder:
        config = super().create_router_config() \
            .add_rule(FilteringRule("*", [TemporaryFileCleanupFilter])) \
            .add_rule(RoutingRule("/static/",
                                  StaticFileRoutingTable(os.path.dirname(static.__file__),
                                                         allowed_extensions=[".png", ".ico", ".html", ".css"])))

        prometheus_endpoint = os.environ.get("PROMETHEUS_GATEWAY_ENDPOINT")
        if prometheus_endpoint:
            InvertPdfContext.LOGGER.info(f"Using prometheus pushgateway endpoint {prometheus_endpoint}")
            config.add_rule(FilteringRule("*", [RequestMetricsFilter]))

        return config


logging.getLogger().setLevel(logging.INFO)

application = JivagoApplication(pdfinvert.wsgi, context=InvertPdfContext)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))

    application.run_dev(port=port, host="0.0.0.0")
