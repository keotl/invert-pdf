import logging
import os
from typing import Type, List, Union

from jivago.config.production_jivago_context import ProductionJivagoContext
from jivago.jivago_application import JivagoApplication
from jivago.lang.annotations import Override
from jivago.wsgi.filter.filter import Filter

import pdfinvert.wsgi
from pdfinvert.wsgi.filter.request_metrics_filter import RequestMetricsFilter
from pdfinvert.wsgi.filter.temporary_file_cleanup_filter import TemporaryFileCleanupFilter


class InvertPdfContext(ProductionJivagoContext):
    LOGGER = logging.getLogger("InvertPdfContext")

    @Override
    def get_default_filters(self) -> List[Union[Filter, Type[Filter]]]:
        filters = super().get_default_filters()

        prometheus_endpoint = os.environ.get("PROMETHEUS_GATEWAY_ENDPOINT")
        if prometheus_endpoint:
            InvertPdfContext.LOGGER.info(f"Using prometheus pushgateway endpoint {prometheus_endpoint}")
            filters = [RequestMetricsFilter] + filters

        return filters + [TemporaryFileCleanupFilter]


logging.getLogger().setLevel(logging.INFO)

application = JivagoApplication(pdfinvert.wsgi, context=InvertPdfContext)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))

    application.run_dev(port=port, host="0.0.0.0")
