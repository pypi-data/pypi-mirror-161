from io import BytesIO
from os import path
from typing import IO, Union
from zipfile import ZipFile

from .parse import read
from .templates import EPILOG, PROLOG, PAGE, PANEL, QUOTE


def generate_to_file(in_spec: Union[str, IO], out_spec: Union[str, IO]) -> None:
    """Read the input specification from in_spec, and generate a Word document to out_spec.

    :param in_spec: Either a path to the input specification, or a stream containing it.
    :type in_spec: Union[str, IO]
    :param out_spec: Either a path to the generated docx, or a stream into which the docx will be written.
    :type out_spec: Union[str, IO]
    :returns: Nothing
    """
    bytes = generate(in_spec)

    try:
        if hasattr(out_spec, "write"):
            f = out_spec
        else:
            f = open(out_spec, "wb")

        f.write(bytes)
    finally:
        if f != out_spec:
            f.close()


def generate(in_spec: Union[str, IO]) -> bytes:
    """Read the input specification from in_spec, and generate a Word document to a byte buffer.

    :param in_spec: Either a path to the input specification, or a stream containing it.
    :type in_spec: Union[str, IO]
    :returns: docx blob
    :rtype: bytes
    """
    with _load_zip() as stream:
        with ZipFile(stream, mode="a") as zip:
            doc = _generate(in_spec)
            zip.writestr("word/document.xml", doc)
        return stream.getvalue()


def _load_zip() -> IO:
    zip_path = path.join(path.dirname(path.abspath(__file__)), "data", "test.docx")
    with open(zip_path, "rb") as f:
        stream = BytesIO(f.read())
    return stream


def _generate(in_spec: Union[str, IO]) -> str:
    chunks = [PROLOG]
    try:
        if hasattr(in_spec, "read"):
            f = in_spec
        else:
            f = open(in_spec, "rt")

        for page, panels in read(f):
            chunks.append(PAGE.format(page))
            for panel in range(panels):
                chunks.append(PANEL.format(panel + 1))
                chunks.append(QUOTE)
        chunks.append(EPILOG)
        return "".join(chunks)
    finally:
        if f != in_spec:
            f.close()
