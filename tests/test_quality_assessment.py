from interpolation.qualityassessment import access_quality_of_interpolation
from interpolation.iohelper import Reader, Writer
from interpolation.analysis import Analysis
from interpolation.utils import divide_in_random, TimeHandler

print('Start')
reader = Reader('input/wetter.csv')
analysis = Analysis(None, 4)
points3d, values, times = reader(2, 3, 4, 13, 1, analysis)
# num_of_random_samples, points, values, timestamps, point_dimension=3
time_handler = TimeHandler(times)
points4d = time_handler.raise_to_fourth_dimension(points3d=points3d, time_scale=1)
grouped_samples, one_sample = divide_in_random(num_of_random_samples=10, points=points4d, values=values,
                                               timestamps=times, point_dimension=4)

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
        print('idw [neighbors: ' + str(neighbors[j]) + ', power: ' + str(powers[k]) + '] in process')
        mae, mse, rmse, mare, r2 = \
            access_quality_of_interpolation(grouped_samples=grouped_samples,
                                            one_sample=one_sample,
                                            function='idw',
                                            number_of_neighbors=neighbors[j],
                                            power=powers[k], r2formula='keller')
        description.append('idw [neighbors: ' + str(neighbors[j]) + ', power: ' + str(powers[k]) + ']')
        stats_mae.append(mae)
        stats_mse.append(mse)
        stats_rmse.append(rmse)
        stats_mare.append(mare)
        stats_r2.append(r2)
        print('Done')

for m in range(len(function_type)):
    print('rbf ' + function_type[m] + ' in process')
    mae, mse, rmse, mare, r2 = \
        access_quality_of_interpolation(grouped_samples=grouped_samples,
                                        one_sample=one_sample,
                                        function='rbf', function_type=function_type[m], r2formula='keller')
    description.append('rbf ' + function_type[m])
    stats_mae.append(mae)
    stats_mse.append(mse)
    stats_rmse.append(rmse)
    stats_mare.append(mare)
    stats_r2.append(r2)
    print('Done')

writer = Writer('output/quality_comparison_4d-2')
writer.write_quality_comparison(description, stats_mae, stats_mse, stats_rmse, stats_mare, stats_r2)
print('All done')



