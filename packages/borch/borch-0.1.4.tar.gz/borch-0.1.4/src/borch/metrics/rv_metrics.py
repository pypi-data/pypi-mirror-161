"""
This module supports calculating different metrics for observed random variables.

One can use a specific metric like
    >>> from borch import distributions
    >>> import torch
    >>> rv = distributions.Normal(torch.randn(10), torch.randn(10).exp())
    >>> mse = mean_squared_error(rv)

one can use ``all_metrics`` to get all valid metrics for that random variable.
    >>> all = all_metrics(rv)

"""
from torch.distributions import constraints
from borch.metrics import metrics
from borch.module import Module

METRICS = {
    constraints.real.__class__: (
        metrics.mean_squared_error,
        metrics.r2_score,
    ),
    constraints.greater_than: (
        metrics.mean_squared_error,
        metrics.r2_score,
    ),
    constraints.real_vector.__class__: (
        metrics.mean_squared_error,
        metrics.r2_score,
    ),
    constraints.greater_than_eq: (
        metrics.mean_squared_error,
        metrics.r2_score,
    ),
    constraints.less_than: (
        metrics.mean_squared_error,
        metrics.r2_score,
    ),
    constraints.integer_interval: (metrics.accuracy,),
    constraints.positive_integer.__class__: (metrics.accuracy,),
    constraints.unit_interval.__class__: (metrics.mean_squared_error,),
}


def suggest_metric_fns(rv):
    """Suggest metric functions to use for an RV"""
    return METRICS.get(type(rv.support), [])


def calculate_metric(fn, rv):
    """Calculate metrics

    Calculate a metric for an observed RV

    Args:
        fn: callable that takes two arguments equivalent to `pred`, `target`
        rv: a random variable
    """
    return fn(rv.distribution.sample(), rv.tensor)


def module_metrics(mod, metrics_fns=None):
    """
    Get the metrics of all observed RV`s in the module

    Note:
        Does only give for RVs directly attached to the module
        not submodules.
    """
    if not isinstance(mod, Module):
        return {}
    return {
        key: all_metrics(getattr(mod.posterior, key), metrics_fns=metrics_fns)
        for key in dict(mod.observed.items())
    }


def all_metrics(rv, metrics_fns=None):
    """
    Calculates all valid performance metrics of an observed RandomVariable,
        rv (borch.RandomVariable): an observed `RandomVariable`.
        metrics_fns (optional, callable, List[callable])]: list of metrics
            functions to calculate, or a callable that takes a rv as argument
            and returns a list of callable

    Returns:
        dict, with performance measures

    Notes:
        If no performance measures is defined for the support of the distribution,
        an empty dict will be returned.

    Examples:
        >>> import torch
        >>> from borch import distributions
        >>> rv = distributions.Normal(0, 1)
        >>> met = all_metrics(rv)

    """
    if metrics_fns is None:
        metrics_fns = suggest_metric_fns
    if callable(metrics_fns):
        metrics_fns = metrics_fns(rv)
    return {met.__name__: calculate_metric(met, rv) for met in metrics_fns}


def mean_squared_error(rv):
    """
    Measures the averaged element-wise mean squared error of an observed RandomVariable
    Args:
        rv(borch.RandomVariable): an observed `RandomVariable`.

    Returns:
        tensor, with the mean squared error
    Examples:
        >>> from borch import RandomVariable, distributions
        >>> import torch
        >>> rv = distributions.Normal(torch.randn(10), torch.randn(10).exp())
        >>> mse = mean_squared_error(rv)
    """
    return calculate_metric(metrics.mean_squared_error, rv)


def accuracy(rv):
    """
    Calculates the accuracy, i.e. how much agreement between two long tensors. It will
    return values between 0 and 1.
    Args:
        rv(borch.RandomVariable): an observed `RandomVariable`.

    Returns:
        tensor, with the calculated accuracy

    Examples:
        >>> from borch import RandomVariable, distributions
        >>> import torch
        >>> rv = distributions.Categorical(logits=torch.randn(4))
        >>> acc = accuracy(rv)

    Notes:
        This function does not support gradient trough it
    """
    return calculate_metric(metrics.accuracy, rv)
