
__module_name__ = "__init__.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])
__version__ = "0.0.3"


## This function controls the main class object and for the most part,
## should be all that is needed by the user.
from ._neural_diffeq import _neural_diffeq as neural_diffeq

## This is the main class object. Normally not needed but creating access for ease of investigation.
from ._neural_diffeq import NeuralDiffEq as _NeuralDiffEq