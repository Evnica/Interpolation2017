from enum import Enum
from scipy.interpolate import Rbf
from scipy.spatial import KDTree
import numpy
import plotly
import plotly.graph_objs as go
from interpolation.qualityassessment import access_quality_of_interpolation
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
from interpolation.utils import divide_in_random, TimeHandler
from interpolation.interpolator import InverseDistanceWeighting
from plotly.offline.offline import _plot_html


print('Start')
reader = Reader('wetter.csv')
analysis = Analysis(900, 25)
points, values, times = reader(2, 3, 4, 14, 1, analysis)
time_handler = TimeHandler(times)
points4d = time_handler.raise_to_fourth_dimension(points, 1)
grids = analysis.generate_time_series_grids(times)
current = numpy.asarray(points4d)
values = numpy.asarray(values)
tree = InverseDistanceWeighting(current, values, 10)
grid_values = []

lat_values = [point[0] for point in points]
lon_values = [point[1] for point in points]
alt_values = [point[2] for point in points]

layout = go.Layout(
    scene=dict(
        xaxis=dict(title='Longitude', autorange='reversed'),
        yaxis=dict(title='Latitude'),
        zaxis=dict(title='Altitude'), ), margin=dict(r=0, b=0, l=0, t=0)
    )

for i in range(len(grids)):
    look_for = numpy.asarray(grids[i])
    target_lat_values = [point[0] for point in look_for]
    target_lon_values = [point[1] for point in look_for]
    target_alt_values = [point[2] for point in look_for]
    rbf = Rbf(lat_values, lon_values, alt_values, values, function='cubic')
    interpolated = rbf(target_lat_values, target_lon_values, target_alt_values)
    grid_values.append(tree(analysis.nearest_neighbors, analysis.power, look_for))
    measurements3d = go.Scatter3d(
        x=target_lon_values,
        y=target_lat_values,
        z=target_alt_values,
        mode='markers',
        marker=dict(
            size=10,
            color=numpy.asarray(grid_values[i]),
            colorscale='Portland',
            # 'pairs' | 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' | 'Jet' | 'RdBu'
            # | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
            cmin=analysis.input_min,
            cmax=analysis.input_max,
            opacity=0.8,
            showscale=True
        )
    )
    fig = go.Figure(data=[measurements3d])
    plot = plotly.offline.plot(fig, filename=("rbf_cubic_" + str(i) + ".html"))

# plotly.offline.plot({"data": [measurements3d], "layout": layout})

print('Finished ')
