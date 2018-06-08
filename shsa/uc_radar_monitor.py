#!/usr/bin/env python3
"""Test radar monitor."""

import argparse
import numpy as np
import itertools

from monitor.shsamonitor import SHSAMonitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel


# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('-m', '--model', type=str,
                    default="../config/radar-tracking.yaml",
                    help="SHSA model in a config file.")
parser.add_argument('csv', type=str,
                    help="CSV log file of itoms.")
args = parser.parse_args()


# create monitor
model = SHSAModel(configfile=args.model)
x_monitor = SHSAMonitor(model=model, domain='x')
y_monitor = SHSAMonitor(model=model, domain='y')
# specify available itoms manually (do not match the csv)


#
# Data
#
# The data consists of rows of track observations per sensor and
# timestamp. Each sensor creates a track for an observed vehicle. Track IDs per
# sensors are unique (increase with every new detected vehicle). The position
# (and velocity) included in each track observation are the itoms to
# monitor.
#
# Additionally the monitor saves the last observation of a track observed by a
# sensor.

# open and parse csv
print("Load data...")
data = np.genfromtxt(args.csv, delimiter=',', comments='%', names=True)
header = data.dtype.names
print("{} columns with names {}".format(len(data[0]), data.dtype.names))
print("first row: {}".format(data[0]))


#
# Maintain track id pairs
#
# Pair the tracks corresponding to the same vehicle, when the vehicle changes
# from one sensor s1 to sensor s2 (i.e., vanishes from the field of view of
# sensor s1). To that end, the distance between all pairs of the vanished track
# s1 to all tracks of s2 is calculated. The nearest track of s2 is selected if
# its below a maximum offset (around vehicle size / lane width).

def distance(track_a, track_b):
    x = header.index('x')
    y = header.index('y')
    return (track_a[x] - track_b[x])**2 + (track_a[y] - track_b[y])**2

def find_match(track, possible_tracks, max_off=6):
    """Find a matching track id for the given id.

    track -- The track for which to find a matching track from another sensor.
    possible_tracks -- Tracks from another neighbor sensor.

    Returns the id of the nearest track iff the distance is below the maximum
    offset.

    """
    track_match = None
    track_distance = max_off+1.0
    # find best match (nearest track) in possible_tracks
    for tid, t in possible_tracks.items():
        d = distance(track, t)
        if d < max_off and d < track_distance:
            track_match = tid
            track_distance = d
    return track_match

def update_id_pairs(s1, s2, track_id_pairs):
    """Appends unmatched tracks in s1 to track_id_pairs."""
    matched_ids = [pair[0] for pair in track_id_pairs]
    for tid1, t1 in s1.items():
        # try to find a near track for all unmatched tracks
        if tid1 not in matched_ids:
            tid2 = find_match(t1, s2)
            # add new pair if successful
            if tid2 is not None:
                track_id_pairs.append([tid1, tid2])
    return track_id_pairs

def pair(s1, s2, track_id_pairs):
    """Returns pairs of tracks, i.e., tracks that can be compared.

    s1 -- all tracks of sensor 1.
    s2 -- all tracks of sensor 2.
    track_id_pairs -- ID pairs of tracks of s1 and s2.

    """
    pairs = []
    # collect available ids of the sensor's tracks
    for tid1, tid2 in track_id_pairs:
        try:
            t1 = s1[tid1]
            t2 = s2[tid2]
            pairs.append([t1, t2])
        except:
            # tracks may vanish from view, ignore
            # (pair gets unused at some point)
            pass
    return pairs

def check_pair(track_a, track_b):
    x = header.index('x')
    y = header.index('y')
    itoms = {
        'x': track_a[x],
        'y': track_a[y],
        'x_nbr': track_b[x],
        'y_nbr': track_b[y],
    }
    status_x = x_monitor.monitor(itoms)
    status_y = y_monitor.monitor(itoms)
    status = {itom: max(status_x[itom], status_y[itom]) for itom in status_x.keys()}
    return status

# assume track ids are unique throughout the run (ids are not re-used when out
# of range)
track_id_pairs_s6 = []  # pairs s7 <--> s6
track_id_pairs_s8 = []  # pairs s7 <--> s8

def check(sensors, sensors_last):
    """Check itoms in sensor 7 domain."""
    if sensors is None:
        return None
    # default
    status = None
    # make the monitoring concrete here
    try:
        s6 = sensors[6]
        s7 = sensors[7]
        s8 = sensors[8]
    except:
        # if we don't have data from neighboring sensors, abort
        return
    # associate tracks from one sensor to the other
    global track_id_pairs_s6
    global track_id_pairs_s8
    track_id_pairs_s6 = update_id_pairs(s7, s6, track_id_pairs_s6)
    track_id_pairs_s8 = update_id_pairs(s7, s8, track_id_pairs_s8)
    track_pairs_6 = pair(s7, s6, track_id_pairs_s6)
    track_pairs_8 = pair(s7, s8, track_id_pairs_s8)
    # check s7 against the neighbors
    if not track_pairs_6 and not track_pairs_8:
        print("no track pairs")
        return
    for track_under_test, track_redundant in track_pairs_6:
        status = check_pair(track_under_test, track_redundant)
    for track_under_test, track_redundant in track_pairs_8:
        status = check_pair(track_under_test, track_redundant)
    print(status)


#
# Simulate monitoring over time: shift data into monitor
#

print("Monitor...")
t = -1.0
sensors = None  # stores the current observation of the tracks per sensor
sensors_last = {}  # keeps the last observation of a track per sensor
status = None
for row in data:
    # gather itoms as long as its the same timestamp
    if row['time'] != t:
        # new timestamp
        t = row['time']
        # check the itoms gathered during the last period
        check(sensors, sensors_last)
        # reset current observations per sensor
        sensors = {}
    # create a list of tracks for each sensor
    sid = row['sensor']
    if sid not in sensors.keys():
        sensors[sid] = {}  # key: sensor ID
    if sid not in sensors_last.keys():
        sensors_last[sid] = {}  # key: sensor ID
    # prepare itoms
    tid = row['track']
    # save track observation
    sensors[sid][tid] = row
    # save last observation of a track (redundancy for forward estimation)
    sensors_last[sid][tid] = row
