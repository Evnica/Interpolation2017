from scipy.interpolate import Rbf
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
import time
import plotly
import plotly.graph_objs as go
import numpy

start = time.time()
print('Start ' + str(start))
reader = Reader('input/wetter.csv')
analysis = Analysis(None, 25)
reader(2, 3, 4, 13, 1, analysis)  # temperature
print(len(reader.points))
grid = analysis.generate_grid()

current = numpy.asarray(reader.points)
values = numpy.asarray(reader.values)
print(values)
target_grid = numpy.asarray(grid)

lat_values = [point[0] for point in reader.points]
lon_values = [point[1] for point in reader.points]
alt_values = [point[2] for point in reader.points]

target_lat_values = [point[0] for point in target_grid]
target_lon_values = [point[1] for point in target_grid]
target_alt_values = [point[2] for point in target_grid]

rbf = Rbf(lat_values, lon_values, alt_values, values, function='cubic')
interpolated_values = rbf(target_lat_values, target_lon_values, target_alt_values)

print(interpolated_values)

measurements3d = go.Scatter3d(
    x=target_lon_values,
    y=target_lat_values,
    z=target_alt_values,
    mode='markers',
    marker=dict(
        size=8,
        color=numpy.asarray(interpolated_values),
        colorscale='Jet',  # 'pairs' | 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' | 'Jet' | 'RdBu'
                           # | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
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
