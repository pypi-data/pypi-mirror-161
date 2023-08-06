from typing import List, Union
import numpy as np


class GetAgreementRateMetric:
    """
    Agreement Rate Metric
    ------------------------------------------------------------------------------------------------------------------------
    1. For every point i find the k-nearest neighbors, using the input cost Matrix D .
    There will a n x k matrix (neighborhood matrix) that need to be computed for this purpose. The rows will
    contain the indices of the k the closest neighboring points corresponding to row number i. More formally, if we call
    this matrix P, p_ij will contain the index of the jth the closest point to point i.

    2. Let a_i stand for the number of points that are in the k-nearest neighbor list for point i as well as having the
    same cluster label
                The agreement rate will be equal to  sum(a_i for all the points)/k*n
    """

    _k_ = 12

    def __init__(
        self,
        cost_matrix: List[List[Union[float, int]]],
        cluster_label: List,
        num_cluster: int,
    ):
        self.cost_matrix = cost_matrix
        self.cluster_label = cluster_label
        self.num_cluster = num_cluster
        self.dimension = len(cost_matrix)
        # If the dimension is less than the neighbour
        self._k_ = min(self.dimension, self._k_)
        # Converting the cluster list to label list
        self.cluster_label = self.__convert_cluster_list__(
            cluster_label=self.cluster_label, num_cluster=num_cluster
        )
        assert len(self.cluster_label) == self.dimension, (
            f"dimension of cost matrix {self.dimension} and "
            f"the label is {len(self.cluster_label)}"
        )
        # Nearest Neighbour Matrix indicator
        self._nearest_neighbour = np.zeros((self.dimension, self._k_))
        self._calculate_arm()

    def _generate_neighbour_matrix(self):
        for i in range(self.dimension):
            self._nearest_neighbour[i, :] = np.argsort(np.array(self.cost_matrix[i]))[
                : self._k_
            ]

    def _calculate_arm(self):
        self._generate_neighbour_matrix()
        _arm = 0
        for i in range(self.dimension):
            for j in self._nearest_neighbour[i]:
                if self.cluster_label[i] == self.cluster_label[int(j)]:
                    _arm += 1
        self.ARM = _arm / (self._k_ * self.dimension)

    @classmethod
    def __convert_cluster_list__(cls, cluster_label: List, num_cluster: int) -> List:
        if isinstance(cluster_label[0], int):
            return cluster_label
        else:
            dimension = sum([len(x[1]) for x in cluster_label])
            _cluster_label = np.zeros(dimension)
            for c in range(num_cluster):
                for order in cluster_label[c][1]:
                    _cluster_label[order.order_sequence] = c
            return [int(x) for x in _cluster_label]
