import numpy


# divides given points, values and timestamps into groups, each of which is composed by means of simple random sampling
# without replacement
def divide_in_random(num_of_random_samples, points, values, timestamps):
    assert len(points) == len(values) == len(timestamps), 'number elements in points [%d], ' \
           'values [%d] and timestamps [%d] must be equal' % (len(points), len(values), len(timestamps))
    n = len(points)
    sample_size = n // num_of_random_samples
    rest = n - (sample_size * num_of_random_samples)
    if rest > 0.5 * sample_size:  # if rest is more than 50% of sample size, values should be split differently
        if rest == sample_size:
            sample_size = (n - 1) // (num_of_random_samples - 1)
        else:
            sample_size = n // (num_of_random_samples - 1)
    random_samples = numpy.empty(shape=(num_of_random_samples - 1, sample_size, 3), dtype=object)
    #  print(random_samples)
    sample_index = 0
    number_of_removed_entries = 0
    element_index = 0
    # print('Sample 1')
    for i in range(sample_size * (num_of_random_samples - 1)):
        random_index = numpy.random.randint(0, n - number_of_removed_entries)
        # print(random_index)
        random_samples[sample_index][element_index] = \
            [[points[random_index][0], points[random_index][1], points[random_index][2]],
             values[random_index], timestamps[random_index]]
        del (points[random_index])
        del (values[random_index])
        del (timestamps[random_index])
        number_of_removed_entries += 1
        element_index += 1
        if element_index >= sample_size:
            sample_index += 1
            # print("Sample " + str(sample_index+1))
            element_index = 0
    last_sample = numpy.empty(shape=(len(points), 3), dtype=object)
    for i in range(len(points)):
        last_sample[i][0] = points[i]
        last_sample[i][1] = values[i]
        last_sample[i][2] = timestamps[i]
    return random_samples, last_sample
