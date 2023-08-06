import argparse
from os import path

from .generator import generate_to_file


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
