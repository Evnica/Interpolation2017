from scipy.interpolate import Rbf

from interpolation.interpolator import InverseDistanceWeighting
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
import time
import plotly
import plotly.graph_objs as go
import numpy


start = time.time()
print('Start ' + str(start))
helper = Reader('input/wetter_nov1.csv')
analysis = Analysis(None, 20)
points, temps, times = helper(2, 3, 4, 14, 1, analysis)
grid = analysis.generate_grid()
current = numpy.asarray(points)
values = numpy.asarray(temps)
look_for = numpy.asarray(grid)
#tree = InverseDistanceWeighting(current, values, 10)
#interpolated = tree(25, 3, look_for)

lat_values = [point[0] for point in points]
lon_values = [point[1] for point in points]
alt_values = [point[2] for point in points]

target_lat_values = [point[0] for point in look_for]
target_lon_values = [point[1] for point in look_for]
target_alt_values = [point[2] for point in look_for]

#analysis.function = 'linear'

rbf = Rbf(lat_values, lon_values, alt_values, values, function=analysis.function)
interpolated = rbf(target_lat_values, target_lon_values, target_alt_values)

for i in range(len(interpolated)):
    if interpolated[i] > analysis.input_max:
        interpolated[i] = analysis.input_max
    elif interpolated[i] < analysis.input_min:
        interpolated[i] = analysis.input_min

measurements3d = go.Scatter3d(
    x=target_lon_values,
    y=target_lat_values,
    z=target_alt_values,
    mode='markers',
    marker=dict(
        size=10,
        color=numpy.asarray(interpolated),
        colorscale='Portland',  # 'pairs' | 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' | 'Jet' | 'RdBu'
                           # | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
        cmin=analysis.input_min,
        cmax=analysis.input_max,
        opacity=0.8,
        showscale=True
    )
)

layout = go.Layout(
    scene=dict(
        xaxis=dict(title='Longitude', autorange='reversed'),
        yaxis=dict(title='Latitude'),
        zaxis=dict(title='Altitude'), ), margin=dict(r=0, b=0, l=0, t=0)
    )

plotly.offline.plot({"data": [measurements3d], "layout": layout})

print('Finished in ' + str(time.time() - start) + ' sec')
