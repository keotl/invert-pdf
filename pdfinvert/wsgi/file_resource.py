from jivago.lang.annotations import Inject
from jivago.wsgi.annotations import Resource
from jivago.wsgi.methods import POST
from jivago.wsgi.request.request import Request
from jivago.wsgi.request.response import Response

from pdfinvert.wsgi.application.conversion_service import ConversionService
from pdfinvert.wsgi.application.temporary_filepath_factory import TemporaryFilePathFactory


@Resource("/convert")
class FileResource(object):

    @Inject
    def __init__(self, temporary_file_factory: TemporaryFilePathFactory, conversion_service: ConversionService):
        self.conversion_service = conversion_service
        self.temporary_file_factory = temporary_file_factory

    @POST
    def post_file(self, request: Request) -> Response:
        filename = self.temporary_file_factory.generate_temporary_pdf_filepath()

        dpi = 120
        if "HTTP_DPI" in request.headers.keys():
            dpi = int(request.headers["HTTP_DPI"])

        with open(filename, 'wb') as f:
            f.write(request.body)

        new_filename = self.conversion_service.convert(filename, dpi)

        with open(new_filename, 'rb') as f:
            body = f.read()
        return Response(200, {}, body)
