from typing import List, Tuple
from collections import Counter


def measure_cluster_imbalance(cluster_index: List) -> Tuple[int, int, float]:
    _freq_distribution = Counter(cluster_index)
    _num_cluster = len(_freq_distribution)
    _max_cluster_index = max(_freq_distribution, key=_freq_distribution.get)
    _min_cluster_index = min(_freq_distribution, key=_freq_distribution.get)
    _ideal_cluster_size = len(cluster_index) / float(_num_cluster)
    return (
        _freq_distribution[_min_cluster_index],
        _freq_distribution[_max_cluster_index],
        (
            _freq_distribution[_max_cluster_index]
            - _freq_distribution[_min_cluster_index]
        )
        / _ideal_cluster_size,
    )
