import interpolation.qualityassessment as qa
import numpy
from interpolation.iohelper import Reader
from interpolation.iohelper import Writer
from interpolation.analysis import Analysis
from interpolation.utils import divide_in_random
from interpolation.interpolator import InverseDistanceWeighting


analysis = Analysis(None, 10)
reader = Reader('input/wetter.csv')
# (lat_index, lon_index, alt_index, value_index, time_index, analysis)
points, values, times = reader(2, 3, 4, 13, 1, analysis)
grouped_samples, one_sample = divide_in_random(10, points, values, times)

known_locations = []
known_values = []
known_times = []
query_locations = []
control_values = []
mae = []
mse = []
rmse = []
mare = []
r2 = []
num_of_known = []
num_of_query = []

for i in range(len(grouped_samples)):  # for each of the 9 samples
    for j in range(len(grouped_samples[i])):  # for each entry in the sample
        known_locations.append(grouped_samples[i][j][0])  # append point to known locations
        known_values.append(grouped_samples[i][j][1])  # append value to known values
        known_times.append(grouped_samples[i][j][2])
for i in range(0, len(one_sample)):
    query_locations.append(one_sample[i][0])
    control_values.append(one_sample[i][1])

idw = InverseDistanceWeighting(numpy.asarray(known_locations), numpy.asarray(known_values), 10)
# nearest_neighbors, epsilon, power, unknown_locations, weights
interpolated = idw(6, 0.0001, 2, numpy.asarray(query_locations), None)

print('Current iteration: 1')
num_of_known.append(len(known_locations))
num_of_query.append(len(query_locations))
print('Number of known locations: ' + str(num_of_known[0]))
print('Number of query locations: ' + str(num_of_query[0]))

print('MAE')
mae.append(qa.mean_absolute_error(interpolated, control_values))
print(mae[0])
print('MSE')
mse.append(qa.mean_squared_error(interpolated, control_values))
print(mse[0])
print('RMSE')
rmse.append(qa.root_mean_square_error(interpolated, control_values))
print(rmse[0])
print('MARE')
mare.append(qa.mean_absolute_relative_error(interpolated, control_values))
print(mare[0])
print('R^2')
r2.append(qa.r2_calc(interpolated, control_values))
print(r2[0])

for i in range(0, len(grouped_samples)):
    #  empty all the temporary storage variables
    known_locations = []
    known_values = []
    query_locations = []
    control_values = []
    for j in range(0, len(grouped_samples[i])):
        #  copy current sample to the query locations / control values
        query_locations.append(grouped_samples[i][j][0])
        control_values.append(grouped_samples[i][j][1])
    #  copy all the samples after this sample to known locations / known values
    for k in range(i+1, len(grouped_samples)):
        for j in range(0, len(grouped_samples[k])):
            known_locations.append(grouped_samples[k][j][0])
            known_values.append(grouped_samples[k][j][1])
    # if current sample is not the first one, copy all the samples before this sample to known locations / known values
    if i > 0:
        for l in range(0, i):
            for j in range(0, len(grouped_samples[l])):
                known_locations.append(grouped_samples[l][j][0])
                known_values.append(grouped_samples[l][j][1])
    # copy the separate sample to known locations / values
    for m in range(0, len(one_sample)):
        known_locations.append(one_sample[m][0])
        known_values.append(one_sample[m][1])
    # perform statistical analysis, save values to arrays
    print('Current iteration: ' + str(i+2))
    num_of_known.append(len(known_locations))
    num_of_query.append(len(query_locations))
    print('Number of known locations: ' + str(num_of_known[i+1]))
    print('Number of query locations: ' + str(num_of_query[i+1]))
    idw = InverseDistanceWeighting(numpy.asarray(known_locations), numpy.asarray(known_values), 10)
    interpolated = idw(6, 0.0001, 2, numpy.asarray(query_locations), None)
    print('MAE')
    mae.append(qa.mean_absolute_error(interpolated, control_values))
    print(mae[i+1])
    print('MSE')
    mse.append(qa.mean_squared_error(interpolated, control_values))
    print(mse[i+1])
    print('RMSE')
    rmse.append(qa.root_mean_square_error(interpolated, control_values))
    print(rmse[i+1])
    print('MARE')
    mare.append(qa.mean_absolute_relative_error(interpolated, control_values))
    print(mare[i+1])
    print('R^2')
    r2.append(qa.r2_calc(interpolated, control_values))
    print(r2[i+1])

print('Results:')
print('MAE ' + str(sum(mae)/len(mae)))
print('MSE ' + str(sum(mse)/len(mse)))
print('RMSE ' + str(sum(rmse)/len(rmse)))
print('MARE ' + str(sum(mare)/len(mare)))
print('R^2 ' + str(sum(r2)/len(r2)))

stat_writer = Writer('output/spatial_idw_quality_assessment')
# write_quality_test_to_csv(mae, mse, rmse, mare, r2, num_of_known, num_of_query):
stat_writer.write_quality_test_to_csv(mae, mse, rmse, mare, r2, num_of_known, num_of_query)
print("Done")
