# pylint: disable=abstract-method,undefined-all-variable
"""
Distributions that are not available in torch.distributions
"""
import torch
from torch import distributions
from torch.distributions import constraints
from torch.distributions.constraint_registry import transform_to

from borch.graph import as_tensor


class Delta(distributions.Distribution):
    """Implements a Delta distribution

    Example:
        >>> dist = Delta(0)
        >>> float(dist.sample())
        0.0
    """

    # pylint: disable=not-callable
    has_rsample = True
    support = constraints.real
    arg_constraints = {"value": constraints.real}

    def __init__(self, value, event_shape=torch.Size(), validate_args=None):
        self.value = as_tensor(value)
        super().__init__(self.value.size(), event_shape, validate_args=validate_args)

    @property
    def mean(self):
        return self.rsample()

    @property
    def variance(self):
        return torch.zeros_like(self.rsample())

    def rsample(self, sample_shape=torch.Size()):
        """Returns transformed value according to the support.

        Returns:
            The current constrained value, expanded to the shape of
            `sample_shape`.
        """
        shape = self._extended_shape(sample_shape)
        return self.value.expand(shape)

    def sample(self, sample_shape=torch.Size()):
        with torch.no_grad():
            return self.rsample(sample_shape).detach()

    def log_prob(self, value):
        return (value == self.value).to(value.dtype).to(value.device).log()


class PointMass(distributions.TransformedDistribution):
    """Implements a PointMass distribution, it takes an unconstrained value
    and constrains it according to the provided support.
    """

    # pylint: disable=not-callable
    has_rsample = True

    arg_constraints = {"value": constraints.real}

    def __init__(self, value, support, event_shape=torch.Size(), validate_args=None):
        base_dist = Delta(
            as_tensor(value), event_shape=event_shape, validate_args=validate_args
        )
        super(PointMass, self).__init__(
            base_dist, transform_to(support), validate_args=validate_args
        )

    @property
    def value(self):
        """Get the value of the base distribution"""
        return self.base_dist.value
