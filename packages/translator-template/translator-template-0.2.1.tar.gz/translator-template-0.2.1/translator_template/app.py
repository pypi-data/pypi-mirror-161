import argparse
from io import BytesIO
from os import path
from typing import IO, Union
from zipfile import ZipFile

from .parse import read
from .templates import EPILOG, PROLOG, PAGE, PANEL, QUOTE


def generate_to_file(in_file: str, out_file: Union[str, IO]) -> None:
    """Read the input specification from the in_file file, and generate a Word document at out_file."""
    bytes = generate(in_file)
    with open(out_file, "wb") as f:
        f.write(bytes)


def generate(in_file: str) -> bytes:
    """Read the input specification from the in_file file, and generate a Word document to a byte buffer."""
    with _load_zip() as stream:
        with ZipFile(stream, mode="a") as zip:
            doc = _generate(in_file)
            zip.writestr("word/document.xml", doc)
        return stream.getvalue()


def _load_zip() -> IO:
    zip_path = path.join(path.dirname(path.abspath(__file__)), "data", "test.docx")
    with open(zip_path, "rb") as f:
        stream = BytesIO(f.read())
    return stream


def _generate(in_file: str) -> str:
    chunks = [PROLOG]
    with open(in_file, "rt") as f:
        for page, panels in read(f):
            chunks.append(PAGE.format(page))
            for panel in range(panels):
                chunks.append(PANEL.format(panel + 1))
                chunks.append(QUOTE)
    chunks.append(EPILOG)
    return "".join(chunks)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Word Document from page/panel specification"
    )
    parser.add_argument("--in-file", help="input file name", required=True)
    parser.add_argument("--out-file", help="output file name")
    args = parser.parse_args()
    if args.out_file:
        out_file = args.out_file
    else:
        root, _ = path.splitext(args.in_file)
        out_file = root + ".docx"
    generate_to_file(args.in_file, out_file)
