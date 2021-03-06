#! /usr/bin/env python2.7
#
# __author__ Denise Ratasich
# __date__ 2017-10-05
#
# Plots execution times collected by ex3.py or ex4.py.
#

import argparse
import numpy as np
import matplotlib.pyplot as plt

# parse arguments
parser = argparse.ArgumentParser(description="""Plots average execution time of
SHSA (best).""")
parser.add_argument("--ymax", type=float,
                    help="max limit y to plot")
parser.add_argument("csvfile", type=str,
                    help="file containing results of ex[3|4].py")
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
et['SH-PGSA (best)'] = data['shsa_et'] / data['shsa_n']
et['ORR'] = data['orr_et'] / data['orr_n']

# get branch
# CAVEAT: assumes the depth is sorted in the csvfile!
branch = np.unique(data['branch'])

# get number of experiments per depth
firstbranch = data['branch'][0]
m = len(filter(lambda i: i == firstbranch, data['branch']))

print "branch: " + str(branch)
print "different models: " + str(m)

# split per branch
et_split = {}
for name, data in et.items():
    et_split[name] = np.split(data, len(data)/m)

# measures to plot
et_measures = {}
# create arrays (element for each branch) for measures per algorithm
for name in et_split.keys():
    et_measures[name] = {}
    et_measures[name]['avg'] = []
    et_measures[name]['std'] = []
    et_measures[name]['min'] = []
    et_measures[name]['max'] = []
# calculate measures per branch
for name, data in et_split.items():
    for a in data:
        et_measures[name]['avg'].append(np.mean(a))
        et_measures[name]['std'].append(np.std(a))
        et_measures[name]['min'].append(min(a))
        et_measures[name]['max'].append(max(a))

print "avg: "
for name in et_measures.keys():
    print "  " + name + ": " + str(et_measures[name]['avg'])


print
print "=== plotting ==================================================="
print

print "* plots"

fig = plt.figure(figsize=(8,3))


# styles
styles = [['-', '--', '-.'], ['r', 'g', 'b'], ['+', '+', '+'], ['x', 'x', 'x']]
names = et_measures.keys()

def linestyle(name):
    return styles[0][names.index(name)]

def color(name):
    return styles[1][names.index(name)]

def marker(name):
    return styles[2][names.index(name)]

def marker_max(name):
    return styles[3][names.index(name)]


# errorbar (assumes data is normally distributed)
for name, measure in et_measures.items():
    y = np.array(measure['avg'])
    ystd = np.array(measure['std'])
    # keep all values of y positive (std deviation cut at 0)
    ylower = np.maximum(1e-4, y - ystd)
    ystdlower = y - ylower
    plt.errorbar(branch, y, yerr=[ystdlower, ystd], label=name,
                 linestyle=linestyle(name), marker=marker(name),
                 color=color(name))

# plot additionally the min-max values
for name, measure in et_measures.items():
    plt.plot(branch, measure['max'], linestyle='', marker=marker_max(name),
             color=color(name))

# # boxplot
# plt.boxplot(startup, positions=startup_n)
# plt.boxplot(shutdown, positions=shutdown_n)

#plt.title("Overhead of starting a node in ROS")
plt.xlabel("branching factor")
plt.xlim(0,max(branch))
plt.ylabel("time (s)")
plt.ylim(0,args.ymax)
plt.legend(loc='upper left')

plt.show()
