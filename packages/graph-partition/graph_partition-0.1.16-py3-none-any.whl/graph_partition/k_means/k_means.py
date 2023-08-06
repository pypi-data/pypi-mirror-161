from typing import List, Union

import numpy as np
from k_means_constrained import KMeansConstrained
from numpy import ndarray
from scipy.spatial import distance_matrix
from sklearn.cluster import KMeans

from graph_partition.evaluation_metric.evaluate_metric import (
    evaluate_clustering_metrics,
)


class ConstrainedKMeans:
    def __init__(
        self,
        design_matrix: Union[List[List], ndarray],
        num_class: int,
        constrained: bool = True,
        evaluate_metric: bool = False,
    ):
        """
        :param design_matrix: array-like, shape=(n_samples, n_features)
        :param num_class: The number of clusters to form
        """
        if isinstance(design_matrix, ndarray):
            self.design_matrix = design_matrix
        else:
            self.design_matrix = np.array(design_matrix)
        self.num_class = num_class
        if constrained:
            self.cluster_label = self.get_constrained_cluster()
        else:
            self.cluster_label = self.get_unconstrained_cluster()

        # Calculating the Distance Matrix
        if evaluate_metric:
            _cost_matrix = distance_matrix(
                self.design_matrix, self.design_matrix
            ).tolist()
            self.evaluation_metric = evaluate_clustering_metrics(
                _cost_matrix, self.cluster_label, self.num_class
            )
        else:
            self.evaluation_metric = None

    def get_constrained_cluster(self) -> List:
        _min_size = int(round(0.9 * self.design_matrix.shape[0] / self.num_class))
        _max_size = int(round(1.1 * self.design_matrix.shape[0] / self.num_class))

        _model = KMeansConstrained(
            n_clusters=self.num_class,
            size_min=_min_size,
            size_max=_max_size,
            max_iter=10000,
            n_jobs=-1,
            random_state=0,
        )

        _model.fit(self.design_matrix)

        return _model.labels_.tolist()

    def get_unconstrained_cluster(self) -> List:
        _model = KMeans(n_clusters=self.num_class, random_state=0)
        _model.fit(self.design_matrix)
        return _model.labels_.tolist()
