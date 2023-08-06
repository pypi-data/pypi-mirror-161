from typing import List, Union, Tuple


class GetClusterDiameter:
    def __init__(
        self,
        cost_matrix: List[List[Union[float, int]]],
        cluster_label: List[int],
        num_cluster: int,
    ):
        self.cost_matrix = cost_matrix
        self.cluster_label = cluster_label
        self.num_cluster = num_cluster
        self.dimension = len(cost_matrix)

        assert (
            len(self.cluster_label) == self.dimension
        ), "dimension of cost matrix and the label is different"
        # Cluster-wise diameter dictionary
        self._cluster_diameters = {}
        # K-means metrics with cluster sum of distances
        self._cluster_distance_sum = 0
        self._calculate_diameters()

    @property
    def cluster_diameters(self):
        return self._cluster_diameters

    @cluster_diameters.setter
    def cluster_diameters(self, key_value_pair: tuple):
        if key_value_pair[0] in self._cluster_diameters:
            del self._cluster_diameters[key_value_pair[0]]
        self._cluster_diameters[key_value_pair[0]] = round(key_value_pair[1], 4)

    @property
    def cluster_distance_sum(self):
        return self._cluster_distance_sum

    @cluster_distance_sum.setter
    def cluster_distance_sum(self, value: Union[int, float]):
        self._cluster_distance_sum += value

    def _calculate_diameter(
        self, cluster_label: Union[int, str]
    ) -> Tuple[Union[float, int], Union[float, int]]:
        _elements = [
            idx for idx, val in enumerate(self.cluster_label) if val == cluster_label
        ]
        _cost_matrix = [
            [c_val for c_index, c_val in enumerate(r_val) if c_index in _elements]
            for r_index, r_val in enumerate(self.cost_matrix)
            if r_index in _elements
        ]
        _n = len(_cost_matrix)  # size of the cluster
        if _n <= 1:
            return 0, 0
        else:
            return max(sum(_cost_matrix, [])), sum([sum(x) for x in _cost_matrix]) / (
                _n * (_n - 1)
            )

    def _calculate_diameters(self):
        _unique_clusters = list(range(self.num_cluster))
        for lbl in _unique_clusters:
            _dia, _distance_sum = self._calculate_diameter(lbl)
            self.cluster_diameters = (lbl, _dia)
            self.cluster_distance_sum = _distance_sum
