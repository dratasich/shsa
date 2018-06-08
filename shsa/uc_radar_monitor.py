#!/usr/bin/python3
"""Test SHSA monitor."""

import argparse
import numpy as np

from monitor.shsamonitor import SHSAMonitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel


# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('-d', '--domain', type=str, default="s",
                    help="""Common domain (variable of the SHSA model) where
                    the itoms are compared against each other.""")
parser.add_argument('-m', '--model', type=str,
                    default="../config/radar-tracking.yaml",
                    help="SHSA model in a config file.")
parser.add_argument('csv', type=str,
                    help="CSV log file of itoms.")
args = parser.parse_args()


# create monitor
model = SHSAModel(configfile=args.model)
monitor = SHSAMonitor(model=model, domain=args.domain)


# open and parse csv
print("Load data...")
# use loadtxt to get 2D array right away
# however, no names with this function
#data = np.loadtxt(args.csv, delimiter=',', comments='%')
data = np.genfromtxt(args.csv, delimiter=',', comments='%', names=True)
header = data.dtype.names
print("{} columns with names {}".format(len(data[0]), data.dtype.names))
print("first row: {}".format(data[0]))


# simulate monitoring over time: shift data into monitor
print("Monitor...")
for row in data:
    itoms = {name: row[name] for name in header}
    status = monitor.monitor(itoms)
    print(",".join([str(status[name]) for name in header]))
