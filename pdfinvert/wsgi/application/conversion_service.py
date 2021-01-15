import logging
import subprocess
from datetime import datetime
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

        flatten_commands = []
        negate_commands = []
        for i in range(0, page_count):
            flatten_commands.append(
                f"convert -density {dpi} -flatten {filepath}[{i}] {flattened_file.strip('.pdf')}-{i:04d}.pdf ".split(
                    " ")[:-1])
            negate_commands.append(
                f"convert -density {dpi} -negate {flattened_file.strip('.pdf')}-{i:04d}.pdf {flattened_file.strip('.pdf')}-{i:04d}.inverted.pdf ".split(
                    " ")[:-1])

        start = datetime.now()
        token = self.conversion_queue.enqueue(QueuedJob(final_file + ":flatten", flatten_commands))
        CompletionTokenAwaiter(token,
                               on_failure=ConversionException(),
                               timeout=self.timeout,
                               on_timeout=ConversionTimeoutException()) \
            .wait()
        self.logger.debug(f"Completed flattenings in {datetime.now() - start}")

        token = self.conversion_queue.enqueue(QueuedJob(final_file + ":negate", negate_commands))
        CompletionTokenAwaiter(token,
                               on_failure=ConversionException(),
                               timeout=self.timeout,
                               on_timeout=ConversionTimeoutException()) \
            .wait()
        self.logger.debug(f"Completed negatings in {datetime.now() - start}")
        start = datetime.now()

        token = self.conversion_queue.enqueue(QueuedJob(final_file + ":concat", [
            f"convert -density {dpi} {flattened_file.strip('.pdf')}-%04d.inverted.pdf[0-{page_count - 1}] {final_file} ".split(
                " ")[:-1]]))

        CompletionTokenAwaiter(token,
                               on_failure=ConversionException(),
                               timeout=self.timeout,
                               on_timeout=ConversionTimeoutException()) \
            .wait()

        self.logger.debug(f"Completed reassembly in {datetime.now() - start}")
        return final_file
