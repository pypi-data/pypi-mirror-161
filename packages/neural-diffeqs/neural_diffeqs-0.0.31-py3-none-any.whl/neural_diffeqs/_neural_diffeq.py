

__module_name__ = "_neural_diffeq.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import torch

# import local dependencies #
# ------------------------- #
from ._compose_nn_sequential import _compose_nn_sequential


#### -------------------------------------------------------- ####
    
def _potential(net, x):
    return net(x.requires_grad_())

def _neg_gradient(potential, y):
    return torch.autograd.grad(
        potential,
        y.requires_grad_(),
        torch.ones_like(potential),
        create_graph=True,
    )[0]


def _neg_grad_of_potential(net, y):
    return _neg_gradient(_potential(net, y), y)


def _mu_as_potential(mu, y):
    return _neg_grad_of_potential(mu, y)


def _sigma_as_potential(sigma, y, brownian_size):
    return _neg_grad_of_potential(sigma, y).view(y.shape[0], y.shape[1], brownian_size)


#### -------------------------------------------------------- ####


def _mu(mu, y):
    return mu(y)


def _sigma(sigma, y, brownian_size):
    return sigma(y).view(y.shape[0], y.shape[1], brownian_size)


#### -------------------------------------------------------- ####


def _initialize_potential_param(net, init_value=None):
    
    potential_param = list(net.parameters())[-1].data
    if not init_value:
        potential_param = torch.zeros(potential_param.shape)
    else:
        potential_param = torch.full(potential_param.shape, init_value)
        

#### -------------------------------------------------------- ####


class NeuralDiffEq(torch.nn.Module):
    def __init__(
        self,
        mu_neural_net,
        mu_potential=True,
        mu_init_potential=None,
        sigma_neural_net=False,
        sigma_potential=False,
        sigma_init_potential=None,
        brownian_size=1,
        noise_type="general",
        sde_type="ito",
    ):
        super(NeuralDiffEq, self).__init__()
        
        self._mu = _mu
        self._sigma = _sigma
        self._brownian_size = brownian_size
        self._mu_potential = mu_potential
        self.noise_type = noise_type
        self.sde_type = sde_type
        self._sigma_potential = sigma_potential
        
        self.mu = mu_neural_net
        self.sigma = sigma_neural_net
        
        if self._mu_potential:
            self._mu = _mu_as_potential
            _initialize_potential_param(self.mu)
            
        if self.sigma:
            if self._sigma_potential:
                self._sigma = _sigma_as_potential
                _initialize_potential_param(self.sigma)
    
    def psi_mu(self, x):
        return self.mu(x.requires_grad_())

    def psi_sigma(self, x):
        return self.sigma(x.requires_grad_())
            
    def f(self, t, y0):
        return self._mu(self.mu, y0)

    def forward(self, t, y0):
        return self._mu(self.mu, y0)

    def g(self, t, y0):
        return self._sigma(self.sigma, y0, self._brownian_size)

    #### -------------------------------------------------------- ####


def _neural_diffeq(
    mu_hidden={1: [400, 400]},
    mu_in_dim=50,
    mu_out_dim=50,
    mu_potential=True,
    mu_init_potential=None,
    mu_activation_function=torch.nn.Tanh(),
    mu_dropout=0.2,
    sigma_hidden={1: [400, 400]},
    sigma_in_dim=50,
    sigma_out_dim=50,
    sigma_potential=False,
    sigma_init_potential=None,
    sigma_activation_function=torch.nn.Tanh(),
    sigma_dropout=0.2,
    brownian_size=1,
    noise_type="general",
    sde_type="ito",
):
    """
    Flexibly instantiate a neural differential equation.

    Parameters:
    -----------
    mu_hidden
        dictionary-style composition of hidden architecture of the mu (drift) neural network. 
        type: dict
        default: {1:[400,400]}
        
    mu_in_dim
        Dimension size of the input state to the mu neural network.
        type: int
        default: 50

    mu_out_dim
        Dimension size of the output state to the mu neural network.
        type: int
        default: 50
        
    mu_potential
        Boolean indicator that dictates whether the mu (drift) component / neural network should be treated
        as a gradient potential function. In other words, the output parameter dimension of the mu
        neural network = 1 and the gradient of the potential of this value is mapped back to the 
        dimension of the input. This is the output when passed through `torchdiffeq.odeint` or `torchsde.sdeint`.
        type: bool
        default: True
        
    mu_init_potential
        The value of the output parameter of the mu potential net. If None, torch.zeros([]) is used by default.
        type: NoneType or float
        default: None
        
    mu_activation_function
        Torch activation function of the mu (drift) neural network
        type: torch.nn.modules.activation
        default: torch.nn.Tanh()
       
    mu_dropout
        Probability of dropout [0,1] in the mu neural network architecture. If not False or 0, a probability between 
        0 and 1 of node dropout for a given linear layer. If False, no dropout filters are added to the mu neural
        network architecture.
        type: float or bool
        default: 0.2
        
    sigma_hidden
        dictionary-style composition of hidden architecture of the sigma (diffusion) neural network. Also may
        function as a boolean indicator to exclude a stochastic diffusion term. To negate stochastic
        term (thereby composing an ODE instead of an SDE), set `sigma=False`.
        type: dict
        default: {1:[400,400]}
        
    sigma_in_dim
        Dimension size of the input state to the sigma neural network.
        type: int
        default: 50

    sigma_out_dim
        Dimension size of the output state to the sigma neural network.
        type: int
        default: 50
        
    sigma_potential
        Boolean indicator that dictates whether the sigma component / neural network should be treated
        as a gradient potential function. In other words, the output parameter dimension of the sigma
        neural network = 1 and the gradient of the potential of this value is mapped back to the 
        dimension of the input. This is the output when passed through `torchdiffeq.odeint` or `torchsde.sdeint`.
        type: bool
        default: True
        
    sigma_init_potential
        The value of the output parameter of the sigma potential net. If None, torch.zeros([]) is used by default.
        type: NoneType or float
        default: None
        
    sigma_activation_function
        Torch activation function of the sigma (diffusion) neural network
        type: torch.nn.modules.activation
        default: torch.nn.Tanh()

    sigma_activation_function
        Torch activation function of the sigma (diffusion) neural network
        type: torch.nn.modules.activation
        default: torch.nn.Tanh()

    sigma_dropout
        Probability of dropout [0,1] in the sigma neural network architecture. If not
        False or 0, a probability between 0 and 1 of node dropout for a given linear layer. If False,
        no dropout filters are added to the sigma neural network architecture.
        type: float or bool
        default: 0.2
        
    brownian_size
        Dimension-wise complexity of the stochastic brownian noise.
        type: int
        default: 1

    Returns:
    --------
    NeuralDiffEq
    """

    if sigma_hidden:
        if sigma_potential:
            sigma_out_dim = 1
        sigma = _compose_nn_sequential(
            in_dim=sigma_in_dim,
            out_dim=sigma_out_dim,
            hidden_layer_nodes=sigma_hidden,
            activation_function=sigma_activation_function,
            dropout_probability=sigma_dropout,
        )
    else:
        sigma=False

    if mu_potential:
        mu_out_dim = 1
    mu = _compose_nn_sequential(
        in_dim=mu_in_dim,
        out_dim=mu_out_dim,
        hidden_layer_nodes=mu_hidden,
        activation_function=mu_activation_function,
        dropout_probability=mu_dropout,
    )
    
    return NeuralDiffEq(
        mu_neural_net=mu,
        mu_potential=mu_potential,
        mu_init_potential=mu_init_potential,
        sigma_neural_net=sigma,
        sigma_potential=sigma_potential,
        sigma_init_potential=sigma_init_potential,
        brownian_size=brownian_size,        
        noise_type=noise_type,
        sde_type=sde_type,
    )
