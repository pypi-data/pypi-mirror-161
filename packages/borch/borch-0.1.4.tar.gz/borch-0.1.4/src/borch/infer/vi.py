# pylint: disable=too-many-arguments, invalid-name

"""VI regularization terms

Variational inference tries to solve the inference problem by optimization,
this is done by also specifying the approximating distribution manually and optimize the
parameters of the approximating distribution with stochastic gradients descent.

One usually maximizes the evidence lower bound(ELBO) of the model. This
manifests itself as a difference between the prior(p_dist) and the approximating
distribution(q_dist). There are several different expressions for the ELBO and
some of the loss functions can for example only be used if a
reparameterized sample is possible to generate from the q_dist.

infer implements ``vi_loss`` which automatically selects the the best loss function
to use.

Example:
    >>> import torch
    >>> import torch.distributions as dist
    >>> params = [torch.ones(1, requires_grad=True) for i in range(10)]
    >>> p_dists = [dist.Cauchy(0,1) for _ in range(5)]
    >>> observed = [False for _ in range(5)]
    >>> opt = torch.optim.Adam(params)
    >>> for i in range(2):
    ...     opt.zero_grad()
    ...     q_dists  = [dist.Normal(params[2*i],params[2*i+1]) for i in range(5)]
    ...     values = [q_dist.rsample() for q_dist in q_dists]
    ...     loss =  vi_loss(p_dists, q_dists, values, observed, 1)
    ...     loss.backward()
    ...     opt.step()

"""
from itertools import compress

import numpy
from torch.autograd import grad
import torch

from borch import distributions
from borch.distributions.distribution_utils import detach_dist
from borch.infer.log_prob import negative_log_prob


def _split(p_dists, q_dists, values, observed):
    not_observed = [not i for i in observed]
    no_p_dists = list(compress(p_dists, not_observed))
    no_q_dists = list(compress(q_dists, not_observed))
    o_p_dists = list(compress(p_dists, observed))
    o_q_dists = list(compress(q_dists, observed))
    no_values = list(compress(values, not_observed))
    o_values = list(compress(values, observed))
    return no_p_dists, no_q_dists, o_p_dists, o_q_dists, no_values, o_values


def _split_observed_latent(p_dists, q_dists, values, observed):
    no_p_dists, no_q_dists, o_p_dists, _, no_values, o_values = _split(
        p_dists, q_dists, values, observed
    )
    return no_p_dists, no_q_dists, o_p_dists, no_values, o_values


def _split_delta(p_dists, q_dists, values):
    delta_qdist = [isinstance(q_dist, distributions.Delta) for q_dist in q_dists]
    return _split(p_dists, q_dists, values, delta_qdist)


def _support_kl(p_dists, q_dists):
    return [
        distributions.kl_exists(p_dist, q_dist)
        for p_dist, q_dist in zip(p_dists, q_dists)
    ]


def _support_rsample(q_dists):
    return [q_dist.has_rsample for q_dist in q_dists]


def _support_kl_or_rsample(p_dists, q_dists):
    return [
        kl or rsample is True
        for kl, rsample in zip(_support_kl(p_dists, q_dists), _support_rsample(q_dists))
    ]


def _check_not_delta(*args, loss_fn):
    for dist in args:
        if isinstance(dist, distributions.Delta):
            raise RuntimeError(f"{loss_fn} does not support Delta distributions")


def elbo_loss(p_dist, q_dist, value):
    r"""Calculates the elbo:

    .. math::
        -(\log p(\textbf{x}) - \log q(\textbf{x}|\textbf{z}))
    where :math:``p`` is ``p_dist``, :math:``q`` is ``q_dist``
    and :math:``x`` is ``value``.

    Args:
      p_dist: torch.distributions.Distribution, the prior
      q_dist: torch.distributions.Distribution, the approximating distribution
      value: torch.tensor, the value where the elbo is evaluated at.

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> elbo_loss(dist.Cauchy(0,1), dist.Normal(1,1), torch.ones(1))
        tensor(0.9189)

    """
    return (-p_dist.log_prob(value) + q_dist.log_prob(value)).sum()


def prior_loss(p_dist, q_dist, value):  # pylint: disable=unused-argument
    r"""Calculates the loss where the values only the prior
    contributes to the los

    .. math::
        -\log p(\textbf{x})
    where :math:``p`` is ``p_dist``and :math:``x`` is ``value``.

    Args:
      p_dist: torch.distributions.Distribution, the prior
      q_dist: torch.distributions.Distribution, the approximating distribution
      value: torch.tensor, the value where the elbo is evaluated at.

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> prior_loss(dist.Cauchy(0,1), dist.Normal(1,1), torch.ones(1))
        tensor(1.8379)

    """
    return -p_dist.log_prob(value).sum()


def elbo_score_function_loss(p_dist, q_dist, value):
    r"""Calculates the elbo with the score function:

    .. math::
        -\log q(\textbf{x}|\textbf{z})(\log p(\textbf{x}) -
        \log q(\textbf{x}|\textbf{z}))

    where :math:``p`` is ``p_dist``, :math:``q`` is ``q_dist``
    and :math:``x`` is ``value``.

    Args:
      p_dist: torch.distributions.Distribution, the prior
      q_dist: torch.distributions.Distribution, the approximating distribution
      value: torch.tensor, the value where the elbo is evaluated at.

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> elbo_score_function_loss(
        ...     dist.Cauchy(0,1), dist.Normal(1,1), torch.ones(1))
        tensor(-0.8444)
    """
    _check_not_delta(q_dist, p_dist, loss_fn="elbo_score_function_loss")
    value = value.detach()
    q_log_prob = q_dist.log_prob(value)
    return (q_log_prob * (-p_dist.log_prob(value) + q_log_prob)).sum()


def elbo_entropy_loss(p_dist, q_dist, value):
    r"""Calculates the elbo with the entropy of the q_dist:

    .. math::
        -(\log p(\textbf{x}) + \mathbb{H}[q])

    where :math:``p`` is ``p_dist``, :math:``q`` is ``q_dist``
    and :math:``x`` is ``value``.

    Args:
      p_dist: torch.distributions.Distribution, the prior
      q_dist: torch.distributions.Distribution, the approximating distribution
      value: torch.tensor, the value where the elbo is evaluated at.

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> elbo_loss(dist.Cauchy(0,1), dist.Normal(1,1), torch.ones(1))
        tensor(0.9189)

    """
    _check_not_delta(q_dist, p_dist, loss_fn="elbo_entropy_loss")
    return (-p_dist.log_prob(value) - q_dist.entropy()).sum()


def vi_regularization(p_dists, q_dists, values, div_fn=elbo_loss):
    r"""Calculates a regularization term, given the provided div_fn

    Args:
      p_dists: list with torch.distributions.Distribution, the prior distributions
      q_dists: list with torch.distributions.Distribution, the approximating
        distributions
      values: list with torch.tensors
      div_fn: Python callable (Default value = elbo_loss)

    Returns:
        torch.tensor

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> import borch.infer as infer
        >>> p_dists = [dist.Cauchy(0,1) for _ in range(5)]
        >>> q_dist  = [dist.Normal(0,1) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(5)]
        >>> vi_regularization(p_dists, q_dist, values, infer.elbo_loss)
        tensor(-6.4327)

    """
    if not len(p_dists) == len(q_dists) == len(values):
        raise ValueError("the provided lists must have the same length")

    loss = 0
    for p_dist, q_dist, value in zip(p_dists, q_dists, values):
        if isinstance(q_dist, distributions.Delta):
            loss += prior_loss(p_dist, q_dist, value)
        else:
            loss += div_fn(p_dist, q_dist, value)
    return loss


def elbo_path_derivative_loss(p_dist, q_dist, value):
    r"""Calculates the elbo with path derivative:

    .. math::
        -(\log p(\textbf{x}) - \log q(\textbf{x.detach()}|\textbf{z}))
    where :math:``p`` is ``p_dist``, :math:``q`` is ``q_dist``
    and :math:``x`` is ``value``.

    Args:
      p_dist: torch.distributions.Distribution, the prior
      q_dist: torch.distributions.Distribution, the approximating distribution
      value: torch.tensor, the value where the elbo is evaluated at.

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import borch.distributions as dist
        >>> elbo_path_derivative_loss(
        ...     dist.Cauchy(0,1),
        ...     dist.Normal(1,1),
        ...     torch.ones(1))
        tensor(0.9189)

    """
    return (-p_dist.log_prob(value) + detach_dist(q_dist).log_prob(value)).sum()


def analytical_kl_divergence_loss(p_dist, q_dist, value=None, backup_loss_fn=None):
    r"""
    Calculates the analytical kl divergence if it is available, and falls back
    to the backup_loss_fn. If no backup_loss_fn is provided, ``elbo_loss`` will be used.


    .. math::
        \mathbb{KL}(q(\textbf{x}|\textbf{z})|| p(\textbf{x}))

    Args:
        p_dist: torch.distributions.Distribution
        q_dist: torch.distributions.Distribution
        value: torch.tensor
        backup_loss_fn: callable, with the args p_dist, q_dist, value

    Returns:
        torch.tensor

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> analytical_kl_divergence_loss(
        ...     dist.Normal(0,1),
        ...     dist.Normal(1,1),
        ...     torch.ones(1))
        tensor(0.5000)
    """
    if backup_loss_fn is None:
        backup_loss_fn = elbo_loss

    if distributions.kl_exists(p_dist, q_dist):
        loss = distributions.kl_divergence(p_dist, q_dist).sum()
        if not torch.isfinite(loss):  # pragma: no cover
            loss = backup_loss_fn(p_dist, q_dist, value)
    else:
        loss = backup_loss_fn(p_dist, q_dist, value)
    return loss


def elbo_score_function(p_dists, q_dists, values, regularization):
    r"""Calculates the elbo with the score function

    .. math::
        -\log q(\textbf{x}|\textbf{z})(\log p(\textbf{x}) -
        \log q(\textbf{x}|\textbf{z})-\textbf{R})

    where :math:`p_i` is element i of `p_dists`, :math:`q_i` is element i of `q_dists`,
    :math:`x_i` is  element i of `values` and :math:`\textbf{R}` is the regularization.

    Args:
      p_dist (iterable): iterable with torch.distributions.Distributions, the prior
      q_dist (iterable): iteable with torch.distributions.Distribution, the
        approximating distributions
      value (iterable): iterable with torch.tensors, the value where the elbo is
        evaluated at.
      regularization (torch.tensor): any other regularization loss

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> p_dists = [dist.Cauchy(0,1) for _ in range(5)]
        >>> q_dist  = [dist.Normal(0,1) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(5)]
        >>> elbo_score_function(p_dists, q_dist, values, 0)
        tensor(126.0460)
    """
    if not len(p_dists) == len(q_dists) == len(values):
        raise ValueError("the provided lists must have the same length")

    p_dists, q_dists, delta_p_dists, delta_q_dists, values, delta_values = _split_delta(
        p_dists, q_dists, values
    )
    delta_dist_loss = vi_regularization(
        delta_p_dists, delta_q_dists, delta_values, div_fn=prior_loss
    )
    values = [value.detach() for value in values]
    log_prob_p = sum(
        p_dist.log_prob(value).sum() for p_dist, value in zip(p_dists, values)
    )

    log_prob_q = sum(
        q_dist.log_prob(value).sum() for q_dist, value in zip(q_dists, values)
    )

    return -(
        log_prob_q
        * (log_prob_p.detach() - log_prob_q - regularization + delta_dist_loss)
    ).sum()


def elbo_rb_score_function(sub_samples):
    """
    Implements algorithm 2 in :cite:``Ranganath``

    It is a Rao-Blackwellization of the ``elbo_score_function``.

    Args:
        sub_samples (iterable): iterable with dictionaries, with the key's
            ``p_dists``, ``q_dists``, ``values``, ``parameters``, and
            ``regularization``. Where ``p_dists`` is an iterable with
            ``torch.distributions.Distributions`` (the prior), ``q_dists``
            iterable with ``torch.distributions. Distribution``s
            (the approximating distributions), ``values`` are where the ``p_dists``,
            ``q_dists`` are evaluated and should be an iterable with torch.tensors,
            ``parameters`` optimizeable tensors corresponding to the approximating
            distributions and should be an iterable with torch.tensors and
            regularization is any regularization term one wants to include, it
            should be a torch.tensor

    Returns:
        torch.tensor, the loss

    Examples:
        >>> import torch
        >>> import torch.distributions as dist
        >>> mu = torch.ones(1, requires_grad = True)
        >>> sigma = torch.ones(1, requires_grad = True)
        >>> def sub_sample(n_var):
        ...     return {'p_dists': [dist.Normal(1, 1) for _ in range(n_var)],
        ...              'q_dists': [dist.Normal(mu, sigma) for _ in
        ... range(n_var)],
        ...              'values': [mu + sigma * torch.randn(1) for _ in
        ... range(n_var)],
        ...              'parameters': [mu, sigma],
        ...              'regularization': torch.ones(1)}
        >>> sub_samples = [sub_sample(5) for _ in range(10)]
        >>> loss = elbo_rb_score_function(sub_samples)
    """
    #  using h and f from the paper
    elbo, f, log_prob_q, h = [], [], [], []
    for sample in sub_samples:
        elbo_temp = elbo_score_function(
            regularization=sample["regularization"],
            p_dists=sample["p_dists"],
            q_dists=sample["q_dists"],
            values=sample["values"],
        )
        elbo.append(elbo_temp)
        f.append(grad(elbo_temp, sample["parameters"], create_graph=True))
        log_prob_q_temp = sum(
            q_dist.log_prob(val)
            for q_dist, val in zip(sample["q_dists"], sample["values"])
        )
        log_prob_q.append(log_prob_q_temp)
        h.append(grad(log_prob_q_temp, sample["parameters"], create_graph=True))
    tot_cov, tot_var = 0, 0
    for param in range(len(sub_samples[0]["parameters"])):
        temp_h = [float(h[ii][param]) for ii in range(len(f))]
        temp_f = [float(f[ii][param]) for ii in range(len(f))]
        tot_cov += numpy.cov(temp_f, temp_h)[0][1]
        tot_var += numpy.var(temp_h)
    if tot_var == 0.0:
        raise ValueError(
            "The variance evaluated to 0, this will result in "
            "nan in the loss function. Make sure that "
            "the values are different between the different"
            "sub samples."
        )
    return (sum(elbo) - float(tot_cov / tot_var) * sum(log_prob_q)).sum()


def elbo_score_entropy(p_dists, q_dists, values, regularization):
    r"""Calculates the elbo with the score function

    .. math::
        -(\log q(\textbf{x}|\textbf{z})*\log p(\textbf{x}) + \textbf{H}[z]
        -\textbf{R})

    where :math:``p_i`` is element i of ``p_dists``, :math:``q_i`` is element i of
    ``q_dists``, :math:``x_i`` is  element i of ``values`` and :math:``\textbf{R}``
    is the regularization.

    Args:
      p_dist (iterable): iterable with torch.distributions.Distributions, the prior
      q_dist (iterable): iteable with torch.distributions.Distribution,
        the approximating distributions
      value (iterable): iterable with torch.tensors, the value where the elbo is
        evaluated at.
      regularization (torch.tensor): any other regularization loss

    Returns:
      torch.tensor the elbo

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> p_dists = [dist.Cauchy(0,1) for _ in range(5)]
        >>> q_dist  = [dist.Normal(0,1) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(5)]
        >>> elbo_score_entropy(p_dists, q_dist, values, 0)
        tensor(-265.0007)
    """
    if not len(p_dists) == len(q_dists) == len(values):
        raise ValueError("the provided lists must have the same length")

    values = [value.detach() for value in values]
    log_prob_p = sum(p_dist.log_prob(value) for p_dist, value in zip(p_dists, values))

    log_prob_q = sum(q_dist.log_prob(value) for q_dist, value in zip(q_dists, values))

    entropy_q = sum(q_dist.entropy() for q_dist in q_dists)

    return -(log_prob_q * log_prob_p + entropy_q - regularization).sum()


def vi_loss(p_dists, q_dists, values, observed, kl_scaling=1, div_fn=elbo_loss):
    r"""Calculates a regularization term for VI, it checks if rsample is
    avalible for all q_dists and applies ``div_fn``. If not it uses
    elbo_score_function as a backup.

    Note in some cases distributions that does not support analytical KL
    divergence and rsample is used, it can be better to use the function
    ``elbo_rb_score_function`` which utilizes sub samples to reduce variance.

    Args:
      p_dists (iterable): list with torch.distributions.Distribution, the prior
        distributions
      q_dists (iterable): list with torch.distributions.Distribution,
        the approximating distributions
      values (iterable): list with torch.tensors, where the distributions are
        evaluated.
      observed (iterable): list with booleans, if True that index in all of the
        lists will be treated as observed.
      kl_scaling (float): sets the scale of of the ELBO term.
      div_fn (callable): function to be used to calculate the divergance term
    Returns:
        torch.tensor

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> p_dists = [dist.Cauchy(0,1) for _ in range(5)]
        >>> q_dist  = [dist.Normal(0,1) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(5)]
        >>> observed = [False for _ in range(5)]
        >>> vi_loss(p_dists, q_dist, values, observed, 1)
        tensor(-6.4327)

    """
    no_p_dists, no_q_dists, o_p_dists, no_values, o_values = _split_observed_latent(
        p_dists, q_dists, values, observed
    )
    rsample_possible = all(_support_rsample(no_q_dists))

    nll = negative_log_prob(o_p_dists, o_values)
    if rsample_possible:
        return nll + kl_scaling * vi_regularization(
            no_p_dists, no_q_dists, no_values, div_fn=div_fn
        )

    kl_or_rsample_possible = all(_support_kl_or_rsample(no_p_dists, no_q_dists))
    if kl_or_rsample_possible:
        return nll + kl_scaling * vi_regularization(
            no_p_dists, no_q_dists, no_values, div_fn=analytical_kl_divergence_loss
        )

    return elbo_score_function(no_p_dists, no_q_dists, no_values, nll * 1 / kl_scaling)


def vi_analytical_kl_loss(p_dists, q_dists, values, observed, kl_scaling=1):
    r"""Calculates a regularization term for VI, it uses the analytical KL
    divergence as a loss function if possible otherwise it uses
    elbo_score_function as a backup.

    Note in some cases distributions that does not support analytical KL
    divergence and rsample is used, it can be better to use the function
    ``elbo_rb_score_function`` which utilizes sub samples to reduce variance.

    Args:
      p_dists (iterable): list with torch.distributions.Distribution, the prior
        distributions
      q_dists (iterable): list with torch.distributions.Distribution,
        the approximating distributions
      values (iterable): list with torch.tensors, where the distributions are
        evaluated.
      observed (iterable): list with booleans, if True that index in all of the
        lists will be treated as observed.
      kl_scaling (float): sets the scale of of the ELBO term.
    Returns:
        torch.tensor

    Example:
        >>> import torch
        >>> import torch.distributions as dist
        >>> p_dists = [dist.Cauchy(0,1) for _ in range(5)]
        >>> q_dist  = [dist.Normal(0,1) for _ in range(5)]
        >>> values = [torch.tensor(float(ii)) for ii in range(5)]
        >>> observed = [False for _ in range(5)]
        >>> vi_analytical_kl_loss(p_dists, q_dist, values, observed, 1)
        tensor(-6.4327)

    """
    no_p_dists, no_q_dists, o_p_dists, no_values, o_values = _split_observed_latent(
        p_dists, q_dists, values, observed
    )

    kl_or_rsample_possible = all(_support_kl_or_rsample(no_p_dists, no_q_dists))

    nll = negative_log_prob(o_p_dists, o_values)
    if kl_or_rsample_possible:
        return nll + kl_scaling * vi_regularization(
            no_p_dists, no_q_dists, no_values, div_fn=analytical_kl_divergence_loss
        )

    return elbo_score_function(no_p_dists, no_q_dists, no_values, nll * 1 / kl_scaling)
