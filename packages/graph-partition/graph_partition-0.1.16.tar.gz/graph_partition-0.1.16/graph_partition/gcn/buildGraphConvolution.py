from typing import Union, List
import torch.nn as nn
from torch import Tensor
import torch

from graph_partition.gcn.convolutionLayer import ConvolutionLayer


class BuildGraphConvolution(nn.Module):
    def __init__(
        self,
        adjacency_matrix: Tensor,
        num_features: int,
        num_class: int,
        hidden_layers: Union[List[int], int],
        dropout_rate: float = 0.1,
    ):
        super().__init__()
        self.adjacency_matrix = adjacency_matrix
        self.num_features = num_features
        self.num_class = num_class
        if isinstance(hidden_layers, int):
            self.hidden_layers = [hidden_layers]
        else:
            self.hidden_layers = hidden_layers

        self.dropout_rate = dropout_rate
        # Model definition
        self.model = None
        self.__build__()

    def __build__(self):
        _layers = [
            ConvolutionLayer(
                adjacency_matrix=self.adjacency_matrix,
                in_dimension=self.num_features,
                out_dimension=self.hidden_layers[0],
            ),
            nn.ReLU(),
            nn.Dropout(p=self.dropout_rate),
        ]
        # Loop for rest of the layers
        for i in range(len(self.hidden_layers) - 1):
            _layers.append(
                ConvolutionLayer(
                    adjacency_matrix=self.adjacency_matrix,
                    in_dimension=self.hidden_layers[i],
                    out_dimension=self.hidden_layers[i + 1],
                )
            )
            _layers.append(nn.ReLU())
            _layers.append(nn.Dropout(p=self.dropout_rate))

        # Adding the output layer
        _layers.append(
            ConvolutionLayer(
                adjacency_matrix=self.adjacency_matrix,
                in_dimension=self.hidden_layers[-1],
                out_dimension=self.num_class,
            )
        )
        _layers.append(nn.Softmax(dim=1))
        self.model = (
            nn.Sequential(*_layers)
            .double()
            .to("cuda" if torch.cuda.is_available() else "cpu")
        )

    def forward(self, x: Tensor):
        return self.model(x)
