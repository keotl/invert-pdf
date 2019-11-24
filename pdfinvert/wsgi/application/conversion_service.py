import subprocess
from glob import glob

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

        page_count = int(subprocess.check_output(f"""identify {filepath} | wc -l""", shell=True))

        final_file = self.temporary_file_factory.generate_temporary_pdf_filepath()

        subprocess.check_call(f"convert -density {dpi} {filepath} {flattened_file}-%04d.pdf ".split(" ")[:-1])
        for frame in glob(f"{flattened_file}-*"):
            subprocess.check_call(f"convert -density {dpi} -flatten {frame} {frame} ".split(" ")[:-1])
            subprocess.check_call(f"convert -density {dpi} -negate {frame} {frame}.inverted.pdf ".split(" ")[:-1])

        subprocess.check_call(f"convert -density {dpi} {flattened_file}-%04d.pdf.inverted.pdf[0-{page_count - 1}] {final_file} ".split(" ")[:-1])

        return final_file
