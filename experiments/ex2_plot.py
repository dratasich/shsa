#! /usr/bin/env python
#
# __author__ Denise Ratasich
# __date__ 2017-10-03
#
# Plots execution times collected by ex2.py.
#

import argparse
import numpy as np
import matplotlib.pyplot as plt

# parse arguments
parser = argparse.ArgumentParser(description="""Plots average execution time of
SHSA (best).""")
parser.add_argument("csvfile", type=str,
                    help="file containing results of ex2.py")
args = parser.parse_args()


print
print "=== loading ===================================================="
print

# convert csvs to numpy array
data = np.genfromtxt(args.csvfile, comments='%',
                     delimiter=',', names=True)

print "data: " + str(data.dtype.names)


print
print "=== prepare ===================================================="
print

# divide exec time by number of calls
et = {}
et['SHSA (best)'] = data['shsa_et'] / data['shsa_n']
et['ORR'] = data['orr_et'] / data['orr_n']
et['DFS'] = data['dfs_et'] / data['dfs_n']

# get depth
# CAVEAT: assumes the depth is sorted in the csvfile!
depth = np.unique(data['depth'])

# get number of experiments per depth
firstdepth = data['depth'][0]
m = len(filter(lambda i: i == firstdepth, data['depth']))

print "depth: " + str(depth)
print "different models: " + str(m)

# split per depth
et_split = {}
for name, data in et.items():
    et_split[name] = np.split(data, len(data)/m)

# measures to plot
et_measures = {}
# create arrays (element for each depth) for measures per algorithm
for name in et_split.keys():
    et_measures[name] = {}
    et_measures[name]['avg'] = []
    et_measures[name]['std'] = []
    et_measures[name]['min'] = []
    et_measures[name]['max'] = []
# calculate measures per depth
for name, data in et_split.items():
    for a in data:
        et_measures[name]['avg'].append(np.mean(a))
        et_measures[name]['std'].append(np.std(a))
        et_measures[name]['min'].append(min(a))
        et_measures[name]['max'].append(max(a))


print
print "=== plotting ==================================================="
print

print "* plots"

fig = plt.figure(figsize=(8,4))

# errorbar (assumes data is normally distributed)
for name, measure in et_measures.items():
    plt.errorbar(depth, measure['avg'], yerr=measure['std'], label=name)

# plot additionally the min-max values
for name, measure in et_measures.items():
    plt.plot(depth, measure['min'], 'b+')

# # boxplot
# plt.boxplot(startup, positions=startup_n)
# plt.boxplot(shutdown, positions=shutdown_n)

#plt.title("Overhead of starting a node in ROS")
plt.xlabel("depth")
plt.xlim(0,max(depth))
plt.ylabel("time (s)")
#plt.ylim(0,1)
plt.legend()

plt.show()
