"""
Distributions
=============

Distributions to use with borch.

It basically does some minor modifications to torch.distributions
"""
from borch.distributions.rv_distributions import *
from borch.distributions.kl_div import kl_divergence, kl_exists
from borch.distributions import distributions
