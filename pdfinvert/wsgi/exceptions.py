from jivago.inject.annotation import Component
from jivago.lang.annotations import Override
from jivago.wsgi.filter.system_filters.error_handling.exception_mapper import ExceptionMapper
from jivago.wsgi.request.response import Response


class ConversionException(Exception):
    pass


@Component
class ConversionExceptionMapper(ExceptionMapper):
    @Override
    def handles(self, exception: Exception) -> bool:
        return isinstance(exception, ConversionException)

    @Override
    def create_response(self, exception: Exception) -> Response:
        return Response(400, {},
                        "An error occurred while converting this file. Make sure that you are uploading a valid PDF file and try again.")


class ConversionTimeoutException(Exception):
    pass


@Component
class ConversionTimeoutExceptionMapper(ExceptionMapper):

    @Override
    def handles(self, exception: Exception) -> bool:
        return isinstance(exception, ConversionTimeoutException)

    @Override
    def create_response(self, exception: Exception) -> Response:
        return Response(400, {},
                        "The operation took too long to complete. Try lowering the DPI or using smaller PDF files.")
