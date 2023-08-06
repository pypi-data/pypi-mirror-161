
__module_name__ = "_compose_nn_sequential.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import torch
from collections import OrderedDict


class _NeuralNetwork:
    def __init__(self):

        self._nn_dict = OrderedDict()
        self._activation_count = 0
        self._hidden_layer_count = 0
        self._dropout_count = 0

    def input_layer(self, in_dim, nodes):

        self._nn_dict["hidden_layer_0"] = torch.nn.Linear(in_dim, nodes)

    def activation_function(self, activation_function=torch.nn.LeakyReLU()):

        self._activation_count += 1
        self._nn_dict[
            "activation_{}".format(self._activation_count)
        ] = activation_function

    def dropout(self, probability=0.1):

        self._dropout_count += 1
        self._nn_dict["dropout_{}".format(self._dropout_count)] = torch.nn.Dropout(
            probability
        )

    def hidden_layer(self, nodes_m, nodes_n):

        self._hidden_layer_count += 1
        self._nn_dict["hidden_{}".format(self._hidden_layer_count)] = torch.nn.Linear(
            nodes_m, nodes_n
        )

    def output_layer(self, nodes, out_dim):

        self._nn_dict["output_layer"] = torch.nn.Linear(nodes, out_dim)

    def compose(self):

        return torch.nn.Sequential(self._nn_dict)


def _compose_nn_sequential(
    in_dim=50,
    out_dim=50,
    activation_function=torch.nn.Tanh(),
    hidden_layer_nodes={1: [500, 500], 2: [500, 500]},
    dropout_probability=0.1,
):

    """
    Compose a sequential linear torch neural network
    
    Parameters:
    -----------
    in_dim
        neural network input dimension. dimensionality of data passed to neural network.
        default: 50
        type: int
        
    out_dim
        neural network out dimension
        default: 50
        type: int
        
    activation_function
        default: torch.nn.Tanh()
        type: torch.nn.modules.activation
        
    hidden_layer_nodes
        dictionary describing the hidden layer architecture in addition to the first/input hidden layer.
        Connecting node shapes are automatically adjusted from hidden_layer_0 (input) to the second layer
        as well as the final hidden layer to the output dimension.
        default: {1:[500,500], 2:[500,500]}
        type: dict
        
    dropout_probability
        probability of a dropout for the nodes in a given layer.
        default: 0
        type: float
    """

    nn = _NeuralNetwork()

    hidden_layer_keys = list(hidden_layer_nodes.keys())

    nn.input_layer(in_dim=in_dim, nodes=hidden_layer_nodes[hidden_layer_keys[0]][0])
    nn.activation_function(activation_function)

    for layer in hidden_layer_keys:
        layer_nodes = hidden_layer_nodes[layer]
        if dropout_probability:
            nn.dropout(probability=dropout_probability)
        nn.hidden_layer(layer_nodes[0], layer_nodes[1])
        nn.activation_function(activation_function)

    if dropout_probability:
        nn.dropout(probability=dropout_probability)
    nn.output_layer(out_dim=out_dim, nodes=hidden_layer_nodes[hidden_layer_keys[-1]][1])

    return nn.compose()
