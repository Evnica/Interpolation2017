from interpolation.interpolator import InverseDistanceWeighting
from interpolation.iohelper import Reader
from interpolation.iohelper import Writer
from interpolation.analysis import Analysis
import numpy
import time

reader = Reader('input/wetter.csv')
analysis = Analysis(None, 10)
# (lat_index, lon_index, alt_index, value_index, time_index, analysis)
reader(2, 3, 4, 13, 1, analysis)  # 13 = temperature
grid = analysis.generate_grid()
current = numpy.asarray(reader.points)
values = numpy.asarray(reader.values)
look_for = numpy.asarray(grid)

start = time.time()
print('Start ' + str(start))
tree = InverseDistanceWeighting(current, values, 10)
# 6 neighbors, epsilon = 0.01, power = 2, no weights
interpol = tree(6, 2, look_for)
writer = Writer('output/idw_temp_with_duplicates.json')
writer.write_spatial_grid_to_json(grid, interpol, analysis, reader.times)
print(time.time() - start)
