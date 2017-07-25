#!/usr/bin/python3
"""Prints a SHSA model."""

import argparse

from model.shsamodel import SHSAModel, SHSANodeType

# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('-m', '--model', type=str,
                    default="../config/shsamodel1.yaml",
                    help="SHSA model in a config file.")
args = parser.parse_args()

# yaml example
model = SHSAModel(configfile=args.model)
model.write_dot("uc_print_model", "pdf")
print(model)
