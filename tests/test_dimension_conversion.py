from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
import interpolation.utils as utils


reader = Reader('input/wetter.csv')
analysis = Analysis(None, 2)
reader(2, 3, 4, 13, 1, analysis)
th = utils.TimeHandler(reader.times)

print(reader.times[100])

mics = [th.get_unix_time_in_millis(dt) for dt in reader.times]
print(mics[100])
print(th.times_normalized[100])
poi = th.raise_to_fourth_dimension(reader.points, th.times_normalized, 1)
print(poi[100])
ttsm = th.get_timestamp_from_scaled(poi[100][3], 1)
print(ttsm)
print(utils.datetime_from_unix_millis(ttsm))
