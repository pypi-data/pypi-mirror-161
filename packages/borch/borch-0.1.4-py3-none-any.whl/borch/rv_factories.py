# pylint: disable=no-member
"""
Random Variable Factories
=========================

Exposes some common functions for replacing parameters with ``RandomVariable``
objects for use in Bayesian neural networks.
"""

from numbers import Number
from typing import Callable, Optional, Union, Dict

import numpy as np
import torch
from torch import Tensor
from torch.nn import Module

from borch.random_variable import RandomVariable
from borch import distributions
from borch.distributions.distribution_utils import get_init_kwargs
from borch.utils.init import kaiming_normal_std, xavier_normal_std
from borch.utils.torch_utils import is_numeric


def priors_to_rv(
    name: str, parameter: Tensor, priors: Dict, fallback_rv_factory: Callable
):
    """Turn a ``torch.Parameter`` into a ``RandomVariable`` prior given a set of
    provided priors, of no prior excsts a fallback rv_factory will be used.

    Args:
        name: The name of the parameter as it appears in the the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter: Parameter to create a random variable for.
        priors: dctionary with prior distributions to use, a new distribution
          wil be creaated where the arguments are broadcasted to the shape of
          the paramater.
        fallback_rv_factory: the backup rv factoy to use if no pririor for that
          name is provided.

    Returns:
        A ``RandomVariable`` object which should replace the given parameter in
        Bayesian neural network.

    Examples:
        >>> from borch import distributions as dist
        >>> import torch
        >>> param = torch.ones(3, 3, requires_grad=True)
        >>> random_var = priors_to_rv("param",
        ...                                     param,
        ...                                     {'param': dist.Normal(0., 100.)},
        ...                                     parameter_to_normal_rv)
        >>> type(random_var)
        <class '...Normal'>
        >>> float(random_var.distribution.scale.mean())
        100.0
    """
    if name not in priors:
        if fallback_rv_factory is None:
            return parameter
        return fallback_rv_factory(name, parameter)
    kwargs = get_init_kwargs(priors[name])
    for key, val in kwargs.items():
        if isinstance(val, Tensor):
            val = val.to(parameter.device)
        if is_numeric(val):
            val = val + parameter.clone().detach().zero_()
        kwargs[key] = val
    distribution = type(priors[name])(**kwargs)
    if distribution.tensor.shape != parameter.shape:
        raise RuntimeError(
            f"""Brodacsting of the arguments of the prior distribution failed,
            the resulting shape of a sample from the distibution{distribution.shape}
            does not match the paramater shape {parameter.shape}"""
        )
    return distribution


def apply_rv_factory(
    module: Module, rv_factory: Optional[Callable[[str, Tensor], RandomVariable]] = None
) -> Module:
    """Apply an rv factory callable to all parameters in a Module.

    Args:
        module: The module which will have all its parameters piped through
          the ``rv_factory`` callable.
        rv_factory: A callable which

    Returns:
        A ``Module`` which has had all ``Parameters`` in ``_parameters`` replaced
        with ``RandomVariable`` objects according to ``rv_factories`` (if
        ``rv_factories`` was not ``None``, otherwise they are unchanged).
    """
    # pylint: disable=protected-access

    params = module._parameters
    if rv_factory is not None:
        for name in tuple(params):
            if params[name] is None:
                continue
            setattr(module, name, rv_factory(name, params.pop(name)))
    return module


def parameter_to_normal_rv(
    name: str,
    parameter: Tensor,
    prior_mean: Union[Tensor, Number] = 0.0,
    prior_sd: Union[Tensor, Number] = 1.0,
) -> RandomVariable:
    """Turn a ``torch.Parameter`` into a ``RandomVariable`` prior given values for
    mean and sd.

    Args:
        name: The name of the parameter as it appears in the the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter: Parameter to create a random variable for.
        prior_mean: Value for the mean of the prior.
        prior_sd: Value for the sd of the prior.

    Returns:
        A ``RandomVariable`` object which should replace the given parameter in
        Bayesian neural network.

    Notes:
        We set the data of the returned rv to be the current value of
        ``parameter``. This means that the current initialisation value for
        the parameter can be used by any posterior for initialisation purposes.

    Examples:
        >>> import torch
        >>> param = torch.ones(3, 3, requires_grad=True)
        >>> random_var = parameter_to_normal_rv("param", param)
        >>> type(random_var)
        <class '...Normal'>
        >>> random_var.distribution.loc  # this is the prior of the RV
        tensor([[0., 0., 0.],
                [0., 0., 0.],
                [0., 0., 0.]])

    """
    # pylint: disable=not-callable,unused-argument
    if isinstance(prior_mean, Number):
        prior_mean = (parameter * 0 + prior_mean).clone().detach()
    if isinstance(prior_sd, Number):
        prior_sd = (parameter * 0 + prior_sd).clone().detach()
    p_dist = distributions.Normal(prior_mean, prior_sd)
    p_dist.tensor.data = parameter.data
    return p_dist


# pylint: disable=unused-argument
def parameter_to_maxwidth_uniform(name: str, parameter: Tensor) -> RandomVariable:
    """
    Create an infinitely wide uniform distribution from a variable. The initial value of
    the RV will be the value of the parameter so we don't have a sample from -inf to inf

    Args:
        name: The name of the parameter as it appears in the the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter: The parameter that will decide the shape and initial value of the
          rv

    Returns: infinitely wide uniform RandomVariable

    """
    dtype = torch.ones(1, dtype=parameter.dtype).numpy().dtype
    min_val = np.finfo(dtype).min / 2
    max_val = np.finfo(dtype).max / 2
    p_dist = distributions.Uniform(
        min_val + 0 * parameter.clone().detach(),
        max_val + 0 * parameter.clone().detach(),
    )

    p_dist.tensor.data = parameter.data
    return p_dist


def parameter_to_scaled_normal_rv(name, parameter, std_fn=lambda x: 1.0, std_scale=1):
    """Turn a ``torch.Parameter`` into a ``RandomVariable``

    Args:
        name (str): The name of the parameter as it appears in the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter (torch.tensor): Parameter to create a random variable for.
        std_fn (callable): callable that takes a tuple with ints as input,
          where the ints represent the shape of the parameter, should return a
          float
        std_scale (float): scale that gets multiplied to the output of std_fn

    Returns:
        A ``RandomVariable`` object which should replace the given parameter in
        Bayesian neural network.

    Notes:
        We set the data of the returned rv to be the current value of
        ``parameter``. This means that the current initialisation value for
        the parameter can be used by any posterior for initialisation purposes.

    Examples:
        >>> import torch
        >>> param = torch.ones(3, requires_grad=True)
        >>> random_var = parameter_to_scaled_normal_rv("param", param)
        >>> type(random_var)
        <class '...Normal'>
        >>> random_var.distribution.loc  # this is the prior of the RV
        tensor([0., 0., 0.])
        >>> random_var.scale
        tensor([1., 1., 1.])
    """
    # pylint: disable=not-callable,unused-argument
    prior_mean = (parameter * 0).clone().detach()

    sd = std_fn(parameter.shape)
    prior_sd = std_scale * (parameter * 0 + sd).clone().detach()
    p_dist = distributions.Normal(prior_mean, prior_sd)
    p_dist.tensor.data = parameter.data
    return p_dist


def kaiming_normal_rv(name, parameter):
    """Turn a ``torch.Parameter`` into a ``RandomVariable``
    Where the RV will have a normal distribution with a mean of zero and
    the sd calculated according to the kaiming initialization scheme.

    Args:
        name (str): The name of the parameter as it appears in the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter (torch.tensor): Parameter to create a random variable for.

    Returns:
        A ``RandomVariable`` object which should replace the given parameter in
        Bayesian neural network.

    Notes:
        We set the data of the returned rv to be the current value of
        ``parameter``. This means that the current initialisation value for
        the parameter can be used by any posterior for initialisation purposes.

    Examples:
        >>> import torch
        >>> param = torch.ones(3, requires_grad=True)
        >>> random_var = kaiming_normal_rv("param", param)
        >>> type(random_var)
        <class '...Normal'>
        >>> random_var.distribution.loc  # this is the prior of the RV
        tensor([0., 0., 0.])
        >>> random_var.scale
        tensor([0.5774, 0.5774, 0.5774])
    """
    return parameter_to_scaled_normal_rv(name, parameter, kaiming_normal_std)


def xavier_normal_rv(name, parameter):
    """Turn a ``torch.Parameter`` into a ``RandomVariable``
    Where the RV will have a normal distribution with a mean of zero and
    the sd calculated according to the kaiming initialization scheme.

    Args:
        name (str): The name of the parameter as it appears in the the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter (torch.tensor): Parameter to create a random variable for.

    Returns:
        A ``RandomVariable`` object which should replace the given parameter in
        Bayesian neural network.

    Notes:
        We set the data of the returned rv to be the current value of
        ``parameter``. This means that the current initialisation value for
        the parameter can be used by any posterior for initialisation purposes.

    Examples:
        >>> import torch
        >>> param = torch.ones(3, requires_grad=True)
        >>> random_var = xavier_normal_rv("param", param)
        >>> type(random_var)
        <class '...Normal'>
        >>> random_var.loc  # this is the prior of the RV
        tensor([0., 0., 0.])
        >>> random_var.scale
        tensor([0.7071, 0.7071, 0.7071])
    """

    return parameter_to_scaled_normal_rv(name, parameter, xavier_normal_std)


def delta_rv(name, parameter):  # pylint: disable=unused-argument
    """Turn a ``torch.Parameter`` into a ``RandomVariable``
    Where the RV will have a delta distribution with a mean around the parameter value

    Args:
        name (str): The name of the parameter as it appears in the the
          ``Module._parameters`` dictionary. This can be used to perform
          different actions depending on what parameter was given.
        parameter (torch.tensor): Parameter to create a random variable for.

    Returns:
        A ``RandomVariable`` object which should replace the given parameter in
        Bayesian neural network.

    Notes:
        We set the data of the returned rv to be the current value of
        ``parameter``. This means that the current initialisation value for
        the parameter can be used by any posterior for initialisation purposes.

    Examples:
        >>> import torch
        >>> param = torch.ones(3, requires_grad=True)
        >>> random_var = delta_rv("param", param)
        >>> type(random_var)
        <class '...Delta'>
        >>> random_var.sample() # this is the prior of the RV
        tensor([1., 1., 1.])
    """

    return distributions.Delta(parameter)
