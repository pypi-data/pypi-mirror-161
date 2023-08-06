# ![neural-diffeqs](/assets/neural-diffeqs.logo.svg)

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/neural_diffeqs.svg)](https://pypi.python.org/pypi/pydk/)
[![PyPI version](https://badge.fury.io/py/neural_diffeqs.svg)](https://badge.fury.io/py/pydk)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A PyTorch-based library for the instantiation of neural differential equations.

### Installation

To install with [**`pip`**](https://pypi.org/project/neural-diffeqs/):
```python
pip install neural_diffeqs
```

To install the development version from GitHub:
```BASH
git clone https://github.com/mvinyard/neural-diffeqs.git; cd ./neural-diffeqs
pip install -e .
```

### Examples

You can instantiate an **`SDE`** or **`ODE`** as follows:
```python
from neural_diffeqs import neural_diffeq

SDE = neural_diffeq()
# this can be passed to `torchsde.sdeint`

ODE = neural_diffeq(sigma_hidden=False)
# this can be passed to `torchdiffeq.odeint`
```

You can also define the **`SDE`** or **`ODE`** as potential functions. These can be passed to `torchsde.sdeint` and `torchdiffeq.odeint` just the same as above:

```python
from neural_diffeqs import neural_diffeq

SDE = neural_diffeq(mu_potential=True, sigma_potential=False)

ODE = neural_diffeq(sigma_hidden=False)
```

There are several other parameters that are easily tweakable, including the composition of the neural network(s), using the following arguments:

**To adjust the parameters of the `mu` neural network**:

 * **`mu_hidden`**  - a `dict` (e.g.,: ``{1:[400,400], 2:[400,400]}``)
 * **`mu_in_dim`**
 * **`mu_out_dim`**
 * **`mu_potential`** - if this parameter is `True`, the output dimension of the output layer is changed to `1`.
 * **`mu_init_potential`** - when `mu_potential = True`, this argument initializes the output value of `mu`. By default, this returns a `torch.zeros([])` tensor.
 * **`mu_activation_function`**
 * **`mu_dropout`**

**Similarly, the `sigma` neural network can be controlled with these parameters**:


 * **`sigma_hidden`**  - a `dict` (e.g.,: ``{1:[400,400], 2:[400,400]}``)
 * **`sigma_in_dim`**
 * **`sigma_out_dim`**
 * **`sigma_potential`** - if this parameter is `True`, the output dimension of the output layer is changed to `1`.
 * **`sigma_init_potential`** - when `sigma_potential = True`, this argument initializes the output value of `sigma`. By default, this returns a `torch.zeros([])` tensor.
 * **`sigma_activation_function`**
 * **`sigma_dropout`**
    
    
**There are also general parameters that are passed / required of the SDE when using the `torchsde` interface**:

 * **`brownian_size`**
 * **`noise_type`**
 * **`sde_type`**

For more examples, please see the notebooks in [**`./examples/`**](./examples/). For documentation related neural ODEs and **`torchdiffeq`**, see the [**`torchdiffeq`** repository](https://github.com/rtqichen/torchdiffeq). For documentation related to neural SDEs and **`torchsde`**, see the [**`torchsde`** repository](https://github.com/google-research/torchsde).

---
**Questions or suggestions**? Open an [issue](https://github.com/mvinyard/neural-diffeqs/issues/new) or send an email to [Michael Vinyard](mailto:mvinyard@broadinstitute.org).
