# pylint: disable=invalid-name
"""
Implementation of Hamiltonian Monte Carlo algorithm (HMC), which is a
Markov chain Monte Carlo method.


Note that the HMC implementations have not gone trough rigorous use and
is considered experimental.

Examples:
    >>> import torch
    >>> from borch.infer.nuts import find_reasonable_epsilon,dual_averaging
    >>> parameters = [torch.ones(1, requires_grad=True) for ii in range(3)]

    >>> def closure():
    ...     return -sum([-(pp).pow(2).sum() for pp in parameters])

    >>> param_value =[]
    >>> inital_epsilon, epsilon_bar, h_bar =  find_reasonable_epsilon(
    ...                                         parameters, closure)
    >>> epsilon = inital_epsilon
    >>> for i in range(1, 10):
    ...     accept_prob = hmc_step(.1, 10, parameters, closure)
    ...     if i < 5:
    ...         epsilon, epsilon_bar, h_bar = dual_averaging(accept_prob, i,
    ...                                                 inital_epsilon,
    ...                                                 epsilon_bar, h_bar)
    ...     else:
    ...         epsilon = epsilon_bar
    ...     param_value.append([par.detach().clone() for par in parameters])
"""
from numbers import Number
import torch
import numpy as np

from borch.utils.torch_utils import detach_copy_tensors, update_tensor_data


def _negative_closure(closure):
    """Convert the closure to be negative in order to operate
    on the likelihood hood instead of the negative log likelihood
    """

    def _negative_closure():
        """make closure negative"""
        return -closure()

    return _negative_closure


def _grad(closure, params):
    grad = torch.autograd.grad(
        closure(), params, create_graph=False, allow_unused=True, retain_graph=True
    )
    return _none_to_zero(grad)


def _none_to_zero(iterable):
    return type(iterable)(var if var is not None else 0 for var in iterable)


def leapfrog(theta, r, epsilon, params, closure):
    """The leapfrog function from the paper "The No-U-Turn Sampler: Adaptively Setting
    Path Lengths in Hamiltonian Monte Carlo".

    Args:
        theta: list with torch.tensor's, the current values of the parameters where
            they are evaluated
        r: list with torch.tensor's
        epsilon: float, the step size
        params: list with torch.tensor's, the tensors that thr derivative of the
            closure is taken with respect to.
        closure: python callable with no arguments. Should do the log_prob calculations

    Returns:
        the new theta_tilde, r_tilde

    """
    update_tensor_data(params, theta)
    r_tilde = [
        r_temp + epsilon * 0.5 * gradL
        for r_temp, gradL in zip(r, _grad(closure, params))
    ]
    theta_tilde = [
        theta_temp + epsilon * r_temp for theta_temp, r_temp in zip(theta, r_tilde)
    ]
    update_tensor_data(params, theta_tilde)
    r_tilde = [
        r_temp + epsilon * 0.5 * gradL
        for r_temp, gradL in zip(r_tilde, _grad(closure, params))
    ]
    return theta_tilde, r_tilde


def _log_energy(theta, r, parameters, closure):
    update_tensor_data(parameters, theta)
    potential_energy = closure()
    kinetric_energy = -0.5 * sum(nn.pow(2).sum() for nn in r)
    return potential_energy + kinetric_energy


def _all_nan_tensor_to_zero(val):
    """Tensors with all values in nan to zero"""
    if isinstance(val, Number) and np.isnan(val):
        return 0
    if isinstance(val, torch.Tensor) and torch.isnan(val).all():
        return torch.zeros_like(val)
    return val


def hmc_step(epsilon, L, parameters, closure):
    """
    Performs one Hamiltonian Monte carlo step, the `.data` of the parameters
    will be updated with the result of the step.

    Notes:
        For some random number generation numpy is used, this means
        that in order to make seeded runs both torch and numpy needs to
        be seeded.

        hmc_step needs to be given the negative log likelihood and not the
        log likelihood as outlined in the paper. This is done to be consistent
        with the optimizer interface.

        The HMC implementations have not gone trough rigorous use and
        is considered experimental.

    Args:
        epsilon (float): float, the step size
        L (int): int, the number of leapfrog steps
        parameters (iterable):  with torch.tensors. The parameters to use in the
            hmc step
        closure (callable): A closure that reevaluates the model and returns the loss.

    Returns:
        float, The acceptance probability of the step.

    Example:
        >>> import torch
        >>> import numpy
        >>> torch.manual_seed(7)
        <...>
        >>> numpy.random.seed(7)
        >>> parameters = [torch.ones(1, requires_grad=True) for ii in range(3)]
        >>> def closure():
        ...     return -sum([-(pp).pow(2).sum() for pp in parameters])
        >>> hmc_step(.1, 10, parameters, closure)
        1.0

    """
    parameters = list(parameters)
    negative_closure = _negative_closure(closure)
    theta = detach_copy_tensors(parameters)
    r0 = [torch.zeros_like(rvar).normal_() for rvar in theta]
    r_tilde = detach_copy_tensors(r0)
    theta_tilde = detach_copy_tensors(theta)

    for _ in range(L):
        theta_tilde, r_tilde = leapfrog(
            theta_tilde, r_tilde, epsilon, parameters, negative_closure
        )

    log_energy_current = _log_energy(theta, r0, parameters, negative_closure)
    log_energy_proposal = _log_energy(
        theta_tilde, r_tilde, parameters, negative_closure
    )
    alpha = log_energy_proposal - log_energy_current

    accept_prob = _all_nan_tensor_to_zero(alpha.exp()).clamp(max=1).item()

    if torch.rand(1) < accept_prob:
        theta = theta_tilde
    update_tensor_data(parameters, theta)

    return accept_prob
