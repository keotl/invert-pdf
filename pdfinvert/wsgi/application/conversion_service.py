import subprocess

from jivago.inject.annotation import Component
from jivago.lang.annotations import Inject

from pdfinvert.wsgi.application.temporary_filepath_factory import TemporaryFilePathFactory
from pdfinvert.wsgi.exceptions import ConversionException


@Component
class ConversionService(object):

    @Inject
    def __init__(self, temporary_file_factory: TemporaryFilePathFactory):
        self.temporary_file_factory = temporary_file_factory

    def convert(self, filepath: str, dpi: int) -> str:
        flattened_file = self.temporary_file_factory.generate_temporary_pdf_filepath()

        try:
            page_count = int(subprocess.check_output(f"""identify {filepath} | wc -l""", shell=True))
        except Exception as e:
            raise ConversionException()

        final_file = self.temporary_file_factory.generate_temporary_pdf_filepath()

        subprocess.check_call(f"convert -density {dpi} {filepath} {flattened_file}-%04d.pdf ".split(" ")[:-1])
        for i in range(0, page_count):
            subprocess.check_call(
                f"convert -density {dpi} -flatten {filepath}[{i}] {flattened_file.strip('.pdf')}-{i:04d}.pdf ".split(
                    " ")[:-1])
            subprocess.check_call(
                f"convert -density {dpi} -negate {flattened_file.strip('.pdf')}-{i:04d}.pdf {flattened_file.strip('.pdf')}-{i:04d}.inverted.pdf ".split(
                    " ")[:-1])

        subprocess.check_call(
            f"convert -density {dpi} {flattened_file.strip('.pdf')}-%04d.inverted.pdf[0-{page_count - 1}] {final_file} ".split(
                " ")[:-1])

        return final_file
