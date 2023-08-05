"""
Laplace
=======

The laplace approximation extends the maximum a posteriori(MAP)
from an delta distribution to a mulivariet noral with the MAP as
the loc and the covaraiance matrix is estimate from the curvature
of the log joint desnity, derived from a taylor expansion.

Example:
    >>> from borch.infer import laplace
    >>> from borch import nn, infer, RandomVariable, posterior, pq_to_infer, sample
    >>> import borch.distributions as dist
    >>> import torch
    >>> from torch import optim
    >>> class Net(nn.Module):
    ...    def __init__(self):
    ...       super().__init__(posterior=posterior.PointMass())
    ...    def forward(self):
    ...       self.rv = dist.Normal(torch.ones(2), .5*torch.ones(2))
    ...       self.rv2 = dist.Normal(torch.ones(2), .5*torch.ones(2))
    ...       out = self.rv+self.rv2
    ...       return out
    >>> net = Net()
    >>> _ = net()
    >>> # find the map
    >>> opt = optim.LBFGS(net.parameters())
    >>> params = list(net.parameters())
    >>> def closure():
    ...     opt.zero_grad()
    ...     sample(net)
    ...     net()
    ...     loss = infer.vi_loss(**pq_to_infer(net), kl_scaling = 1)
    ...     loss.backward()
    ...     return loss
    >>> for i in range(10):     #doctest: +SKIP
    ...     opt.step(closure)   #doctest: +SKIP
    >>> def laplace_closure():
    ...     sample(net)
    ...     net()
    ...     loss = infer.vi_loss(**pq_to_infer(net), kl_scaling = 1)
    ...     return loss
    >>> fit = laplace.Laplace(laplace_closure, net.parameters())
    >>> fit.sample()
"""
import torch
from borch import distributions as dist
from borch.utils.torch_utils import hessian
from borch.utils.numpy_utils import nearest_pos_def_mat


def _update_params_data_(params, values):
    i = 0
    for par in params:
        n_elm = len(par.view(-1))
        par.data = values[i : i + n_elm].view_as(par)
        i += n_elm


def _update_params_(params, values):
    i = 0
    for par in params:
        n_elm = len(par.view(-1))
        par.detach_().copy_(values[i : i + n_elm].view_as(par))
        i += n_elm


def _make_symmetric(mat, epsilon):
    mat[~torch.isfinite(mat)] = epsilon  # pylint: disable=invalid-unary-operand-type
    mat = (mat + torch.t(mat)) * 0.5
    mat[range(len(mat)), range(len(mat))] = torch.diagonal(mat).clamp(min=epsilon)
    return mat


def _pos_def_cov_mat(hess):
    cov_mat = _make_symmetric(hess.inverse().sqrt(), 0)
    cov_mat = torch.tensor(  # pylint: disable=not-callable
        nearest_pos_def_mat(cov_mat.cpu().numpy())
    )
    return _make_symmetric(cov_mat, 1e-6)


def _symetric_hessian(loss_clossure, value):
    hess = hessian(loss_clossure(), value, create_graph=False, allow_unused=True)
    hess = hess.cpu()
    hess = _make_symmetric(hess, 0)
    return torch.tensor(  # pylint: disable=not-callable
        nearest_pos_def_mat(hess.cpu().numpy())
    )


class Laplace:
    """
    The laplace approximation extends the maximum a posteriori(MAP)
    from a delta distribution to a multivariate normal with the MAP as
    the loc and the covariance matrix as an estimate of the curvature
    of the log joint density, derived from a Taylor expansion.

    Args:
        loss_clossure (closure): returns the loss
        params (iterable): the parameters to form a laplace approximation
            for.


    Example:
        >>> from borch.infer import laplace
        >>> from borch import nn, infer, RandomVariable, posterior, sample, pq_to_infer
        >>> import borch.distributions as dist
        >>> from torch import optim
        >>> import torch
        >>> class Net(nn.Module):
        ...    def __init__(self):
        ...       super().__init__(posterior=posterior.PointMass())
        ...    def forward(self):
        ...       self.rv = dist.Normal(torch.ones(2), .5*torch.ones(2))
        ...       self.rv2 = dist.Normal(torch.ones(2), .5*torch.ones(2))
        ...       out = self.rv+self.rv2
        ...       return out
        >>> net = Net()
        >>> _ = net()
        >>> opt = optim.LBFGS(net.parameters())
        >>> params = list(net.parameters())
        >>> def closure():
        ...     opt.zero_grad()
        ...     sample(net)
        ...     net()
        ...     loss = infer.vi_loss(**pq_to_infer(net), kl_scaling = 1)
        ...     loss.backward()
        ...     return loss
        >>> for i in range(10):         #doctest: +SKIP
        ...     _ = opt.step(closure)   #doctest: +SKIP
        >>> def laplace_closure():
        ...     sample(net)
        ...     net()
        ...     loss = infer.vi_loss(**pq_to_infer(net), kl_scaling = 1)
        ...     return loss
        ...     return loss
        >>> fit = laplace.Laplace(laplace_closure, net.parameters())
        >>> fit.sample()
    """

    def __init__(self, loss_clossure, params):
        self.params = list(params)
        try:
            self.loc = torch.cat(
                [par.clone().detach().view(-1) for par in self.params]
            ).requires_grad_(True)
            _update_params_(self.params, self.loc)
            hess = _symetric_hessian(loss_clossure, self.loc)
            cov_mat = (
                _pos_def_cov_mat(hess).detach().to(self.loc.device).to(self.loc.dtype)
            )
            self.dist = dist.MultivariateNormal(
                self.loc.detach(), covariance_matrix=cov_mat
            )
        finally:
            for par in self.params:
                par.detach_().requires_grad_(True)

    def sample(self):
        """
        Update the parameters with a new sample drawn from the Laplace approximation.
        """
        _update_params_data_(self.params, self.dist.distribution.sample())

    def to(self, val):  # pylint: disable=invalid-name
        """
        Move the weight to a device, dtype,... etc. it mimics the `.to()`
        function of `nn.Modules`
        """
        self.dist = self.dist.to(val)
