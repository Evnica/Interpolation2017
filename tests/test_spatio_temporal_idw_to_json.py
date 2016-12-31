import numpy
import time
from interpolation.analysis import Analysis
from interpolation.iohelper import Reader, Writer
from interpolation.interpolator import InverseDistanceWeighting
import interpolation.utils as utils


reader = Reader('input/wetter_nov.csv')
analysis = Analysis(None, 4)
reader(2, 3, 4, 13, 1, analysis)

grid = analysis.generate_grid()
current = numpy.asarray(reader.points)
values = numpy.asarray(reader.values)
look_for = numpy.asarray(grid)

grids = [grid]
grid_values = [values]

start = time.time()
print('Start ' + str(start))
tree = InverseDistanceWeighting(current, values, 10)
interpol = tree(6, 2, look_for)
writer = Writer('output/idw_temp_nov.json')
writer.write_time_series_grids_to_json(analysis=analysis, grids=grids, grid_values=grid_values)

analysis = Analysis(30*60, 5)  # time step: every 30 minutes
reader(2, 3, 4, 13, 1, analysis)
time_handler = utils.TimeHandler(reader.times)
points4d = time_handler.raise_to_fourth_dimension(reader.points, 1)
grids = analysis.generate_time_series_grids(reader.times)
print(len(grids))
current = numpy.asarray(points4d)
values = numpy.asarray(reader.values)
tree = InverseDistanceWeighting(current, values, 10)

grid_values = []
for i in range(len(grids)):
    look_for = numpy.asarray(grids[i])
    grid_values.append(tree(6, 2, look_for))

writer = Writer('output/spatio_temporal_idw_temp_nov.json')
writer.write_time_series_grids_to_json(analysis=analysis, grids=grids, grid_values=grid_values)
print(time.time() - start)