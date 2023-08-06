import os
from io import BytesIO, StringIO
from tempfile import TemporaryDirectory
from typing import IO, Union
from zipfile import ZipFile

from translator_template.generator import generate, generate_to_file
from translator_template.templates import EPILOG, PROLOG

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def test_generate_to_file():
    with TemporaryDirectory() as dir:
        in_file = os.path.join(TEST_DIR, "data", "test.txt")
        out_file = os.path.join(dir, "test.docx")
        generate_to_file(in_file, out_file)
        _assert_docx(out_file)


def test_generate_to_file_from_stream():
    with open(os.path.join(TEST_DIR, "data", "test.txt"), "rt") as f_in:
        in_stream = StringIO(f_in.read())
        out_stream = BytesIO()
        generate_to_file(in_stream, out_stream)
        out_stream.seek(0)
        _assert_docx(out_stream)


def test_generate():
    in_file = os.path.join(TEST_DIR, "data", "test.txt")
    zip_bytes = generate(in_file)
    _assert_docx(zip_bytes)


def test_generate_from_stream():
    with open(os.path.join(TEST_DIR, "data", "test.txt"), "rt") as f:
        in_stream = StringIO(f.read())
        zip_bytes = generate(in_stream)
        _assert_docx(zip_bytes)


def _assert_docx(stream_bytes_or_path: Union[IO, bytes, str]):
    def _assert_zip(zip_file):
        with ZipFile(zip_file) as zip:
            with zip.open("word/document.xml") as docx:
                xml = docx.read().decode("utf8")
                assert xml.startswith(PROLOG)
                assert xml.endswith(EPILOG)

    if hasattr(stream_bytes_or_path, "read"):
        _assert_zip(stream_bytes_or_path)
    elif isinstance(stream_bytes_or_path, bytes):
        _assert_zip(BytesIO(stream_bytes_or_path))
    else:
        with open(stream_bytes_or_path, "rb") as f:
            _assert_zip(f)
