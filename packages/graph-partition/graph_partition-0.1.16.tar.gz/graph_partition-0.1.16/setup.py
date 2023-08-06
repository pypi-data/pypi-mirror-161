# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graph_partition',
 'graph_partition.evaluation_metric',
 'graph_partition.gcn',
 'graph_partition.k_means',
 'graph_partition.spectral_clustering']

package_data = \
{'': ['*']}

install_requires = \
['k-means-constrained==0.7.1',
 'numpy==1.23.1',
 'scikit-learn==1.1.1',
 'scipy>=1.8.1,<2.0.0',
 'torch==1.12.0']

setup_kwargs = {
    'name': 'graph-partition',
    'version': '0.1.16',
    'description': 'Graph Partitioning Algorithms',
    'long_description': '# Graph Partitioning\n\nGraph Partitioning is an age-old problem with applications in various domains, such as \nrouting vehicles for delivery and finding the right target for immunizations to control a \npandemic. Graph Partitioning involves partitioning a graph’s vertices into roughly \nequal-sized subsets such that the total edge cost spanning the subsets is at most k. \nIn this package we have implemented three major algorithms - \n\n## Authors\n\n- [@somsubhra88](https://github.com/somsubhra88)\n\n## Graph Convolution Networks (GCN) \n\nGraph Convolution Networks use neural networks on structured graphs. Graph convolutions are\ngeneralizations of convolutions and are easier to apply in the spectral domain. Graph \nConvolutional Networks (GCN) which can use both - graph and node feature information. This\npython implementation is mostly inspired from a paper wiritten by Thomas N. Kipf and \nMax Welling. [Paper](https://arxiv.org/abs/1609.02907)\n\n## Spectral Clustering\n\nThe spectral clustering method is defined for general weighted graphs; it identifies K clusters\nusing the eigenvectors of a matrix.\n\n## Constrained K-Means Clustering\n\nK-means clustering implementation whereby a minimum and/or maximum size for each cluster \ncan be specified.\n\nThis K-means implementation modifies the cluster assignment step (E in EM) by formulating \nit as a Minimum Cost Flow (MCF) linear network optimisation problem. This is then solved \nusing a cost-scaling push-relabel algorithm and uses Google\'s Operations Research \ntools\' SimpleMinCostFlow which is a fast C++ implementation.\n\n## Installation\n\nYou can install the graph-partition from PyPI:\n```shell\npip install graph-partition\n```\n\n## How to Use\n\nPrimarily there are three major algorithms are there\n- Graph Convolutional Neural Network\n- Spectral Clustering\n- Constrained K-Means Clustering\n\n### Using of Graph Convolutional Network\n\n```python\nimport urllib.request\nfrom scipy.spatial import distance_matrix\nfrom graph_partition import *\n\n# Artificial test Data\nurl = "https://cs.joensuu.fi/sipu/datasets/s1.txt"\ndata = urllib.request.urlopen(url)\nds = []\nfor line in data:\n    ds.append([float(x) for x in line.strip().split()])\n\n# Calculating the Const Matrix\ncost_matrix = distance_matrix(ds[:50], ds[:50])\n\n# Defining the GCN Model\ngcn_model = GraphConvolutionNetwork(\n    cost_matrix=cost_matrix, \n    num_class=2, \n    hidden_layers=10\n    )\n# GCN fit and predict\ngcn_model.fit()\n\n# Printing the cluster label\nprint(gcn_model.cluster_label)\n# Printing the cluster evaluation metrics\nprint(gcn_model.evaluation_metric)\n```\n\n### Using of Spectral Clustering\n```python\nimport urllib.request\nfrom scipy.spatial import distance_matrix\nfrom graph_partition import *\n\n# Artificial test Data\nurl = "https://cs.joensuu.fi/sipu/datasets/s1.txt"\ndata = urllib.request.urlopen(url)\nds = []\nfor line in data:\n    ds.append([float(x) for x in line.strip().split()])\n\n# Calculating the Const Matrix\ncost_matrix = distance_matrix(ds[:50], ds[:50])\n\n# Defining Spectral Clustering Model\nsc_model = SpectralClustering(cost_matrix=cost_matrix, num_class=2)\n\n# Printing the cluster labels and evaluation metrics\nprint(sc_model.cluster_label)\nprint(sc_model.evaluation_metric)\n```\n\n### Using of Constrained K-Means Clustering\n```python\nimport urllib.request\nfrom graph_partition import *\n\n# Artificial test Data\nurl = "https://cs.joensuu.fi/sipu/datasets/s1.txt"\ndata = urllib.request.urlopen(url)\nds = []\nfor line in data:\n    ds.append([float(x) for x in line.strip().split()])\n\n# Defining Spectral Clustering Model\nk_means_model = ConstrainedKMeans(\n    design_matrix=ds[:50], \n    num_class=2, \n    evaluate_metric=True\n    )\n\n# Printing the cluster labels and evaluation metrics\nprint(k_means_model.cluster_label)\nprint(k_means_model.evaluation_metric)\n```\n\n## Support\n\nFor any queries please contact via [email](mailto:somsubhra.ghosh88@gmail.com)',
    'author': 'somsubhra88',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
