from interpolation.qualityassessment import access_quality_of_spatial_interpolation
from interpolation.iohelper import Reader, Writer
from interpolation.analysis import Analysis
from interpolation.utils import divide_in_random

print('Start')
reader = Reader('input/wetter.csv')
analysis = Analysis(None, 4)
points, values, times = reader(2, 3, 4, 13, 1, analysis)
grouped_samples, one_sample = divide_in_random(10, points, values, times)

description = []
stats_mae = []
stats_mse = []
stats_rmse = []
stats_mare = []
stats_r2 = []

function_type = ['thin_plate', 'cubic', 'linear', 'inverse', 'quintic', 'multiquadric', 'gaussian']
neighbors = [2, 4, 6, 8, 10, 20, 25]
powers = [1, 2, 3]

for j in range(len(neighbors)):
    for k in range(len(powers)):
        mae, mse, rmse, mare, r2 = \
            access_quality_of_spatial_interpolation(grouped_samples=grouped_samples,
                                                    one_sample=one_sample,
                                                    function='idw',
                                                    number_of_neighbors=neighbors[j],
                                                    power=powers[k], r2formula='keller')
        print('idw [neighbors: ' + str(neighbors[j]) + ', power: ' + str(powers[k]) + '] in process')
        description.append('idw [neighbors: ' + str(neighbors[j]) + ', power: ' + str(powers[k]) + ']')
        stats_mae.append(mae)
        stats_mse.append(mse)
        stats_rmse.append(rmse)
        stats_mare.append(mare)
        stats_r2.append(r2)
        print('Done')

for m in range(len(function_type)):
    mae, mse, rmse, mare, r2 = \
        access_quality_of_spatial_interpolation(grouped_samples=grouped_samples,
                                                one_sample=one_sample,
                                                function='rbf', function_type=function_type[m], r2formula='keller')
    print('rbf ' + function_type[m] + ' in process')
    description.append('rbf ' + function_type[m])
    stats_mae.append(mae)
    stats_mse.append(mse)
    stats_rmse.append(rmse)
    stats_mare.append(mare)
    stats_r2.append(r2)
    print('Done')

writer = Writer('output/quality_comparison_keller_idwPowerChange')
writer.write_quality_comparison(description, stats_mae, stats_mse, stats_rmse, stats_mare, stats_r2)
print('All done')



