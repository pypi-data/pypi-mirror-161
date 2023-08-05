"""
Posterior
=========

The concept of posteriors is as important as the concept of modules in the borch
framework.
The posterior's job is to create ``RandomVariable`` s for approximating distributions.
Whenever we add a ``RandomVariable`` to a ``Module``, the posterior will pick it up
and create an approximating distribution for it.

Thus one need to select the correct posterior to use with a specific inference method.
However most posteriors are designed for variational inference.
"""

from borch.posterior.as_prior import AsPrior
from borch.posterior.automatic import Automatic
from borch.posterior.manual import Manual
from borch.posterior.posterior import Posterior
from borch.posterior.normal import Normal, ScaledNormal
from borch.posterior.pointmass import PointMass
