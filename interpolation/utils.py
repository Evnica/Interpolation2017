import numpy
import datetime


class TimeHandler:
    def __init__(self, timestamps):
        if isinstance(timestamps[0], datetime.date):
            self.epoch = datetime.datetime.utcfromtimestamp(0)
            self.times_in_seconds = [self.get_unix_time_in_seconds(dt) for dt in timestamps]
        else:
            self.times_in_seconds = [float(dt) for dt in timestamps]
        self.time_max = max(self.times_in_seconds)
        self.time_min = min(self.times_in_seconds)
        self.times_normalized = [self.get_normalized_timestamp(t) for t in self.times_in_seconds]

    def get_unix_time_in_seconds(self, dt):
        return (dt - self.epoch).total_seconds()

    def raise_to_fourth_dimension(self, points3d, time_scale):
        assert len(points3d) == len(self.times_normalized), \
            "number of points [%d] differs from the number of timestamps [%d]" \
            % (len(points3d), len(self.times_normalized))
        points4d = []
        if time_scale != 1:
            for i in range(len(points3d)):
                points4d.append([points3d[i][0], points3d[i][1], points3d[i][2],
                                 self.times_normalized[i] * time_scale])
        else:
            for i in range(len(points3d)):
                points4d.append([points3d[i][0], points3d[i][1], points3d[i][2],
                                 self.times_normalized[i]])
        return points4d

    def get_timestamp_from_scaled(self, scaled_timestamp, scale_factor):
        time_in_seconds_normalized = scaled_timestamp / scale_factor
        return time_in_seconds_normalized * (self.time_max - self.time_min) + self.time_min

    def get_normalized_timestamp(self, timestamp_in_seconds):
        return (timestamp_in_seconds - self.time_min) / (self.time_max - self.time_min)


def datetime_from_unix_seconds(unix_seconds):
        return datetime.datetime.fromtimestamp((unix_seconds - 2 * 60 * 60))


# divides given points, values and timestamps into groups, each of which is composed by means of simple random sampling
# without replacement
def divide_in_random(num_of_random_samples, points, values, timestamps, point_dimension=3):
    assert len(points) == len(values) == len(timestamps), 'number elements in points [%d], ' \
           'values [%d] and timestamps [%d] must be equal' % (len(points), len(values), len(timestamps))
    assert point_dimension == 3 or point_dimension == 4, 'point dimension must be 3 or 4'
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
        if point_dimension == 3:
            random_samples[sample_index][element_index] = \
                [[points[random_index][0], points[random_index][1], points[random_index][2]],
                 values[random_index], timestamps[random_index]]
        else:
            random_samples[sample_index][element_index] = [[points[random_index][0], points[random_index][1],
                                                            points[random_index][2], points[random_index][3]],
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


def info():
    return 'The Spatio-Temporal Interpolation tool interpolates weather observation data given in CSV format and ' \
           'saves interpolated data as a JSON file suitable for further visualization. The coordinates are normalized' \
           ' for interpolation and do not require homogeneity.\n' + \
           'You can choose from the following interpolation options:\n' + \
           '1. Spatial Inverse Distance Weighting Interpolation\n' + \
           '  - number of nearest neighbors for interpolation: from 2 to 50\n' + \
           '  - power: from 1 to 3\n' + \
           '  - spatial density: from 1 to 50 points for cube side\n' + \
           '2. Spatial Radial Basis Functions\n' + \
           '  - cubic (the less accurate of given functions)\n' + \
           '  - linear\n' + \
           '  - thin plate\n' + \
           '3, 4. Spatio-temporal IDW and RBF\n' + \
           '  - temporal step in seconds\n' + \
           '  - min - 2 second, max - interval between the first and the last measurement in the dataset\n' + \
            'NOTES:\n' + \
            '1. Interpolation with high temporal/spatial density will ' \
            'result in long processing times and very large output files. E.g. for a dataset with an input time ' \
            'interval of less than 1.5 hours interpolation with a density of 10 points per cube side and a temporal ' \
            'step of 30 seconds will result in 180 000 points (180 cubes with 1000 points each). The output JSON file' \
            ' size will make up about 11 Mb.\n' \
            '2. After interpolation is done, the quality of chosen interpolation method can be tested by means of ' \
            'tenfold cross validation. For big input datasets statistical evaluation of interpolation method quality ' \
            'can take a while.\n' \
            '3. The tool also converts input data in the JSON format. This can be done as a separate task or ' \
            'together with interpolation. Dataset description is provided in an info window upon completion as ' \
            'well as in the metadata of the output JSON file.\n' \
            '4. Output file name is a must only in case of interpolation. Input data converted into JSON, if ' \
            'done simultaneously with interpolation, is stored in the same folder as interpolation results. If ' \
            'done separately, it is stored under a chosen path or in the default output folder.\n\n' \
            '(c)Evnica, 2017'
