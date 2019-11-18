#!/usr/bin/python3
"""Visualization of the monitor data.

Visualize:
* Tracks, output of the sensor KF, measurements, detected vehicles - dots
  with covariance (a color per sensor).
* Track pairs, related measurements of two different sensors - line between
  track dots.
* Monitor logs (compared itoms in the common domain).

Move timeline with arrow keys. Quit with 'q'.

"""

import numpy as np
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.colors as colors
import yaml
import math
from collections import OrderedDict

from utils.logger import Logger


# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('sensors', type=str,
                    help="CSV file of sensor locations.")
parser.add_argument('tracks', type=str,
                    help="CSV file of tracks.")
parser.add_argument('-l', '--monitor-logs', type=str, nargs=2, metavar=("X",
                    "Y"), help="Logfiles (yaml) of monitors.")
parser.add_argument('-p', '--pairs', type=str,
                    help="""Draw a line between paired tracks given the output
                    (YAML of pairs) of the monitor.""")
parser.add_argument('-s', '--sensor', type=int, default=7,
                    help="Sensor ID under test.")
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

pairs_logger = None
if args.pairs:
    print("\nPairs")
    print("------")
    print("Load ...")
    pairs_logger = Logger(args.pairs, 'r')
    print("Pairs at timestamp 0.4: " + str(pairs_logger.get(time=0.4,
                                                            tolerance=0.1)))

# Note that a monitor log may not include all timestamps!
monitor_x = None
monitor_y = None
if args.monitor_logs:
    print("\nMonitor-Log")
    print("-----------")
    print("Load x ...")
    monitor_x = Logger(args.monitor_logs[0], 'r')
    print("Load y ...")
    monitor_y = Logger(args.monitor_logs[1], 'r')
    assert len(monitor_x.documents) == len(monitor_y.documents), "monitor x/y logs mismatch"
    print("rows/timesteps: {}".format(len(monitor_x.documents)))
    print("first row: {}".format(monitor_x.get()))


#
# Helpers
#

def translate(point, translation):
    """Translates a 2D point."""
    px, py = point
    tx, ty = translation
    return [px + tx, py + ty]

def rotate(origin, point, angle):
    """Rotate a 2D point counterclockwise around the given origin.

    origin -- 2D vector, origin of the rotation.
    point -- 2D vector, point to rotate.
    angle -- Angle in radians.

    https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

    """
    import math
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]


ti = 0
tstep = time[1] - time[0]  # assume equidistant time steps!

def time_to_index(t):
    t = round(t, 1)
    ti = int(round((t - time[0]) / tstep, 0))
    return ti


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
fig, (axtracks, axstatus, axtime) = plt.subplots(3, 1, gridspec_kw = {'height_ratios':[10, 10, 1]})
plt.subplots_adjust(top=0.95, bottom=0.05, hspace=0.5)

# --- subplot ---
axtracks.set_xlabel('x')
axtracks.set_ylabel('y')

#
# sensors
#

color = {args.sensor-1: '#555555', args.sensor: '#888888', args.sensor+1: '#aaaaaa'}
print("Print tracks of sensors: {}".format(color.keys()))
# define area around sensor under test
x1 = float("inf"); x2 = float("-inf")
y1 = float("inf"); y2 = float("-inf")
# min and max positions of sensors to plot
for s in sensors:
    if int(s['sensor']) in set(color.keys()):
        x1 = min(x1, s['x'])
        x2 = max(x2, s['x'])
        y1 = min(y1, s['y'])
        y2 = max(y2, s['y'])
# detection range of sensor under test
x2 = max(x2, sensors[args.sensor]['x'] + sensors[args.sensor]['range'])
d = math.sqrt(math.pow(sensors[1]['x']-sensors[0]['x'], 2) +
              math.pow(sensors[1]['y']-sensors[0]['y'], 2))
print("Pylon distance: {}".format(d))
axtracks.set_xlim(x1-d/2, x2+d/2)
axtracks.set_ylim(y1-d/2, y2+d/2)
# set the same scale for x/y
axtracks.set_aspect('equal', adjustable='datalim')
axtracks.set_anchor('C')
print("Plot area around sensor {}: {}".format(args.sensor, [x1-d, x2+d, y1-d, y2+d]))


# plot sensors
def draw_fov(s, color):
    """Draw field of view of a sensor (detection cone)."""
    x1, y1 = s['x'], s['y']  # origin
    radius, heading, angle = s['range'], 0, s['angle']*math.pi/180
    xt, yt = translate([x1, y1], [radius, 0])
    x = [x1]
    y = [y1]
    # add some intermediate points
    for alpha in np.linspace(heading - angle/2, heading + angle/2, 10):
        xr, yr = rotate([x1, y1], [xt, yt], alpha)
        x.append(xr)
        y.append(yr)
    # draw filled polygon
    axtracks.fill(x, y, c=color, zorder=1)

# plot detection cone
for s in sensors:
    # draw cone of sensor under test only
    sid = int(s['sensor'])
    if sid in set(color.keys()):
        draw_fov(s, colors.to_rgba('#aaaaaa', alpha=0.1))

# plot position of each sensor
x = [row['x'] for row in sensors]
y = [row['y'] for row in sensors]
axtracks.scatter(x, y, c='grey', zorder=2)
# plot sensor id
for s in sensors:
    x, y, name = s['x'], s['y'], int(s['sensor'])
    axtracks.annotate(name, (x, y), (x-1, y-3))


#
# tracks
#

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
    pathcol[sensor] = axtracks.scatter(x, y, s=sigma, c=color[sensor], zorder=5)


#
# pairs
#

# plot track pairs
def get_track_location(t, sensor, track):
    ti = time_to_index(t)
    sensor = int(sensor)
    track = int(track)
    return tracks[ti][sensor][track]['x'], tracks[ti][sensor][track]['y']

def draw_pairs(time):
    if args.pairs is None:
        return
    # get all yaml docs with timestamp=time
    docs = pairs_logger.get(time=time, tolerance=0.1)
    # draw
    l = 0
    for doc in docs:
        s_from, s_to = doc['sensors']
        pairs = doc['pairs']
        for pair in pairs:
            tid_from, tid_to = pair
            try:
                x1, y1 = get_track_location(time, s_from, tid_from)
                x2, y2 = get_track_location(time, s_to, tid_to)
                pair_lines[l].set_xdata([x1, x2])
                pair_lines[l].set_ydata([y1, y2])
                l = l + 1
            except KeyError:
                # pair is not in view
                pass
    for i in range(l, len(pair_lines)):
        # reset unused pairs to (0, 0)
        pair_lines[i].set_xdata([0, 0])
        pair_lines[i].set_ydata([0, 0])

# draw (dummy) track pairs by lines
# restrict the number or lines that are visible
pair_lines = []
for p in range(50):
    line, = axtracks.plot([0, 0], [0, 0], 'k-', color='green', lw=1, zorder=4)
    pair_lines.append(line)


#
# monitor
#

# draw monitor data
def get_monitor_data_for_time(t):
    """Returns a list (all monitor calls at the same timestamp) of list of
    (comparable) points."""
    if args.monitor_logs is None:
        return [], [], [], []
    # monitor data at timestamp
    x_calls = monitor_x.get(time=t, tolerance=0.1)
    y_calls = monitor_y.get(time=t, tolerance=0.1)
    # no monitor data for this timestamp
    if len(x_calls) == 0 or len(y_calls) == 0:
        return [], [], [], []
    # x/y output status shall be the same
    x = [v for call in x_calls for v in call['out']]
    y = [v for call in y_calls for v in call['out']]
    status = [v for call in x_calls for v in call['ostatus']]
    lines = [list(zip(x_calls[i]['out'], y_calls[i]['out']))
             for i in range(len(x_calls))]
    return x, y, status, lines

def draw_monitor_data(t):
    if args.monitor_logs is None:
        return
    x, y, status, lines = get_monitor_data_for_time(t)
    # compared positions as dots
    color_map = ['green', 'blue', 'red']  # OK, UNDEFINED, FAULTY
    colors = [color_map[s] for s in status]
    # update path collection of scatter plot
    monitor_pathcol.set_color(colors)
    a = np.array([x, y])
    monitor_pathcol.set_offsets(a.transpose())
    # link compared positions
    if len(lines) > len(monitor_lines):
        raise RuntimeException("""More lines to draw than canvas lines
        available.""")
    for i, line in enumerate(monitor_lines):
        # update lines of plot
        if i < len(lines):
            x1, y1 = lines[i][0]
            x2, y2 = lines[i][1]
            line.set_xdata([x1, x2])
            line.set_ydata([y1, y2])
        else:
            # reset remaining lines
            line.set_xdata([0, 0])
            line.set_ydata([0, 0])

# draw (dummy) scatter
monitor_pathcol = axtracks.scatter([0]*50, [0]*50, s=5, zorder=10)
# draw (dummy) lines for monitor data
# restrict the number or lines that are visible
monitor_lines = []
for p in range(50):
    line, = axtracks.plot([0, 0], [0, 0], '--', color='black', lw=1, zorder=9)
    monitor_lines.append(line)
# draw true data
draw_monitor_data(0)


# --- subplot ---

# monitor status
status = OrderedDict()
status["paired"] = 0.2
status["lost"] = 0.1
status["health score"] = 0.8
axstatus.set_ylim(0, 1)  # all values normalized
axstatus.bar(range(len(status)), list(status.values()), tick_label=list(status.keys()))

def draw_status(t):
    pass

# --- subplot ---

#
# time update, keys
#

# the time can be advanced with a slider
#axtime = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightblue')
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
    draw_pairs(time)
    # update monitor data
    draw_monitor_data(time)
    # update status
    draw_status(time)
    # redraw
    fig.canvas.draw_idle()

slider_time.on_changed(update)


def key_released(event):
    if event.key == 'left' and slider_time.val > slider_time.valmin:
        slider_time.set_val(slider_time.val - 0.1)
        update(slider_time.val)
    if event.key == 'right' and slider_time.val < slider_time.valmax:
        slider_time.set_val(slider_time.val + 0.1)
        update(slider_time.val)
    elif event.key == 'q':
        # close with key 'q' for convenience
        plt.close(event.canvas.figure)

fig.canvas.mpl_connect('key_release_event', key_released)


plt.show()
