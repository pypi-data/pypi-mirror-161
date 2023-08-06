# scan_merge

This is a simple tool to merge scanned PDFs if you have scanner with a document
feeder but that doesn't support double sided pages.

The idea is to scan the document stack into two PDFs, a forward one of the front
of the pages and a backward one with the back of the pages. Then this script can
be used to merge the two into a coherent single PDF with the pages in order.

# Install

It is recommended to install this from PyPi:

```
pip install scan-merge
```
