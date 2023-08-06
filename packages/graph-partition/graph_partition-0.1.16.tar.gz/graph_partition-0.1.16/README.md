# Graph Partitioning

Graph Partitioning is an age-old problem with applications in various domains, such as 
routing vehicles for delivery and finding the right target for immunizations to control a 
pandemic. Graph Partitioning involves partitioning a graph’s vertices into roughly 
equal-sized subsets such that the total edge cost spanning the subsets is at most k. 
In this package we have implemented three major algorithms - 

## Authors

- [@somsubhra88](https://github.com/somsubhra88)

## Graph Convolution Networks (GCN) 

Graph Convolution Networks use neural networks on structured graphs. Graph convolutions are
generalizations of convolutions and are easier to apply in the spectral domain. Graph 
Convolutional Networks (GCN) which can use both - graph and node feature information. This
python implementation is mostly inspired from a paper wiritten by Thomas N. Kipf and 
Max Welling. [Paper](https://arxiv.org/abs/1609.02907)

## Spectral Clustering

The spectral clustering method is defined for general weighted graphs; it identifies K clusters
using the eigenvectors of a matrix.

## Constrained K-Means Clustering

K-means clustering implementation whereby a minimum and/or maximum size for each cluster 
can be specified.

This K-means implementation modifies the cluster assignment step (E in EM) by formulating 
it as a Minimum Cost Flow (MCF) linear network optimisation problem. This is then solved 
using a cost-scaling push-relabel algorithm and uses Google's Operations Research 
tools' SimpleMinCostFlow which is a fast C++ implementation.

## Installation

You can install the graph-partition from PyPI:
```shell
pip install graph-partition
```

## How to Use

Primarily there are three major algorithms are there
- Graph Convolutional Neural Network
- Spectral Clustering
- Constrained K-Means Clustering

### Using of Graph Convolutional Network

```python
import urllib.request
from scipy.spatial import distance_matrix
from graph_partition import *

# Artificial test Data
url = "https://cs.joensuu.fi/sipu/datasets/s1.txt"
data = urllib.request.urlopen(url)
ds = []
for line in data:
    ds.append([float(x) for x in line.strip().split()])

# Calculating the Const Matrix
cost_matrix = distance_matrix(ds[:50], ds[:50])

# Defining the GCN Model
gcn_model = GraphConvolutionNetwork(
    cost_matrix=cost_matrix, 
    num_class=2, 
    hidden_layers=10
    )
# GCN fit and predict
gcn_model.fit()

# Printing the cluster label
print(gcn_model.cluster_label)
# Printing the cluster evaluation metrics
print(gcn_model.evaluation_metric)
```

### Using of Spectral Clustering
```python
import urllib.request
from scipy.spatial import distance_matrix
from graph_partition import *

# Artificial test Data
url = "https://cs.joensuu.fi/sipu/datasets/s1.txt"
data = urllib.request.urlopen(url)
ds = []
for line in data:
    ds.append([float(x) for x in line.strip().split()])

# Calculating the Const Matrix
cost_matrix = distance_matrix(ds[:50], ds[:50])

# Defining Spectral Clustering Model
sc_model = SpectralClustering(cost_matrix=cost_matrix, num_class=2)

# Printing the cluster labels and evaluation metrics
print(sc_model.cluster_label)
print(sc_model.evaluation_metric)
```

### Using of Constrained K-Means Clustering
```python
import urllib.request
from graph_partition import *

# Artificial test Data
url = "https://cs.joensuu.fi/sipu/datasets/s1.txt"
data = urllib.request.urlopen(url)
ds = []
for line in data:
    ds.append([float(x) for x in line.strip().split()])

# Defining Spectral Clustering Model
k_means_model = ConstrainedKMeans(
    design_matrix=ds[:50], 
    num_class=2, 
    evaluate_metric=True
    )

# Printing the cluster labels and evaluation metrics
print(k_means_model.cluster_label)
print(k_means_model.evaluation_metric)
```

## Support

For any queries please contact via [email](mailto:somsubhra.ghosh88@gmail.com)