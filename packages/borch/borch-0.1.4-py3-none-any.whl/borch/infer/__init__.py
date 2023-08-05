"""
Infer
=====

Bayesian inference this commonly involves computing  an approximate posterior
distribution for the paramaters of the model. There are two common approaches,
markov sampling and variational inference

Infer is a collection of inference algortihms and loss functions to train models,
it has support for Variational Inference trough loss functions and Monete Carlo
estimation using classical algorithms like HMC and NUTS.

It also extends to more excostic traings scheems like Weight smoothing of
networks(Mean teacher).

The training loop for normal VI looks like:
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

The No-U-Turn Sampler (NUTS) algorithm can be used like:
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

from borch.infer.nuts import nuts_step, find_reasonable_epsilon, dual_averaging
from borch.infer.hmc import hmc_step
from borch.infer.vi import (
    vi_regularization,
    elbo_loss,
    elbo_path_derivative_loss,
    analytical_kl_divergence_loss,
    vi_loss,
)
from borch.infer.log_prob import negative_log_prob, negative_log_prob_loss
from borch.infer.hard_negative_mining import hard_negative_mining
