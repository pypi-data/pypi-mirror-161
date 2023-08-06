#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""Tool to merge single-sided PDF scans of the same page stack into a double sided scan

This is useful if you have a scanner with a document feeder but no double sided
page support.
"""

import argparse
from itertools import zip_longest
from pathlib import Path

import argcomplete
from PyPDF2 import PdfFileWriter, PdfFileReader
from funcy import cat


def interleave_longest(*sequences):
    """Interleave sequences, substituting with None if a sequence ends early"""
    return cat(zip_longest(*sequences))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Tool to merge single-sided PDF scans of the same page stack into a double sided scan"
    )
    pdf_completer = argcomplete.FilesCompleter(allowednames=("pdf",))
    parser.add_argument(
        "front_file", type=Path, help="Path to PDF with fronts of pages (1,3,...)"
    ).completer = pdf_completer
    parser.add_argument(
        "back_file", type=Path, help="Path to PDF with backs of pages (2,4,...)"
    ).completer = pdf_completer
    parser.add_argument(
        "output_file", type=Path, help="Path of combined output file"
    ).completer = pdf_completer
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    output = PdfFileWriter()
    # Load the PDFs
    with args.front_file.open(mode="rb") as front_file, args.back_file.open(
        mode="rb"
    ) as back_file:
        input_front = PdfFileReader(front_file)
        input_back = PdfFileReader(back_file)
        # Generate combined sequence of pages from both PDFs
        combined = filter(
            bool, interleave_longest(input_front.pages, reversed(input_back.pages))
        )
        for page in combined:
            output.addPage(page)
        with args.output_file.open(mode="wb") as output_file:
            output.write(output_file)


if __name__ == "__main__":
    main()
