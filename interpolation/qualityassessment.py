# statistical methods of error analysis meant to assess interpolation quality
import statistics
import numpy
from scipy.interpolate import Rbf
from interpolation.interpolator import InverseDistanceWeighting
from interpolation.iohelper import Writer


def mean_absolute_error(predicted, actual):
    assert len(predicted) == len(actual), \
        "number of predicted values [%d] differs from the number of actual values [%d]" % (len(predicted), len(actual))
    total = 0
    for i in range(len(predicted)):
        total += abs(predicted[i] - actual[i])
    return total / len(predicted)


def mean_squared_error(predicted, actual):
    assert len(predicted) == len(actual), \
        "number of predicted values [%d] differs from the number of actual values [%d]" % (len(predicted), len(actual))
    total = 0
    for i in range(len(predicted)):
        total += (predicted[i] - actual[i]) ** 2
    return total / len(predicted)


def root_mean_square_error(predicted, actual):
    assert len(predicted) == len(actual), \
        "number of predicted values [%d] differs from the number of actual values [%d]" % (len(predicted), len(actual))
    return mean_squared_error(predicted, actual)**0.5


def mean_absolute_relative_error(predicted, actual):
    assert len(predicted) == len(actual), \
        "number of predicted values [%d] differs from the number of actual values [%d]" % (len(predicted), len(actual))
    total = 0
    for i in range(len(predicted)):
        total += abs(predicted[i] - actual[i]) / actual[i]
    return total / len(predicted)


def mean(values):
    return sum(values)/len(values)


# used for actual values in r**2 calculation
#  p. 242 Statistics for The Exploration and Analysis of Data 7th Ed.
def sum_of_squares(values):
    mean_value = mean(values)
    total = 0
    for i in range(len(values)):
        total += (values[i] - mean_value)**2
    return total


#  p. 242 Statistics for The Exploration and Analysis of Data 7th Ed.
def residual_sum_of_squares(predicted, actual):
    assert len(predicted) == len(actual), \
        "number of predicted values [%d] differs from the number of actual values [%d]" % (len(predicted), len(actual))
    total = 0
    for i in range(len(predicted)):
        total += (actual[i] - predicted[i])**2
    return total


#  p. 243 Statistics for The Exploration and Analysis of Data 7th Ed.
def coefficient_of_determination(predicted, actual):
    return 1 - (residual_sum_of_squares(predicted, actual)) / (sum_of_squares(predicted))


def r2_linear(predicted, actual):
    assert len(predicted) == len(actual), \
        "number of predicted values [%d] differs from the number of actual values [%d]" % (len(predicted), len(actual))
    n = len(predicted)
    sum_of_diffs = 0
    mean_actual = mean(actual)
    mean_predicted = mean(predicted)
    std_actual = statistics.stdev(actual)
    std_predicted = statistics.stdev(predicted)
    for i in range(n):
        sum_of_diffs += (actual[i] - mean_actual)*(predicted[i] - mean_predicted)
    return (sum_of_diffs / (std_actual * std_predicted) / n) ** 2


# according to the formula of keller
def r2_keller(predicted, actual):
    rmse2 = root_mean_square_error(predicted, actual)**2
    mse_obs = sum_of_squares(actual) / len(actual)
    return max([0, 1 - rmse2/mse_obs])


def access_quality_of_interpolation(grouped_samples, one_sample, function='rbf', function_type='linear',
                                    number_of_neighbors=6, power=2, write=False, r2formula='keller'):
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

    if function == 'idw':
        idw = InverseDistanceWeighting(numpy.asarray(known_locations), numpy.asarray(known_values), 10)
        # nearest_neighbors, epsilon, power, unknown_locations, weights
        interpolated = idw(number_of_neighbors, power, numpy.asarray(query_locations))
    else:

        lat_values = [point[0] for point in known_locations]
        lon_values = [point[1] for point in known_locations]
        alt_values = [point[2] for point in known_locations]

        target_lat_values = [point[0] for point in query_locations]
        target_lon_values = [point[1] for point in query_locations]
        target_alt_values = [point[2] for point in query_locations]

        if len(known_locations[0]) == 3:
            rbf = Rbf(lat_values, lon_values, alt_values, known_values, function=function_type)
            interpolated = rbf(target_lat_values, target_lon_values, target_alt_values)
        else:
            time_values = [point[3] for point in known_locations]
            target_time_values = [point[3] for point in query_locations]
            rbf = Rbf(lat_values, lon_values, alt_values, time_values, known_values, function=function_type)
            interpolated = rbf(target_lat_values, target_lon_values, target_alt_values, target_time_values)

    num_of_known.append(len(known_locations))
    num_of_query.append(len(query_locations))
    mae.append(mean_absolute_error(interpolated, control_values))
    mse.append(mean_squared_error(interpolated, control_values))
    rmse.append(root_mean_square_error(interpolated, control_values))
    mare.append(mean_absolute_relative_error(interpolated, control_values))
    if r2formula == 'keller':
        # use the formula of peck and devore
        r2.append(r2_keller(interpolated, control_values))
    elif r2formula == 'linear':
        # use the formula for a linear regression model
        r2.append(r2_linear(interpolated, control_values))
    else:
        # use the formula of Peck and Devore
        r2.append(coefficient_of_determination(interpolated, control_values))

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
        # copy all the samples after this sample to known locations / known values
        for k in range(i + 1, len(grouped_samples)):
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
        num_of_known.append(len(known_locations))
        num_of_query.append(len(query_locations))

        if function == 'idw':
            idw = InverseDistanceWeighting(numpy.asarray(known_locations), numpy.asarray(known_values), 10)
            # nearest_neighbors, epsilon, power, unknown_locations, weights
            interpolated = idw(number_of_neighbors, power, numpy.asarray(query_locations))
        else:
            lat_values = [point[0] for point in known_locations]
            lon_values = [point[1] for point in known_locations]
            alt_values = [point[2] for point in known_locations]

            target_lat_values = [point[0] for point in query_locations]
            target_lon_values = [point[1] for point in query_locations]
            target_alt_values = [point[2] for point in query_locations]

            if len(known_locations[0]) == 3:
                rbf = Rbf(lat_values, lon_values, alt_values, known_values, function=function_type)
                interpolated = rbf(target_lat_values, target_lon_values, target_alt_values)
            else:
                time_values = [point[3] for point in known_locations]
                target_time_values = [point[3] for point in query_locations]
                rbf = Rbf(lat_values, lon_values, alt_values, time_values, known_values, function=function_type)
                interpolated = rbf(target_lat_values, target_lon_values, target_alt_values, target_time_values)

        mae.append(mean_absolute_error(interpolated, control_values))
        mse.append(mean_squared_error(interpolated, control_values))
        rmse.append(root_mean_square_error(interpolated, control_values))
        mare.append(mean_absolute_relative_error(interpolated, control_values))
        if r2formula == 'keller':
            # use the formula of peck and devore
            r2.append(r2_keller(interpolated, control_values))
        elif r2formula == 'linear':
            # use the formula for a linear regression model
            r2.append(r2_linear(interpolated, control_values))
        else:
            # use the formula of Peck and Devore
            r2.append(coefficient_of_determination(interpolated, control_values))

    if write:
        if function == 'idw':
            writer = Writer('output/quality_idw_neigh_' + str(number_of_neighbors))
        else:
            writer = Writer('output/quality_rbf_' + function_type)
        # write_quality_test_to_csv(mae, mse, rmse, mare, r2, num_of_known, num_of_query):
        writer.write_quality_with_avg_to_csv(mae, mse, rmse, mare, r2, num_of_known, num_of_query)

    return statistics.mean(mae), statistics.mean(mse), statistics.mean(rmse), statistics.mean(mare), statistics.mean(r2)
