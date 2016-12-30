from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
import interpolation.utils as utils


reader = Reader('input/wetter.csv')
analysis = Analysis(None, 2)
reader(2, 3, 4, 13, 1, analysis)
th = utils.TimeHandler(reader.times)

print(reader.times[100])

mics = [th.get_unix_time_in_seconds(dt) for dt in reader.times]
print(mics[100])
print(th.times_normalized[100])
poi = th.raise_to_fourth_dimension(reader.points, 1)
print(poi[100])
tt_sm = th.get_timestamp_from_scaled(poi[100][3], 1)
print(tt_sm)
print(utils.datetime_from_unix_seconds(tt_sm))

all_right = True
for i in range(len(poi)):
    tt_sm = th.get_timestamp_from_scaled(poi[i][3], 1)
    if tt_sm != mics[i]:
        print(str(i) + ' ' + str(tt_sm) + ' != ' + str(mics[i]))
        all_right = False

if all_right:
    print('Everything is fine. Done.')
else:
    print('Done, but with errors')
