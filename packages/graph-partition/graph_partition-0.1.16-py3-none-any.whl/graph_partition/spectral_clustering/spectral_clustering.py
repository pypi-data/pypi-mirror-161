from typing import List
import numpy as np

from graph_partition.evaluation_metric.evaluate_metric import (
    evaluate_clustering_metrics,
)
from graph_partition.k_means.k_means import ConstrainedKMeans


class SpectralClustering:
    def __init__(
        self, cost_matrix: List[List], num_class: int, constrained: bool = True
    ):
        self.cost_matrix = cost_matrix
        self.num_cluster = num_class
        self.constrained = constrained
        self.cluster_label = self.cluster()
        self.evaluation_metric = evaluate_clustering_metrics(
            self.cost_matrix, self.cluster_label, self.num_cluster
        )

    def transform(self):
        _cost_matrix = np.array(self.cost_matrix)
        _cost_matrix = (_cost_matrix + _cost_matrix.T) / 2
        _row_sum = _cost_matrix.sum(axis=1)
        _normalized_cost_matrix = _cost_matrix / _row_sum[:, np.newaxis]
        return _normalized_cost_matrix

    def cluster(self):
        _cost_matrix = self.transform()
        _eigen_values, _eigen_vectors = np.linalg.eig(_cost_matrix)
        # Sanity Check: to avoid the complex numbers in eigen decomposition
        _eigen_values = np.real_if_close(_eigen_values, tol=1)
        _eigen_vectors = np.real_if_close(_eigen_vectors, tol=1)
        assert (
            np.abs(_eigen_values[0] - 1) < 1e-06
        ), f"First Eigen Value is not equal to 1, it is {round(_eigen_values[0], 4)}"
        # Discard the first eigen vector
        _k_means_model = ConstrainedKMeans(
            _eigen_vectors[:, 1:],
            num_class=self.num_cluster,
            constrained=self.constrained,
        )
        return _k_means_model.cluster_label
