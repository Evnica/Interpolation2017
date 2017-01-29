import plotly
import plotly.graph_objs as go
import numpy
from interpolation.csvconverter import CsvConverter

plotter = CsvConverter('input/wetter_nov1.csv')
plotter(1, 2, 3, 4, 13, 15, 14)

measurements3d = go.Scatter3d(
    x=plotter.lon_values,
    y=plotter.lat_values,
    z=plotter.alt_values,
    mode='lines+markers',
    marker=dict(
        size=3,
        color=numpy.asarray(plotter.press_values),
        colorscale='Portland',
        opacity=0.8,
        showscale=True
    ),
    line=dict(color=numpy.asarray(plotter.press_values), colorscale='Portland', width=1)
)

layout = go.Layout(
    scene=dict(
        xaxis=dict(title='Longitude'),
        yaxis=dict(title='Latitude'),
        zaxis=dict(title='Altitude'), ), margin=dict(r=0, b=0, l=0, t=0)
    )

plotly.offline.plot({"data": [measurements3d], "layout": layout})

