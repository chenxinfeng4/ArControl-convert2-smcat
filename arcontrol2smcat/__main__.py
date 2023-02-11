import sys
from .converter_cli import convert

filetxts = sys.argv[1:]
for filetxt in filetxts:
    convert(filetxt)