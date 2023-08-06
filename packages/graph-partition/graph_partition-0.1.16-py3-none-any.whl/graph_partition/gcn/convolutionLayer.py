import torch.nn as nn
from torch import matmul, Tensor
import torch


class ConvolutionLayer(nn.Module):
    def __init__(self, adjacency_matrix: Tensor, in_dimension: int, out_dimension: int):
        super().__init__()
        self.adjacency_matrix = adjacency_matrix
        self.in_dimension = in_dimension
        self.out_dimension = out_dimension
        self.__make_layer__()

    def __make_layer__(self):
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        weights = torch.FloatTensor(self.in_dimension, self.out_dimension).to(_device)
        self.weights = nn.Parameter(weights)
        # initialize weight
        nn.init.kaiming_uniform_(self.weights)

    def forward(self, x: Tensor):
        assert (
            x.shape[0] == self.adjacency_matrix.shape[0]
        ), "size mis-match between adjacency matrix and data"
        assert (
            x.shape[1] == self.in_dimension
        ), "size mis-match between in dimension and data"
        return matmul(matmul(self.adjacency_matrix, x), self.weights)
