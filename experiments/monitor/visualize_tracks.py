#!/usr/bin/python3
"""Visualization of the monitor data.

Visualize:
* Tracks, output of the sensor KF, measurements, detected vehicles - dots
  with covariance (a color per sensor).
* Track pairs, related measurements of two different sensors - line between
  track dots.
* Prediction of tracks - light dots with covariance.

"""

import numpy as np
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons


# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('sensors', type=str,
                    help="CSV file of sensor locations.")
parser.add_argument('tracks', type=str,
                    help="CSV file of tracks.")
parser.add_argument('-p', '--pairs', type=str,
                    help="""Draw a line between paired tracks given the output
                    (CSV of pairs) of the monitor.""")
args = parser.parse_args()


#
# Load data
#

print("\nSensors")
print("-------")
sensors = np.genfromtxt(args.sensors, delimiter=',', comments='#', names=True)
print("{} columns with names {}".format(len(sensors[0]), sensors.dtype.names))
print("first row: {}".format(sensors[0]))

def collect_track_timeline(data):
    """Collect tracks per time step.

    Assumption: Tracks are listed in ascending time.
    """
    time = []  # timeline (seconds)
    tracks = []  # timeline of measured tracks per sensor
    t = data[0]['time']  # first timestamp
    sensors = {}
    for row in data:
        # gather itoms as long as its the same timestamp
        if row['time'] != t:
            # save data to time step
            time.append(round(t,1))
            tracks.append(sensors)
            # reset for new timestamp
            t = row['time']
            sensors = {}
        # create a list of tracks for each sensor
        sid = int(row['sensor'])
        if sid not in sensors.keys():
            sensors[sid] = {}  # key: sensor ID
        # save track observation (key = track ID)
        tid = int(row['track'])
        sensors[sid][tid] = row
    return time, tracks

print("\nTracks")
print("------")
data = np.genfromtxt(args.tracks, delimiter=',', comments='#', names=True)
print("{} columns with names {}".format(len(data[0]), data.dtype.names))
print("first row: {}".format(data[0]))
time, tracks = collect_track_timeline(data)
s0 = list(tracks[0].keys())[0]
t0 = list(tracks[0][s0].keys())[0]
print("first time step:")
print("  sensors: {}".format(tracks[0].keys()))
print("  tracks IDs of sensor {}: {}".format(s0, tracks[0][s0].keys()))
print("  first track: {}".format(tracks[0][s0][t0]))

def collect_pairs(time, data):
    """Collect pairs per track time step.

    Assumption: Pairs are listed in ascending time.
    """
    # default: no pairs per time step
    pairs_timeline = []  # timeline of pairs
    t = data[0]['time']  # first timestamp
    ti_last = 0  # last timestamp index processed
    tstep = time[1] - time[0]
    pairs = []
    for row in data:
        ti = int(round((row['time'] - time[0]) / tstep, 0))
        # gather pairs as long as its the same timestamp
        if ti != ti_last:
            # fill intermediate time steps that are not in the csv
            for i in range(ti_last, ti-1):
                pairs_timeline.append([])
            # set pairs of current time step
            pairs_timeline.append(pairs)
            # reset for new timestamp
            ti_last = ti
            pairs = []
        # save pair
        pair = {'from_sensor': int(row['from_sensor']),
                'from_track': int(row['from_track']),
                'to_sensor': int(row['to_sensor']),
                'to_track': int(row['to_track'])}
        pairs.append(pair)
    for i in range(ti_last, len(time)):
        pairs_timeline.append([])
    return pairs_timeline

if args.pairs:
    print("\nPairs")
    print("------")
    data = np.genfromtxt(args.pairs, delimiter=',', comments='#', names=True)
    print("{} columns with names {}".format(len(data[0]), data.dtype.names))
    print("first row: {}".format(data[0]))
    pairs = collect_pairs(time, data)
    print("pairs for first timestamp: {}".format(pairs[0]))


#
# Plot
#
# https://matplotlib.org/gallery/widgets/slider_demo.html
# https://github.com/joferkington/oost_paper_code/blob/master/error_ellipse.py
# Instead of ellipses we draw circles for simplicity (available a parameter in
# the scatter plot):
# https://matplotlib.org/gallery/shapes_and_collections/scatter.html

print("\nPlot")
print("====")
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
plt.axis([200, 370, -220, -100])

ti = 0
tstep = time[1] - time[0]  # assume equidistant time steps!

def time_to_index(t):
    t = round(t, 1)
    ti = int(round((t - time[0]) / tstep, 0))
    return ti

# sensors
color = {6: 'seagreen', 7: 'lime', 8: 'darkolivegreen'}
print("Print tracks of sensors: {}".format(color.keys()))

# plot position of each sensor
x = [row['x'] for row in sensors]
y = [row['y'] for row in sensors]
plt.scatter(x, y, c='grey')

# plot scatter of each sensor's tracks

def get_data_for_time(t, sensor):
    x, y, sigma = None, None, None
    try:
        ti = time_to_index(t)
        x = [track['x'] for track in tracks[ti][sensor].values()]
        y = [track['y'] for track in tracks[ti][sensor].values()]
        sigma = [track['sigma_x']**2  # size of the marker
                 for track in tracks[ti][sensor].values()]
    except Exception as e:
        print("Warning: nothing will be printed for time {}, sensor {}".format(t, sensor))
        x, y, sigma = [], [], []
    return x, y, sigma

# scatter data of each sensor
pathcol = {}
for sensor in color.keys():
    x, y, sigma = get_data_for_time(time[0], sensor)
    pathcol[sensor] = plt.scatter(x, y, s=sigma, c=color[sensor])

# plot track pairs
def get_track_location(t, sensor, track):
    ti = time_to_index(t)
    sensor = int(sensor)
    track = int(track)
    return tracks[ti][sensor][track]['x'], tracks[ti][sensor][track]['y']

# draw track pairs by lines
# restrict the number or lines that are visible
lines = []
for p in range(50):
    line, = plt.plot([0, 0], [0, 0], 'k-', color='black', lw=1)
    lines.append(line)

# the time can be advanced with a slider
axtime = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightblue')
slider_time = Slider(axtime, 'Time', time[0], time[-1], valinit=time[0],
                     valstep=tstep)

def update(val):
    time = slider_time.val
    # update scatter plot
    for sensor in color.keys():
        x, y, sigma = get_data_for_time(time, sensor)
        a = np.array([x, y])
        pathcol[sensor].set_offsets(a.transpose())
    # update pair lines
    l = 0
    for pair in pairs[time_to_index(time)]:
        try:
            x1, y1 = get_track_location(time, pair['from_sensor'], pair['from_track'])
            x2, y2 = get_track_location(time, pair['to_sensor'], pair['to_track'])
            lines[l].set_xdata([x1, x2])
            lines[l].set_ydata([y1, y2])
            l = l + 1
        except KeyError:
            # pair is not in view
            pass
    for i in range(l, len(lines)):
        # reset unused pairs to (0, 0)
        lines[i].set_xdata([0, 0])
        lines[i].set_ydata([0, 0])
    # redraw
    fig.canvas.draw_idle()

slider_time.on_changed(update)

plt.show()
