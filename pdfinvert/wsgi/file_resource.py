import logging
import os
import subprocess
import uuid

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.lang.annotations import Inject
from jivago.wsgi.annotations import Resource
from jivago.wsgi.methods import POST
from jivago.wsgi.request.request import Request
from jivago.wsgi.request.response import Response


@Resource("/convert")
class FileResource(object):

    @Inject
    def __init__(self, properties: ApplicationProperties):
        self.temp_dir = properties.get("temp_directory")

    @POST
    def post_file(self, request: Request) -> Response:
        filename = os.path.join(self.temp_dir, str(uuid.uuid4())) + ".pdf"
        new_filename = os.path.join(self.temp_dir, str(uuid.uuid4())) + ".pdf"

        dpi = 125
        if "HTTP_DPI" in request.headers.keys():
            dpi = int(request.headers["HTTP_DPI"])

        with open(filename, 'wb') as f:
            f.write(request.body)

        subprocess.call(f"""convert -density {dpi} -negate {filename} {new_filename} """.split(" ")[:-1])

        with open(new_filename, 'rb') as f:
            body = f.read()
        return Response(200, {}, body)
