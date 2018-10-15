import os
import uuid

import subprocess

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.lang.annotations import Inject
from jivago.templating.rendered_view import RenderedView
from jivago.wsgi.annotations import Resource
from jivago.wsgi.methods import GET, POST
from jivago.wsgi.request.request import Request
from jivago.wsgi.request.response import Response


@Resource("/2x2")
class PdfnupResource(object):

    @Inject
    def __init__(self, properties: ApplicationProperties):
        self.temp_dir = properties.get("temp_directory")

    @GET
    def get(self) -> RenderedView:
        return RenderedView("2x2.html", {})

    @POST
    def post(self, request: Request) -> Response:
        filename = os.path.join(self.temp_dir, str(uuid.uuid4())) + ".pdf"
        new_filename = os.path.join(self.temp_dir, str(uuid.uuid4())) + ".pdf"

        with open(filename, 'wb') as f:
            f.write(request.body)

        subprocess.call(("""pdfnup --nup 2x2 """ + filename + """ --papersize {8.5in,11in} -o """ + new_filename).split(" "))

        with open(new_filename, 'rb') as f:
            body = f.read()
        return Response(200, {}, body)
