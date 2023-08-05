# pylint: disable=unused-argument
"""Functional interface to log_joint calculations

Functionality to calculate the `log_prob` of several distributions.
If one feeds in only observed values to the ``values`` argument of the function
one operates in the classic maximum likelihood paradigm. If one on the other hand
also includes unobserved values one calculates what is known as maximum a
posteriori(MAP)

Examples:
    >>> import borch.distributions as dist
    >>> import torch
    >>> params = [torch.ones(1, requires_grad=True) for i in range(5)]
    >>> p_dists = [dist.Cauchy(2,2) for _ in range(5)] + [dist.Normal(
    ...     2,2) for _ in range(5)]
    >>> values = [torch.tensor(float(ii)) for ii in range(1,6)] + params
    >>> opt = torch.optim.Adam(params)
    >>> for _ in range(5):
    ...     opt.zero_grad()
    ...     loss = negative_log_prob(p_dists, values)
    ...     loss.backward()
    ...     opt.step()

"""
from torch.distributions.constraint_registry import biject_to, transform_to


def volume_adjustment(p_dist, value):
    """Adjustment term to the logJoint when preforming space transformations

    Args:
      p_dist: torch.distributions.Distribution, the prior
      value: torch.tensor, the point where it is evaluated

    Returns:
      torch.tensor

    Example:
        >>> import torch
        >>> import borch.distributions as dist
        >>> volume_adjustment(dist.Gamma(1,1), torch.ones(1))
        tensor([0.])


    """
    support = p_dist.support
    return biject_to(support).log_abs_det_jacobian(
        transform_to(support).inv(value), value
    )


def log_prob_volume_adjustment(p_dists, values, **kwargs):
    """Adjustment term to the log prob when preforming space transformations.

    Args:
      values: list with torch.tensor where the log_prob volume adjustments is evaluated
      p_dists: list with torch.distributions.Distribution

    Returns:
      torch.tensor

    Examples:
        >>> import borch.distributions as dist
        >>> import torch
        >>> p_dists = [dist.Gamma(2,2) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(1,6)]
        >>> log_prob_volume_adjustment(p_dists, values)
        tensor(4.7875)

    """
    return sum(
        volume_adjustment(p_dist, val).sum() for p_dist, val in zip(p_dists, values)
    )


def log_prob_loss(p_dist, value):
    """
    Returns the log_prob of the p_dist evaluated at value

    .. math::
        log dist(value | **)

    Args:
        p_dist:  a ``torch.distributions.Distribution``
        value: torch.tensor

    Returns:
        torch.tensor

    Example:
        >>> import torch
        >>> import borch.distributions as dist
        >>> log_prob_loss(
        ...     dist.Normal(loc = torch.ones(1), scale = torch.ones(1)),
        ...     torch.zeros(1))
        tensor(-1.4189)
    """
    return p_dist.log_prob(value).sum()


def negative_log_prob_loss(p_dist, value):
    """
    Returns the negative log_prob of the p_dist evaluated at value

    .. math::
        -log dist(value | **)

    Args:
        P_dist:  a ``torch.distributions.Distribution``
        value: torch.tensor

    Returns:
        torch.tensor

    Example:
        >>> import torch
        >>> import borch.distributions as dist
        >>> negative_log_prob_loss(
        ...     dist.Normal(loc = torch.ones(1), scale = torch.ones(1)),
        ...     torch.zeros(1))
        tensor(1.4189)
    """
    return -log_prob_loss(p_dist, value)


def negative_log_prob(p_dists, values, **kwargs):
    """Calculates the negative log_prob the provided distributions at supplied
     values.

    Args:
        p_dists: list with torch.distributions.Distribution
        values: list with torch.tensor where the log_prob volume adjustments
            is evaluated.

    Returns:
        torch.tensor

    Examples:
        >>> import borch.distributions as dist
        >>> import torch
        >>> p_dists = [dist.Cauchy(2,2) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(1,6)]
        >>> negative_log_prob(p_dists, values)
        tensor(11.5075)

    """
    return -log_prob(p_dists, values, **kwargs)


def log_prob(p_dists, values, **kwargs):
    """Calculates the log_prob the provided distributions at supplied values.

    Args:
        p_dists: list with torch.distributions.Distribution
        values: list with torch.tensor where the log_prob volume adjustments
            is evaluated.

    Returns:
        torch.tensor

    Examples:
        >>> import borch.distributions as dist
        >>> import torch
        >>> p_dists = [dist.Cauchy(2,2) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(1,6)]
        >>> log_prob(p_dists, values)
        tensor(-11.5075)

    """
    return sum(log_prob_loss(p_dist, value) for p_dist, value in zip(p_dists, values))
