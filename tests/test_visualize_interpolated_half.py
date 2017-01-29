from scipy.interpolate import Rbf

from interpolation.interpolator import InverseDistanceWeighting
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
from interpolation.interpolator import TimeHandler
import time
import plotly
import plotly.graph_objs as go
import numpy


start = time.time()
print('Start ' + str(start))
helper = Reader('input/wetter_nov1.csv')
density = 20
step = 1 / density
analysis = Analysis(None, density)
points, temps, times = helper(2, 3, 4, 14, 1, analysis)
input_max = analysis.input_max
input_min = analysis.input_min
time_handler = TimeHandler(times)
points4d = time_handler.raise_to_fourth_dimension(points3d=points, time_scale=4.5)
print(analysis.input_min)
print(analysis.input_max)
grid = analysis.generate_grid()
analysis = Analysis(900, density)
grids = analysis.generate_time_series_grids(times)
current = numpy.asarray(points)
values = numpy.asarray(temps)
look_for = numpy.asarray(grid)
grid_values = []


layout = go.Layout(
    scene=dict(
        xaxis=dict(title='Longitude', autorange='reversed'),
        yaxis=dict(title='Latitude'),
        zaxis=dict(title='Altitude'), ), margin=dict(r=0, b=0, l=0, t=0)
    )

lat_values = [point[0] for point in points4d]
lon_values = [point[1] for point in points4d]
alt_values = [point[2] for point in points4d]
time_values = [point[3] for point in points4d]

target_lat_values = [point[0] for point in look_for]
target_lon_values = [point[1] for point in look_for]
target_alt_values = [point[2] for point in look_for]

indices = []
for i in range(len(grid)):
    # print(grid[i])
    if grid[i][1] < 0.2 or grid[i][1] > 0.8 or grid[i][0] < 0.2 \
            or grid[i][0] > 0.8 or grid[i][2] < 0.2 or grid[i][2] > 0.8:
        # print('deleted ' + str(grid[i]))
        indices.append(i)

print(len(indices))

for i in range(len(grids)):
    look_for = numpy.asarray(grids[i])
    target_lat_values = [point[0] for point in look_for]
    target_lon_values = [point[1] for point in look_for]
    target_alt_values = [point[2] for point in look_for]
    target_time_values = [point[3] for point in look_for]
    rbf = Rbf(lat_values, lon_values, alt_values, time_values, values, function='cubic')
    interpolated = rbf(target_lat_values, target_lon_values, target_alt_values, target_time_values)
    print(interpolated)
    grid_values.append(interpolated)

    interpol_left = []
    locations = []

    # for index in range(len(indices) - 1, -1, -1):
    #    del (grids[i][index])

    for mu in range(len(interpolated)):
        need_to_add = True
        for index in range(len(indices)):
            if mu == indices[index]:
                need_to_add = False
                break
        if need_to_add:
            interpol_left.append(interpolated[mu])
            locations.append(grids[i][mu])

    print(str(len(locations)) + " locations")
    print(str(len(interpol_left)) + " values")
    print(interpol_left)

    look_for2 = numpy.asarray(locations)
    vis_lat = [point[0] for point in look_for2]
    vis_lon = [point[1] for point in look_for2]
    vis_alt = [point[2] for point in look_for2]

    measurements3d = go.Scatter3d(
        x=vis_lon,
        y=vis_lat,
        z=vis_alt,
        mode='markers',
        marker=dict(
            cmin=input_min,
            cmax=input_max,
            size=15,
            color=numpy.asarray(interpol_left),
            colorscale='Portland',
            # 'pairs' | 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' | 'Jet' | 'RdBu'
            # | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
            opacity=0.8,
            showscale=True
        )
    )
    fig = go.Figure(data=[measurements3d])
    plot = plotly.offline.plot(fig, filename=("rbf_cubic_" + str(i) + ".html"))

# plotly.offline.plot({"data": [measurements3d], "layout": layout})

print('Finished ')