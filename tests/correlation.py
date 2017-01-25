import plotly
import plotly.graph_objs as go
import numpy
from interpolation.csvconverter import CsvConverter

plotter = CsvConverter('input/wetter.csv')
plotter(1, 2, 3, 4, 13, 15, 14)

measurements = go.Scatter(
    x=plotter.times,
    y=plotter.alt_values,
    mode='markers',
    marker=dict(
        size=8,
        color=numpy.asarray(plotter.press_values),
        colorscale='Portland',
        opacity=0.8,
        showscale=True
    )
)

layout = dict(
        xaxis=dict(title='Time'),
        yaxis=dict(title='Altitude')
            )

plotly.offline.plot({"data": [measurements], "layout": layout})

