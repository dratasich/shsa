#!/usr/bin/env python3
"""Test radar monitor."""

import argparse
import numpy as np
import csv
import os

from monitor.shsamonitor import SHSAMonitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel
from utils.logger import Logger


# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('-m', '--model', type=str,
                    default="../config/radar-tracking.yaml",
                    help="SHSA model in a config file.")
parser.add_argument('-s', '--sensor', type=int,
                    default=7,
                    help="Sensor ID to monitor.")
parser.add_argument('csv', type=str,
                    help="CSV log file of itoms.")
args = parser.parse_args()


#
# Log
#

# create folder for logs if not yet exists
if not os.path.exists("log"):
    os.makedirs("log")

pairs_logger = Logger('log/pairs.yaml', mode='w');


#
# Create monitors
#

model = SHSAModel(configfile=args.model)
x_monitor = SHSAMonitor(model=model, domain='x', logfile='log/monitor-log-x.yaml')
y_monitor = SHSAMonitor(model=model, domain='y', logfile='log/monitor-log-y.yaml')


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
    """Find a matching track in the set of possible ones for the given track.

    track -- The track for which to find a matching track from another sensor.
    possible_tracks -- Tracks from another neighbor sensor.

    Returns the id of the nearest track iff the distance is below the maximum
    offset.

    """
    track_match_id = None
    track_distance = max_off+1.0
    # find best match (nearest track) in possible_tracks
    for tid, t in possible_tracks.items():
        d = distance(track, t)
        if d < max_off and d < track_distance:
            track_match_id = int(tid)
            track_distance = d
    return track_match_id

def update_id_pairs(s1, s2, track_id_pairs):
    """Appends unmatched tracks in s1 to track_id_pairs.

    TODO: find additional id pairs with forward estimation
    """
    matched_ids = [pair[0] for pair in track_id_pairs]
    for tid1, t1 in s1.items():
        # try to find a near track for all unmatched tracks
        if tid1 not in matched_ids:
            tid2 = find_match(t1, s2)
            # add new pair if successful
            if tid2 is not None:
                track_id_pairs.append([int(tid1), int(tid2)])
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

def check_itoms(timestamp, under_test, neighbor, predecessor_last):
    # indices of relevant fields in the track
    x, y = header.index('x'), header.index('y')
    vx, vy = header.index('v_x'), header.index('v_y')
    t = header.index('time')
    # fill itoms as available
    itoms = {'t': timestamp, 'x': under_test[x], 'y': under_test[y]}
    if neighbor is not None:
        itoms.update({
            'x_nbr': neighbor[x],
            'y_nbr': neighbor[y],
        })
    if predecessor_last is not None:
        itoms.update({
            't': under_test[t],
            't_old': predecessor_last[t],
            'x_old': predecessor_last[x],
            'y_old': predecessor_last[y],
            'vx_old': predecessor_last[vx],
            'vy_old': predecessor_last[vy],
            'vx_old': predecessor_last[vx],
            'vy_old': predecessor_last[vy],
        })
    status_x = x_monitor.monitor(itoms)
    status_y = y_monitor.monitor(itoms)
    status = {itom: max(status_x[itom], status_y[itom]) for itom in itoms}
    return status

# assume track ids are unique throughout the run (ids are not re-used when out
# of range)
track_id_pairs_spre = []  # pairs sensor to monitor <--> predecessor
track_id_pairs_ssuc = []  # pairs sensor to monitor <--> successor

def check(t, sensors, sensors_last):
    """Check itoms in sensor-under-test's domain."""
    if sensors is None:
        return None
    # default
    status = None
    # make the monitoring concrete here
    try:
        spre_last = sensors_last[args.sensor-1]
        spre = sensors[args.sensor-1]  # all contained in spre_last, only used to update pairs
        stest = sensors[args.sensor]
        ssuc = sensors[args.sensor+1]
    except Exception as e:
        # if we don't have data from neighboring sensors, abort
        print("no data from neighboring sensors at time {}".format(t))
        return
    # associate tracks from one sensor to the other
    global track_id_pairs_spre
    global track_id_pairs_ssuc
    track_id_pairs_spre = update_id_pairs(stest, spre, track_id_pairs_spre)
    track_id_pairs_ssuc = update_id_pairs(stest, ssuc, track_id_pairs_ssuc)
    track_pairs_spreold = pair(stest, spre_last, track_id_pairs_spre)
    #track_pairs_spre = pair(stest, spre, track_id_pairs_spre)
    track_pairs_ssuc = pair(stest, ssuc, track_id_pairs_ssuc)
    pairs_logger.log(time=float(t), sensors=[args.sensor, args.sensor-1],
                     pairs=track_id_pairs_spre)
    pairs_logger.log(time=float(t), sensors=[args.sensor, args.sensor+1],
                     pairs=track_id_pairs_ssuc)
    # check sensor against the neighbors
    if not track_pairs_spreold and not track_pairs_ssuc:
        print("no track pairs")
        return
    # TODO: sum up status
    for track_under_test, track_neighbor in track_pairs_ssuc:
        status = check_itoms(t, track_under_test, track_neighbor, None)
    # for track_under_test, track_neighbor in track_pairs_6:
    #     status = check_itoms(track_under_test, track_neighbor)
    for track_under_test, track_old in track_pairs_spreold:
        status = check_itoms(t, track_under_test, None, track_old)


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
        # check the itoms gathered during the last period
        check(t, sensors, sensors_last)
        # reset
        t = row['time']
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
