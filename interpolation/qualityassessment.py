# statistical methods of error analysis meant to assess interpolation quality


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
    return 1 - (residual_sum_of_squares(predicted, actual)) / (sum_of_squares(actual))
