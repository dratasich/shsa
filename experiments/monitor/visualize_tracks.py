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
args = parser.parse_args()


#
# Load data
#

print("Sensors")
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
            time.append(t)
            tracks.append(sensors)
            # reset for new timestamp
            t = row['time']
            sensors = {}
        # create a list of tracks for each sensor
        sid = row['sensor']
        if sid not in sensors.keys():
            sensors[sid] = {}  # key: sensor ID
        # save track observation (key = track ID)
        tid = row['track']
        sensors[sid][tid] = row
    return time, tracks

print("Tracks")
print("------")
data = np.genfromtxt(args.tracks, delimiter=',', comments='#', names=True)
print("{} columns with names {}".format(len(data[0]), data.dtype.names))
print("first row: {}".format(data[0]))
time, tracks = collect_track_timeline(data)


#
# Plot
#
# https://matplotlib.org/gallery/widgets/slider_demo.html
# https://github.com/joferkington/oost_paper_code/blob/master/error_ellipse.py
# Instead of ellipses we draw circles for simplicity (available a parameter in
# the scatter plot):
# https://matplotlib.org/gallery/shapes_and_collections/scatter.html

print("Plot")
print("====")
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)

ti = 0
t = time[ti]
tstep = time[1] - time[0]  # assume equidistant time steps!

# sensors
color = {6: 'seagreen', 7: 'lime', 8: 'darkolivegreen'}
print("Print tracks of sensors: {}".format(color.keys()))

# plot position of each sensor
x = [row['x'] for row in sensors]
y = [row['y'] for row in sensors]
plt.scatter(x, y, c='grey')

# scatter data of each sensor
pathcol = {}

def get_data_for_time(t, sensor):
    x, y, sigma = None, None, None
    try:
        t = round(t, 1)
        ti = int(round((t - time[0]) / tstep, 0))
        x = [track['x'] for track in tracks[ti][sensor].values()]
        y = [track['y'] for track in tracks[ti][sensor].values()]
        sigma = [track['sigma_x']**2  # size of the marker
                 for track in tracks[ti][sensor].values()]
    except Exception as e:
        print("Warning: nothing will be printed for time {}, sensor {}".format(t, sensor))
        x, y, sigma = [], [], []
    return x, y, sigma

# print scatter of each sensor separately
for sensor in color.keys():
    x, y, sigma = get_data_for_time(time[0], sensor)
    pathcol[sensor] = plt.scatter(x, y, s=sigma, c=color[sensor])

plt.axis([200, 370, -220, -100])

# The time can be advanced with a slider
axtime = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightblue')
slider_time = Slider(axtime, 'Time', time[0], time[-1], valinit=time[0],
                     valstep=tstep)

def update(val):
    time = slider_time.val
    for sensor in color.keys():
        x, y, sigma = get_data_for_time(time, sensor)
        a = np.array([x, y])
        pathcol[sensor].set_offsets(a.transpose())
    fig.canvas.draw_idle()

slider_time.on_changed(update)

plt.show()
