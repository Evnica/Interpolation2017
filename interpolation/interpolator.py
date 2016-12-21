from enum import Enum
from scipy.spatial import KDTree
import numpy


class InterpolationMethod(Enum):
    idw = 'Inverse Distance Weighting'
    idw_st = 'Spatio-Temporal IDW'
    rbf = 'Radial Basis Functions (RBFs)'
    rbf_st = 'Spatio-Temporal RBFs'


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
                                           %(len(points), len(values))
        self.storage = KDTree(points, leafsize=leaves)
        self.values = values
        self.weightedSum = None
        self.numberOfWeights = 0

    def __call__(self, nearest_neighbors, epsilon, power, unknown_locations, weights):
        """
        :param nearest_neighbors: positive int
            Number of nearest neighbors to consider for value calculation
        :param epsilon: non-negative float, optional
            Allow approximate nearest neighbors; the kth returned value is guaranteed to be no further than
            (1+eps) times the distance to the real kth nearest neighbor.
        :param power: float, 1 <= power <= infinity, optional
            Which Minkowski p-norm to use. 1 is the sum-of-absolute-values “Manhattan” distance 2 is the usual Euclidean
             distance infinity is the maximum-coordinate-difference distance
        :return: float or array of floats
            The interpolated values proceeding from the distances to the nearest neighbors and their values.
        """
        query_points = numpy.asarray(unknown_locations)
        if self.weightedSum is None:
            self.weightedSum = numpy.zeros(nearest_neighbors)

        self.distances, self.neighbor_locations = \
            self.storage.query(x=query_points, k=nearest_neighbors, eps=epsilon, p=power)
        interpolation = numpy.zeros((len(self.distances),) + numpy.shape(self.values[0]))

        i = 0
        for current_distances, nearest_neighbors_indices in zip(self.distances, self.neighbor_locations):
            for j in range(len(current_distances)):
                if current_distances[j] == 0:
                    current_distances[j] = 0.000000009
            # print(current_distances)
            current_weights = 1 / current_distances**power
            if weights is not None:
                current_weights *= weights[nearest_neighbors_indices]
            current_weights /= numpy.sum(current_weights)
            weighted_value = numpy.dot(current_weights, self.values[nearest_neighbors_indices])
            self.weightedSum += current_weights
            interpolation[i] = weighted_value
            i += 1
        return interpolation


