# flake8: noqa
# pylint: skip-file
# the code is close to the algorithm in the paper in favor of agreeing with lint
"""
The No-U-Turn Sampler (NUTS), an extension to Hamiltonian Monte Carlo that
eliminates the need to set a number of steps leapfrog steps. Empirically,
NUTS perform at least as efficiently as and sometimes more efficiently than a
well tuned standard HMC method, without requiring user intervention.

Note that the NUTS implementations have not gone trough rigorous use and
is considered experimental.

Examples:
    >>> import torch
    >>> parameters = [torch.ones(1, requires_grad=True) for ii in range(3)]

    >>> def closure():
    ...     return -sum([-(pp).pow(2).sum() for pp in parameters])

    >>> param_value =[]
    >>> inital_epsilon, epsilon_bar, h_bar =  find_reasonable_epsilon(
    ...                                         parameters, closure)
    >>> epsilon = inital_epsilon
    >>> for i in range(1, 10):
    ...     accept_prob = nuts_step(.1, parameters, closure)
    ...     if i < 5:
    ...         epsilon, epsilon_bar, h_bar = dual_averaging(accept_prob, i,
    ...                                                 inital_epsilon,
    ...                                                 epsilon_bar, h_bar)
    ...     else:
    ...         epsilon = epsilon_bar
    ...     param_value.append([par.detach().clone() for par in parameters])
"""
import math

import numpy as np
import torch

from borch.infer.hmc import (
    _log_energy,
    _negative_closure,
    detach_copy_tensors,
    leapfrog,
    _all_nan_tensor_to_zero,
)
from borch.utils.torch_utils import update_tensor_data


def find_reasonable_epsilon(parameters, closure):
    """
    Implements a Heuristic for choosing an initial value of epsilon for
    HMC and NUTS.

    It implements algorithm 4 in :cite:`Hoffman2011`.
    .. bibliography:: references.bib

    Args:
        parameters: list, with torch.tensors. The parameters to use in the hmc step
        closure: python callable, that takes no arguments. Usually the calculation
            of the log joint of the model

    Returns:
        float, epsilon: the suggested epsilon
        float, epsilon_bar: the initial value of epsilon_bar for dual_averaging
        float, h_bar: the initial value of h_bar for dual_averaging

    Examples:
        >>> import torch
        >>> torch.manual_seed(7)
        <...>
        >>> parameters = [torch.ones(1, requires_grad=True) for ii in range(3)]
        >>> def closure():
        ...     return sum([-(pp).pow(2).sum() for pp in parameters])
        >>> epsilon, epsilon_bar, h_bar = find_reasonable_epsilon(parameters, closure)
        >>> epsilon
        0.5
    """
    parameters = list(parameters)
    negative_closure = _negative_closure(closure)
    epsilon = 1
    r0 = [torch.zeros_like(var).normal_() for var in parameters]
    theta = detach_copy_tensors(parameters)

    log_energy_current = _log_energy(theta, r0, parameters, negative_closure)

    theta_prime, r_prime = leapfrog(theta, r0, epsilon, parameters, negative_closure)
    log_energy_proposal = _log_energy(
        theta_prime, r_prime, parameters, negative_closure
    )

    # Hack to get sane init value of epsilon
    accept_prob = (
        _all_nan_tensor_to_zero((log_energy_proposal - log_energy_current).exp())
        .clamp(max=1)
        .item()
    )
    while (
        not torch.isfinite(log_energy_proposal.detach())
        or not any([torch.isfinite(r.sum()).all() for r in r_prime])
        or accept_prob <= 0
    ):
        epsilon *= 0.5
        theta_prime, r_prime = leapfrog(
            theta, r0, epsilon, parameters, negative_closure
        )
        log_energy_proposal = _log_energy(
            theta_prime, r_prime, parameters, negative_closure
        )

        accept_prob = (
            _all_nan_tensor_to_zero((log_energy_proposal - log_energy_current).exp())
            .clamp(max=1)
            .item()
        )
    a = 2.0 * float((accept_prob > 0.5)) - 1.0
    while (accept_prob**a) > (2 ** (-a)):
        epsilon = epsilon * (2.0**a)
        theta_prime, r_prime = leapfrog(
            theta, r0, epsilon, parameters, negative_closure
        )
        log_energy_proposal = _log_energy(
            theta_prime, r_prime, parameters, negative_closure
        )
        accept_prob = (
            _all_nan_tensor_to_zero((log_energy_proposal - log_energy_current).exp())
            .clamp(min=1e-6, max=1)
            .item()
        )

    # init values from Algorithm 6 in `Hoffman2011`
    epsilon_bar = 1.0
    h_bar = 0.0

    return epsilon, epsilon_bar, h_bar


def dual_averaging(
    accept_prob,
    m,
    initial_epsilon,
    epsilon_bar,
    h_bar,
    delta=0.8,
    gamma=0.05,
    t0=10,
    kappa=0.75,
):
    """
    Dual Averaging is a scheme to sole optimization problems, this
    implemenation is addapted to be used with nuts_step and hmc_step.

    It implements the Dual algorithm parts that is outlined in algorithm 6
    in :cite:`Hoffman2011`.
    .. bibliography:: references.bib


    Args:
        accept_prob (float): the acceptance probability of the MCMC step
        m (int): what dual averaging step this is
        initial_epsilon (float): the the epsilon the scheme is initialized with.
        epsilon_bar (float): the epsilon_bar from the previous step, usualy init to 1.
        h_bar (float): parameter in the scheme to do the updating, good initial
            value is 0.
        delta (float, default .8): parameter that specifies the desired accept_prob
        gamma (float, default 0.05):
        t0 (float, default 10): parameter that stabilizes the initial steps of the scheme.
        kappa (float, default .75): parameter that controls the weights of steps of the scheme.

    Returns:
        a tuple with the new epsilon, epsilon_bar, h_bar
    """
    mu = math.log(10 * initial_epsilon)
    eta = 1.0 / float(m + t0)
    h_bar = (1.0 - eta) * h_bar + eta * (delta - accept_prob)
    epsilon = math.exp(mu - math.sqrt(m) / gamma * h_bar)
    eta = m**-kappa
    epsilon_bar = math.exp(
        (1.0 - eta) * math.log(epsilon_bar) + eta * math.log(epsilon)
    )
    return epsilon, epsilon_bar, h_bar


def _stop_criterion(theta_plus, theta_minus, r):
    """
    A stopping criteria used in nuts
    """
    theta_diff = [t_plus - t_minus for t_plus, t_minus in zip(theta_plus, theta_minus)]
    dot_prod = sum((t_diff * r_temp).sum() for t_diff, r_temp in zip(theta_diff, r))
    return dot_prod >= 0


def _is_turning(theta_minus, r_minus, theta_plus, r_plus):
    diff_plus = 0
    diff_minus = 0
    for t_m, r_m, t_p, r_p in zip(theta_minus, r_minus, theta_plus, r_plus):
        dz = t_m - t_p
        diff_minus += (dz * r_m).sum()
        diff_plus += (dz * r_p).sum()
    return diff_minus < 0 or diff_plus < 0


def _build_tree(
    theta,
    r,
    log_u,
    v,
    j,
    epsilon,
    log_energy_current,
    parameters,
    closure,
    delta_energy_max,
):  # pragma: no cover
    """
    Builds the tree structure in nuts
    """
    if j == 0:
        theta_prime, r_prime = leapfrog(theta, r, v * epsilon, parameters, closure)
        log_energy_proposal = _log_energy(theta_prime, r_prime, parameters, closure)

        alpha = log_energy_proposal - log_energy_current
        accept_prob = float(_all_nan_tensor_to_zero(alpha.exp()))
        alpha_prime = min(1.0, accept_prob)

        n_prime = float(log_u <= log_energy_proposal)
        s_prime = float(log_u < delta_energy_max + log_energy_proposal)
        return (
            theta_prime,
            r_prime,
            theta_prime,
            r_prime,
            theta_prime,
            n_prime,
            s_prime,
            alpha_prime,
            1.0,
        )
    else:
        (
            theta_minus,
            r_minus,
            theta_plus,
            r_plus,
            theta_prime,
            n_prime,
            s_prime,
            alpha_prime,
            n_alpha_prime,
        ) = _build_tree(
            theta,
            r,
            log_u,
            v,
            j - 1,
            epsilon,
            log_energy_current,
            parameters,
            closure,
            delta_energy_max,
        )

        if s_prime == 1:
            if v == -1:
                (
                    theta_minus,
                    r_minus,
                    _,
                    _,
                    theta_2prime,
                    n_2prime,
                    s_2prime,
                    alpha_2prime,
                    n_alpha_2prime,
                ) = _build_tree(
                    theta_minus,
                    r_minus,
                    log_u,
                    v,
                    j - 1,
                    epsilon,
                    log_energy_current,
                    parameters,
                    closure,
                    delta_energy_max,
                )
            else:
                (
                    _,
                    _,
                    theta_plus,
                    r_plus,
                    theta_2prime,
                    n_2prime,
                    s_2prime,
                    alpha_2prime,
                    n_alpha_2prime,
                ) = _build_tree(
                    theta_plus,
                    r_plus,
                    log_u,
                    v,
                    j - 1,
                    epsilon,
                    log_energy_current,
                    parameters,
                    closure,
                    delta_energy_max,
                )

            if np.random.uniform() < (
                float(n_2prime) / max(float(int(n_prime) + int(n_2prime)), 1.0)
            ):
                theta_prime = theta_2prime

            alpha_prime = alpha_prime + alpha_2prime
            n_alpha_prime = n_alpha_prime + n_alpha_2prime
            n_prime = n_prime + n_2prime

            s_prime = (
                s_2prime
                * _stop_criterion(theta_plus, theta_minus, r_minus)
                * _stop_criterion(theta_plus, theta_minus, r_plus)
            )
        return (
            theta_minus,
            r_minus,
            theta_plus,
            r_plus,
            theta_prime,
            n_prime,
            s_prime,
            alpha_prime,
            n_alpha_prime,
        )


def nuts_step(
    epsilon, parameters, closure, max_tree_depth=10, delta_energy_max=1000
):  # pragma: no cover
    """
    Performers one step using the 'The No-U-Turn Sampler'. The No-U-Turn Sampler
    adaptively sets the path lengths in Hamiltonian Monte Carlo, typically
    resulting in lower auto correlation between the samples.

    It implements algorithm 3 in :cite:`Hoffman2011`.
    .. bibliography:: references.bib

    Notes:
        For some random number generation numpy is used, this means
        that in order to make seeded runs both torch and numpy needs to
        be seeded.

        Nuts_step needs to be given the negative log likelihood and not the
        log likelihood as outlined in the paper. This is done to be consistent
        with the optimizer interface.

        The NUTS implementations have not gone trough rigorous use and
        is considered experimental.

    Args:
        epsilon (float): the step size
        parameters: (iterable): list with torch.tensor's
        closure (callable): A closure that reevaluates the model
                and returns the loss.
        max_tree_depth (int): The maximum allowed tree depth.
        delta_energy_max (float): larges allowed energy change.

    Returns:
        a float, the acceptance probability of the step

    Example:
        >>> import torch
        >>> import numpy
        >>> torch.manual_seed(7)
        <...>
        >>> numpy.random.seed(7)
        >>> parameters = [torch.ones(1, requires_grad=True) for ii in range(3)]
        >>> def closure():
        ...     return -sum([-(pp).pow(2).sum() for pp in parameters])
        >>> nuts_step(.1, parameters, closure)
        1.0

    """
    parameters = list(parameters)
    negative_closure = _negative_closure(closure)
    r0 = [torch.zeros_like(var).normal_() for var in parameters]
    r_plus = detach_copy_tensors(r0)
    r_minus = detach_copy_tensors(r0)

    theta = detach_copy_tensors(parameters)
    theta_minus = detach_copy_tensors(theta)
    theta_plus = detach_copy_tensors(theta)

    n, s, j = 1, 1, 0

    log_energy_current = _log_energy(theta, r0, parameters, negative_closure).item()
    log_u = float(log_energy_current - np.random.exponential(1, size=1))
    tree_count = 0
    while s == 1:
        v = int(2 * (np.random.uniform() < 0.5) - 1)
        if v == -1:
            (
                theta_minus,
                r_minus,
                _,
                _,
                theta_prime,
                n_prime,
                s_prime,
                alpha,
                n_alpha,
            ) = _build_tree(
                theta_minus,
                r_minus,
                log_u,
                v,
                j,
                epsilon,
                log_energy_current,
                parameters,
                negative_closure,
                delta_energy_max,
            )
        else:
            (
                _,
                _,
                theta_plus,
                r_plus,
                theta_prime,
                n_prime,
                s_prime,
                alpha,
                n_alpha,
            ) = _build_tree(
                theta_plus,
                r_plus,
                log_u,
                v,
                j,
                epsilon,
                log_energy_current,
                parameters,
                negative_closure,
                delta_energy_max,
            )

        if s_prime == 1 and np.random.uniform() < min(1, n_prime / n):
            theta = theta_prime
            log_energy_current = _log_energy(
                theta, r0, parameters, negative_closure
            ).item()
        n += n_prime
        s = (
            s_prime
            * _stop_criterion(theta_plus, theta_minus, r_minus)
            * _stop_criterion(theta_plus, theta_minus, r_plus)
        )

        if _is_turning(theta_minus, r_minus, theta_plus, r_minus):
            break  # taken from pyro notes code
        j += 1
        tree_count += 1
        if tree_count >= max_tree_depth + 1:
            break

    accept_prob = alpha / n_alpha
    update_tensor_data(parameters, theta)
    return accept_prob
