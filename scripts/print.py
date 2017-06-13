#!/usr/bin/python
"""
Prints a SHSA config file to pdf.
"""

import argparse
import os.path
import sys

sys.path.append('../shsa')
from model.shsamodel import SHSAModel

# parse args
desc = "Prints a SHSA model in yaml as pdf."
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('-o', '--output', default="out",
                    help="""Output file name (pdf).""")
parser.add_argument(dest='model',
                    help="""Path to SHSA model as yaml file.""")
args = parser.parse_args()

# load
model = SHSAModel(configfile=args.model)

# name and output format (e.g., pdf, eps, ..)
root, ext = os.path.splitext(args.output)
# default output format if not specified
if len(ext) == 0:
    ext = 'pdf'
else:
    ext = ext[1:]

# print
model.write_dot(root, ext)
