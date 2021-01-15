import logging
import subprocess
from glob import glob
from typing import Union

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.inject.annotation import Component
from jivago.lang.annotations import Inject

from pdfinvert.wsgi.application.queueing.control.completion_token_awaiter import CompletionTokenAwaiter
from pdfinvert.wsgi.application.queueing.conversion_queue import JobQueue
from pdfinvert.wsgi.application.queueing.queued_job import QueuedJob
from pdfinvert.wsgi.application.temporary_filepath_factory import TemporaryFilePathFactory
from pdfinvert.wsgi.exceptions import ConversionException, ConversionTimeoutException


@Component
class ConversionService(object):

    @Inject
    def __init__(self, temporary_file_factory: TemporaryFilePathFactory, conversion_queue: JobQueue,
                 application_properties: ApplicationProperties):
        self.timeout: Union[int, None] = application_properties.get("timeout")
        self.conversion_queue = conversion_queue
        self.temporary_file_factory = temporary_file_factory
        self.logger = logging.getLogger(self.__class__.__name__)

    def convert(self, filepath: str, dpi: int) -> str:
        flattened_file = self.temporary_file_factory.generate_temporary_pdf_filepath()

        page_count = int(subprocess.check_output(f"""identify {filepath} | wc -l""", shell=True))

        final_file = self.temporary_file_factory.generate_temporary_pdf_filepath()

        try:
            subprocess.check_call(f"convert -density {dpi} {filepath} {flattened_file}-%04d.pdf ".split(" ")[:-1])
        except Exception as e:
            self.logger.error(f"Error while splitting PDF file. {e}")
            raise ConversionException()

        commands = []
        for frame in glob(f"{flattened_file}-*"):
            commands.append(f"convert -density {dpi} -flatten {frame} {frame} ".split(" ")[:-1])
            commands.append(f"convert -density {dpi} -negate {frame} {frame}.inverted.pdf ".split(" ")[:-1])

        token = self.conversion_queue.enqueue(QueuedJob(final_file, commands))

        CompletionTokenAwaiter(token,
                               on_failure=ConversionException(),
                               timeout=self.timeout,
                               on_timeout=ConversionTimeoutException()) \
            .wait()

        subprocess.check_call(
            f"convert -density {dpi} {flattened_file}-%04d.pdf.inverted.pdf[0-{page_count - 1}] {final_file} ".split(
                " ")[:-1])

        return final_file
