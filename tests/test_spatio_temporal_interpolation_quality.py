from interpolation.analysis import Analysis
from interpolation.iohelper import Reader
import interpolation.utils as utils
import interpolation.qualityassessment as qa


reader = Reader('input/wetter_nov.csv')
analysis = Analysis(60, 10)
reader(2, 3, 4, 13, 1, analysis)

time_handler = utils.TimeHandler(reader.times)
points4d = time_handler.raise_to_fourth_dimension(reader.points, 1)

random_samples, last_sample = utils.divide_in_random(10, points=points4d, timestamps=reader.times, values=reader.values,
                                                     point_dimension=4)
# access_quality_of_spatial_interpolation(grouped_samples, one_sample, function='rbf', function_type='linear',
# number_of_neighbors=6, power=2, write=False, r2formula='keller'):
qa.access_quality_of_interpolation(random_samples, last_sample, function='idw', write=True)
# grids = analysis.generate_time_series_grids(reader.times)

qa.access_quality_of_interpolation(random_samples, last_sample, write=True)
