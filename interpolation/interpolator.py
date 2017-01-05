from enum import Enum
from scipy.interpolate import Rbf
from scipy.spatial import KDTree
from interpolation.iohelper import Writer
from interpolation.utils import TimeHandler
import numpy


def interpolate_with_idw(analysis, points, values, filename, times=None):
    writer = Writer(filename)
    if times is None:
        grid = analysis.generate_grid()
        current = numpy.asarray(points)
        values = numpy.asarray(values)
        look_for = numpy.asarray(grid)
        grids = [grid]
        tree = InverseDistanceWeighting(current, values, 10)
        interpol = tree(analysis.nearest_neighbors, analysis.power, look_for)
        analysis.value_max = max(interpol)
        analysis.value_min = min(interpol)
        grid_values = [interpol]
    else:
        time_handler = TimeHandler(times)
        points4d = time_handler.raise_to_fourth_dimension(points, 1)
        grids = analysis.generate_time_series_grids(times)
        current = numpy.asarray(points4d)
        values = numpy.asarray(values)
        tree = InverseDistanceWeighting(current, values, 10)
        grid_values = []
        for i in range(len(grids)):
            look_for = numpy.asarray(grids[i])
            grid_values.append(tree(analysis.nearest_neighbors, analysis.power, look_for))
        max_values = []
        min_values = []
        for i in range(len(grid_values)):
            max_values.append(max(grid_values[i]))
            min_values.append(min(grid_values[i]))
        analysis.value_max = max(max_values)
        analysis.value_min = min(min_values)
    writer.write_time_series_grids_to_json(analysis=analysis, grids=grids, grid_values=grid_values)


def interpolate_with_rbf(analysis, points, values, filename, times=None):
    writer = Writer(filename)
    lat_values = [point[0] for point in points]
    lon_values = [point[1] for point in points]
    alt_values = [point[2] for point in points]
    # 3 d points - pure spatial interpolation
    if times is None:
        analysis.dimension = 3
        grid = analysis.generate_grid()
        grids = [grid]
        target_lat_values = [point[0] for point in grid]
        target_lon_values = [point[1] for point in grid]
        target_alt_values = [point[2] for point in grid]
        rbf = Rbf(lat_values, lon_values, alt_values, values, function=analysis.function)
        interpolated = [rbf(target_lat_values, target_lon_values, target_alt_values)]
    else:
        analysis.dimension = 4
        time_handler = TimeHandler(times)
        points4d = time_handler.raise_to_fourth_dimension(points3d=points, time_scale=1)
        time_values = [point[3] for point in points4d]
        grids = analysis.generate_time_series_grids(times)
        interpolated = []
        for i in range(len(grids)):
            target_lat_values = [point[0] for point in grids[i]]
            target_lon_values = [point[1] for point in grids[i]]
            target_alt_values = [point[2] for point in grids[i]]
            target_time_values = [point[3] for point in grids[i]]
            rbf = Rbf(lat_values, lon_values, alt_values, time_values, values, function=analysis.function)
            interpolated.append(rbf(target_lat_values, target_lon_values, target_alt_values, target_time_values))
    writer.write_time_series_grids_to_json(analysis=analysis, grids=grids, grid_values=interpolated)


class InterpolationMethod(Enum):
    IDW = 'IDW: Spatial Inverse Distance Weighting'
    IDW_ST = 'IDW: Spatio-Temporal Inverse Distance Weighting'
    RBF = 'RBF: Spatial Radial Basis Functions'
    RBF_ST = 'RBF: Spatio-Temporal Radial Basis Functions'

    @staticmethod
    def as_string_sequence():
        methods = []
        for name, member in InterpolationMethod.__members__.items():
            methods.append(member.value)
        return methods


class RadialBasisFunctions(Enum):
    multiquadric = 'multiquadric'  # sqrt((r / self.epsilon) ** 2 + 1)
    inverse = 'inverse'  # 1.0 / sqrt((r / self.epsilon) ** 2 + 1)
    gaussian = 'gaussian'  # : exp(-(r / self.epsilon) ** 2)
    cubic = 'cubic'  # r ** 3
    quintic = 'quintic'  # r ** 5
    thin_plate = 'thin_plate'  # r ** 2 * log(r)
    linear = 'linear'  # r


class InverseDistanceWeighting:
    """
    InverseDistanceWeighting class is based on a KDTree for nearest neighbor search
    Parameters
    ----------
    points: array_like
        scattered 3D points and
    values: array_like
        corresponding measurement values; the length should be equal to points length
    leaves: int
        is the number of tree leaves
    """

    def __init__(self, points, values, leaves):
        assert len(points) == len(values), "number of measurement values [%d] differs from the number of points [%d]" \
                                           % (len(points), len(values))
        self.storage = KDTree(points, leafsize=leaves)
        self.values = values
        self.weightedSum = None
        self.numberOfWeights = 0

    def __call__(self, nearest_neighbors, power, unknown_locations):
        """
        :param nearest_neighbors: positive int
            Number of nearest neighbors to consider for value calculation
        :param power: float, 1 <= power <= infinity, optional
            Which Minkowski p-norm to use. 1 is the sum-of-absolute-values “Manhattan” distance,
            2 is the usual Euclidean distance
        :return: float or array of floats
            The interpolated values proceeding from the distances to the nearest neighbors and their values.
        """
        query_points = numpy.asarray(unknown_locations)
        if self.weightedSum is None:
            self.weightedSum = numpy.zeros(nearest_neighbors)

        self.distances, self.neighbor_locations = \
            self.storage.query(x=query_points, k=nearest_neighbors, p=power)
        # noinspection PyTypeChecker
        interpolation = numpy.zeros((len(self.distances),) + numpy.shape(self.values[0]))

        i = 0
        for current_distances, nearest_neighbors_indices in zip(self.distances, self.neighbor_locations):
            for j in range(len(current_distances)):
                if current_distances[j] == 0:
                    current_distances[j] = 0.000000009
            # print(current_distances)
            current_weights = 1 / current_distances**power
            # noinspection PyTypeChecker
            current_weights /= numpy.sum(current_weights)
            # noinspection PyTypeChecker
            weighted_value = numpy.dot(current_weights, self.values[nearest_neighbors_indices])
            self.weightedSum += current_weights
            interpolation[i] = weighted_value
            i += 1
        return interpolation
