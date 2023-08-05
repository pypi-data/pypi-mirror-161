# pylint: disable=not-callable
"""Utility functions used in the model interface"""

from numbers import Number
from typing import Union

import inspect
from numpy import ndarray
import torch
from torch import Tensor
from torch.nn import Parameter
from torch.distributions import constraints, Distribution
from torch.distributions.constraint_registry import transform_to

import borch.distributions as dist
from borch.distributions.constraint_transforms import transform
from borch.utils.torch_utils import is_numeric
import borch


def requires_grad(tensor) -> bool:
    """Checks if a tensor/number requires gradient.

    Args:
        tensor: Tensor or numeric argument to check for `requires_grad`.

    Returns:
        Whether or not `tensor` had a requires_grad attribute which is set
        to `True`.
    """
    if isinstance(tensor, (Number, ndarray)):
        return False
    if isinstance(tensor, borch.Graph):
        return any(param.requires_grad for param in tensor.parameters())
    if isinstance(tensor, torch.Tensor):
        return tensor.requires_grad

    msg = f"tensor must be valid numeric type, not '{type(tensor).__name__}'"
    raise TypeError(msg)


def as_distribution(rv):
    """Get the distribution from a Random Variable

    If it is not a random varaible the input will just be returned.
    """
    if isinstance(rv, borch.RandomVariable):
        return rv.distribution
    return rv


def as_distributions(*rvs):
    """Get the distribution from a Random Variable

    If it is not a random varaible the input will just be returned.
    """
    return [as_distribution(rv) for rv in rvs]


def _get_constraint(name, distribution):
    distribution = as_distribution(distribution)
    if name in distribution.arg_constraints:
        return distribution.arg_constraints[name]
    if name == "logits":
        return constraints.real
    return None


def _val_to_tp(value, constraint):
    value = borch.as_tensor(value)
    unconstrained = Parameter(transform_to(constraint).inv(value).clone().detach())
    value = borch.Transform(transform(constraint), unconstrained)
    return value


def get_init_kwargs(obj):
    """Get the init arguments of a class as a dict"""
    args = inspect.getfullargspec(obj.__init__).args
    for key in ["self", "posterior"]:
        if key in args:
            args.remove(key)
    kwargs = {}
    for arg in args:
        if not hasattr(obj, arg):
            continue
        kwargs[arg] = getattr(obj, arg)
    return kwargs


def detach_dist(distribution: Distribution) -> Distribution:
    """Takes a `borch.RandomVariable` and creates a new
    `RandomVariable` where the gradient does not proppegate trough the
    arguments of the distribution.

    Args:
      distribution: Diborch stributon to clone where the clone does not
        proppegate the gradient to the arguments.

    Returns:
        A `ppl.distributions.Distribution` whose arguments can
        not be optimized.

    Example:
        >>> normal = dist.Normal(0, 1)
        >>> dist = detach_dist(normal)
    """
    kwargs = get_init_kwargs(distribution)
    for key, val in kwargs.items():
        if is_numeric(val):
            val = borch.as_tensor(val)
            kwargs[key] = val.clone().detach()
        elif isinstance(val, (torch.distributions.Distribution, borch.RandomVariable)):
            kwargs[key] = detach_dist(val)
    return type(distribution)(**kwargs)


def dist_to_qdist(rv):
    """Takes a `torch.distributions.Distribution` and converts it to a new
    distribution whose arguments can be optimised.

    If the args in the distribution are none in the field `_grad_fn` it will
    return a Transform consisting of the same type of transformation
    as its constraints dictates and with the variable being in the
    unconstrained space and detached, else the variable will just be returned.

    Args:
      distribution: torch.distributions.Distribution

    Returns:
        A `ppl.distributions.Distribution` whose arguments can be optimised.
    """
    kwargs = get_init_kwargs(rv)
    for name, value in kwargs.items():
        if is_numeric(value):
            constraint = _get_constraint(name, rv)
            if constraint == constraints.real:
                kwargs[name] = Parameter(borch.as_tensor(value).clone().detach())
            elif constraint is None:
                kwargs[name] = borch.as_tensor(value).clone().detach()
            else:
                kwargs[name] = _val_to_tp(value, constraint)
        elif isinstance(value, (borch.RandomVariable, Distribution)):
            kwargs[name] = dist_to_qdist(value)
    return type(rv)(**kwargs)


def dist_to_qdist_infer_hierarchy(distribution):
    """Takes a `torch.distributions.Distribution` and converts it to a new
    distribution whose arguments can be optimised.

    If the args in the distribution are none in the field `_grad_fn` it will
    return a Transform consisting of the same type of transformation
    as its constraints dictates and with the variable being in the
    unconstrained space and detached, else the variable will just be returned.

    Args:
      distribution: torch.distributions.Distribution

    Returns:
        A `ppl.distributions.Distribution` whose arguments can be optimised.
    """
    kwargs = get_init_kwargs(distribution)
    for name, value in kwargs.items():
        if (
            is_numeric(value)
            and not requires_grad(value)
            and not isinstance(value, Parameter)
        ):
            constraint = _get_constraint(name, distribution)
            if constraint == constraints.real:
                kwargs[name] = Parameter(borch.as_tensor(value).clone().detach())
            elif constraint is None:
                kwargs[name] = borch.as_tensor(value).clone().detach()
            else:
                kwargs[name] = _val_to_tp(value, constraint)
        elif isinstance(value, (borch.RandomVariable, Distribution)):
            kwargs[name] = dist_to_qdist_infer_hierarchy(value)
    return type(distribution)(**kwargs)


def is_continuous(support):
    """Check is a support is continuous"""
    if isinstance(support, (constraints.integer_interval)) or support in (
        constraints.nonnegative_integer,
        constraints.positive_integer,
    ):
        return False
    return True


def _verify_is_continuous(rv):
    if not is_continuous(rv.support):
        raise RuntimeError(f"{rv} is not continuous")


def _dist_mean(distribution):
    try:
        if isinstance(distribution, borch.RandomVariable):
            distribution = distribution.distribution
        mean = distribution.mean.detach()
    except NotImplementedError:
        mean = distribution.sample(sample_shape=torch.Size([1000])).mean(0)
    return mean


def normal_distribution_from_rv(
    rv, log_scale: Union[Tensor, Number], loc_at_mean=True
) -> dist.Normal:
    """Create a Normal distribution with optimisable arguments from an
    existing random variable. The loc of the returned distribution is set
    to the current value of ``rv``.

    Args:
        rv: A `RandomVariable` from which to use the value as the
          loc of the Normal.
        log_scale: Log of the scale for the created normal distribution.

    Returns:
        A new distribution of type :class:`borch.distributions.Normal`.

    Raises:
        TypeError if ``rv`` does not have `real` support.

    Notes:
        When ``rv`` does not have a finite value the underlying distribution
        is sampled to create the mean for the normal distribution.
    """
    _verify_is_continuous(rv)
    if loc_at_mean:
        loc_init = _dist_mean(rv.distribution).detach()
    else:
        loc_init = rv.detach()
    if not torch.isfinite(loc_init).all():
        loc_init = rv.sample()
    scale = Parameter((loc_init * 0 + log_scale).clone().detach())
    scale = borch.Transform(torch.exp, scale)

    if rv.support is constraints.real:
        loc = loc_init.clone().detach()
        return dist.Normal(Parameter(loc), scale)

    loc = Parameter(transform_to(rv.support).inv(loc_init).clone().detach())
    return dist.TransformedDistribution(
        dist.Normal(loc, scale), [transform_to(rv.support)]
    )


def delta_distribution_from_rv(rv):
    """Create a Delta distribution with optimisable argument from an
    existing random variable. The value of the returned distribution is set
    to the current value of :arg:`rv`.

    Args:
        rv: A `RandomVariable` from which to use the value as the
          loc of the Normal.

    Returns:
        A new distribution of type :class:`borch.distributions.Delta`.
    """
    _verify_is_continuous(rv)
    loc_init = rv.tensor
    if not torch.isfinite(loc_init).all():
        loc_init = rv.sample()
    loc_init = loc_init.clone().detach()
    if rv.support is constraints.real:
        return dist.Delta(Parameter(loc_init))
    loc = transform_to(rv.support).inv(loc_init).clone().detach()
    return dist.TransformedDistribution(
        dist.Delta(Parameter(loc)), [transform_to(rv.support)]
    )


def _scale(rv):
    if isinstance(rv, (dist.StudentT, dist.Cauchy)):
        return rv.scale
    try:
        if isinstance(rv, borch.RandomVariable):
            rv = rv.distribution
        scale = rv.stddev
    except NotImplementedError:
        scale = rv.sample(sample_shape=torch.Size([1000])).std()
    return scale


def scaled_normal_dist_from_rv(rv, scaling, loc_at_mean=True):
    """Create a Normal distribution with optimisable arguments from an
    existing random variable. The loc of the returned distribution is set
    to the current value of ``rv``.

    Where the scale in initilized as `rv.stddev*scaling` in the constrained space.

    Args:
        rv: A `RandomVariable` from which to use the value as the
          loc of the Normal.
        scaling: the degree of scaling of the stddev of the prior to use for
            the scale of the created normal distribution.

    Returns:
        A new distribution of type :class:`borch.distributions.Normal`.

    Raises:
        TypeError if ``rv`` does not have `REAL` support.

    Notes:
        When ``rv`` does not have a finite value the underlying distribution
        is sampled to create the mean for the normal distribution.
    """
    _verify_is_continuous(rv)
    if loc_at_mean:
        loc_init = _dist_mean(rv.distribution).detach()
    else:
        loc_init = rv.detach()
    if not torch.isfinite(loc_init).all():
        loc_init = rv.sample()
    scale = Parameter(
        (borch.as_tensor(_scale(rv)) * scaling + loc_init * 0).clone().detach().log()
    )
    scale = borch.Transform(torch.exp, scale)
    if rv.support is constraints.real:
        loc = loc_init.clone().detach()
        return dist.Normal(Parameter(loc), scale)
    loc = Parameter(transform_to(rv.support).inv(loc_init).clone().detach())
    return dist.TransformedDistribution(
        dist.Normal(loc, scale), [transform_to(rv.support)]
    )
