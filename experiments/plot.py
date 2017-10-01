#!/usr/bin/env python3

import argparse
import yaml



# parse arguments
parser = argparse.ArgumentParser(description="""Plots sth.""")
parser.add_argument("experiment", type=str,
                    help="""Experiment's output (YAML).""")
args = parser.parse_args()

data = None
with open(args.experiment, 'r') as f:
    try:
        data = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)

print(data)
