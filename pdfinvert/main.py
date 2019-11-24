import os
from typing import Type, List, Union

from jivago.config.production_jivago_context import ProductionJivagoContext
from jivago.jivago_application import JivagoApplication
from jivago.wsgi.filter.filter import Filter

import pdfinvert.wsgi
from pdfinvert.wsgi.filter.temporary_file_cleanup_filter import TemporaryFileCleanupFilter


class InvertPdfContext(ProductionJivagoContext):

    def get_default_filters(self) -> List[Union[Filter, Type[Filter]]]:
        return super().get_default_filters() + [TemporaryFileCleanupFilter]


application = JivagoApplication(pdfinvert.wsgi, context=InvertPdfContext)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))

    application.run_dev(port=port, host="0.0.0.0")
