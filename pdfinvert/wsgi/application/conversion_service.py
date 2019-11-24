import subprocess
from jivago.lang.annotations import Inject
from jivago.lang.registry import Component

from pdfinvert.wsgi.application.temporary_filepath_factory import TemporaryFilePathFactory


@Component
class ConversionService(object):

    @Inject
    def __init__(self, temporary_file_factory: TemporaryFilePathFactory):
        self.temporary_file_factory = temporary_file_factory

    def convert(self, filepath: str, dpi: int) -> str:
        flattened_file = self.temporary_file_factory.generate_temporary_pdf_filepath()

        subprocess.check_call(f"""convert -flatten -density {dpi} {filepath} {flattened_file} """.split(" ")[:-1])

        final_file = self.temporary_file_factory.generate_temporary_pdf_filepath()
        subprocess.check_call(f"""convert -density {dpi} -negate {flattened_file} {final_file} """.split(" ")[:-1])

        return final_file
