from interpolation.interpolator import InverseDistanceWeighting
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
import time
import plotly
import plotly.graph_objs as go
import numpy


start = time.time()
print('Start ' + str(start))
helper = Reader('input/wetter.csv')
analysis = Analysis(None, 25)
points, temps, times = helper(2, 3, 4, 13, 1, analysis)
grid = analysis.generate_grid()
current = numpy.asarray(points)
values = numpy.asarray(temps)
look_for = numpy.asarray(grid)
tree = InverseDistanceWeighting(current, values, 10)
interpol = tree(6, 0.01, 3, look_for, None)

lat_values = [point[0] for point in look_for]
lon_values = [point[1] for point in look_for]
alt_values = [point[2] for point in look_for]

measurements3d = go.Scatter3d(
    x=lon_values,
    y=lat_values,
    z=alt_values,
    mode='markers',
    marker=dict(
        size=8,
        color=numpy.asarray(interpol),
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
