import numpy
import time
from interpolation.analysis import Analysis
from interpolation.iohelper import Reader, Writer
from interpolation.interpolator import InverseDistanceWeighting
import interpolation.utils as utils


reader = Reader('input/wetter_nov.csv')
analysis = Analysis(None, 4)
reader(2, 3, 4, 13, 0, analysis)

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
writer = Writer('output/idw_temp_systime.json')
#writer.write_time_series_grids_to_json(analysis=analysis, grids=grids, grid_values=grid_values)
writer.write_spatial_grid_to_json(analysis=analysis, grid=grid, values=values)

reader2 = Reader('input/wetter_nov.csv')
analysis = Analysis(50000, 5)  # time step: every 30 minutes
reader2(2, 3, 4, 13, 0, analysis)
time_handler = utils.TimeHandler(reader2.system_times)
points4d = time_handler.raise_to_fourth_dimension(reader2.points, 1)
grids = analysis.generate_time_series_grids(reader2.system_times)
print(len(grids))
current = numpy.asarray(points4d)
values = numpy.asarray(reader2.values)
tree = InverseDistanceWeighting(current, values, 10)

grid_values = []
for i in range(len(grids)):
    look_for = numpy.asarray(grids[i])
    grid_values.append(tree(6, 2, look_for))

writer = Writer('output/spatio_temporal_idw_systime.json')
writer.write_time_series_grids_to_json(analysis=analysis, grids=grids, grid_values=grid_values)
print(time.time() - start)