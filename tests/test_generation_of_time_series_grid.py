from interpolation.analysis import Analysis
from interpolation.iohelper import Reader


reader = Reader('input/wetter_sshort.csv')
analysis = Analysis(6, 4)
reader(2, 3, 4, 13, 1, analysis)

grids = analysis.generate_time_series_grids(reader.times)
for i in range(len(grids)):
    print(grids[i])