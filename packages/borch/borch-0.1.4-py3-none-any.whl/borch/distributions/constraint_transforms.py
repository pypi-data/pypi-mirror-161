"""
In may cases `torch.distributions.transform_to` is a better way to go,
however it relies on `weakref` which makes it impossible to pickle any object
that contains that object.
"""
from torch.distributions import constraints, transform_to
import torch


def _identity(x):
    return x


CONSTRAINTS_TRANSFORMS = {
    constraints.real: _identity,
    constraints.positive: torch.exp,
}


def transform(constraint):
    """Get a transform from real --> constraint"""
    if constraint in CONSTRAINTS_TRANSFORMS:
        return CONSTRAINTS_TRANSFORMS[constraint]
    return transform_to(constraint)
