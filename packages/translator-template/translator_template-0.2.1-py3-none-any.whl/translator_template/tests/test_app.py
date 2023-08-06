import os
from io import BytesIO
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from translator_template.app import generate, generate_to_file
from translator_template.templates import EPILOG, PROLOG

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def test_generate_to_file():
    with TemporaryDirectory() as dir:
        in_file = os.path.join(TEST_DIR, "data", "test.txt")
        out_file = os.path.join(dir, "test.docx")
        generate_to_file(in_file, out_file)


def test_generate():
    in_file = os.path.join(TEST_DIR, "data", "test.txt")
    zip_bytes = generate(in_file)
    zip_file = BytesIO(zip_bytes)
    with ZipFile(zip_file) as zip:
        with zip.open("word/document.xml") as docx:
            xml = docx.read().decode("utf8")
            assert xml.startswith(PROLOG)
            assert xml.endswith(EPILOG)
