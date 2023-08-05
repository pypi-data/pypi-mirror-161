"""An automatic posterior will automatically add approximating distributions
based on the ``RandomVariable`` objects that are used in any call."""

from warnings import warn

import torch

import borch
from borch.posterior.posterior import Posterior
import borch.distributions.distribution_utils as dist_utl


class Automatic(Posterior):
    """An automatic posterior will automatically add approximating distributions
    based on the ``RandomVariable`` objects that are used in any call.

    It will use the same type of distribution as the prior and initialize the
    variables in the same point as the prior, but if some of the arguments
    of the prior requires gradients, it will create an parameter for this
    argument.

    Examples:
        >>> import borch
        >>> import borch.distributions as dist
        >>> class Model(borch.Module):
        ...     def __init__(self):
        ...         super().__init__(posterior=Automatic())
        ...         self.student_t = dist.StudentT(3, 3, 4)
        ...         self.gamma = dist.Gamma(.5, .5)
        ...     def forward(self):
        ...         self.y = dist.Normal(self.student_t, self.gamma)
        ...         return self.y
        >>> model = Model()
        >>> type(model())
        <class 'torch.Tensor'>

        The posterior will be initialized with the same type of distribution
        and the same values for the parameters.

        >>> type(model.posterior.student_t)
        <class 'borch.distributions.rv_distributions.StudentT'>
        >>> model.posterior.student_t.loc == model.prior.student_t.loc
        tensor(True)
        >>> model.posterior.student_t.scale == model.prior.student_t.scale
        tensor(True)


        The main purpose of the ``Automatic`` posterior is that keeps the hierarchy
        of the model. In this case it means that the ``loc`` of ``y`` will be updated
        with the value of ``student_t`` in every forward call in such a way that the
        gradients will propagate.

        >>> model.posterior.y.loc == model.student_t
        tensor(True)
        >>> borch.sample(model)
        >>> _ = model()
        >>> model.posterior.y.loc == model.student_t
        tensor(True)
        >>> id(model.posterior.y.loc) == id(model.student_t)
        True
    """

    def register_random_variable(self, name, rv):
        """A passed RandomVariable will be cloned and an appropriate
        approximating distribution will be returned in its place, based on
        whether the given ``rv`` had an approximating distribution or not."""
        if not torch.is_grad_enabled():
            warn(
                """Automatic posterior can result in different
                    behavior if executed in a ``toch.no_grad`` context then
                    outiside. All distributions will be created with
                    leaf nodes as arguments"""
            )
        setattr(self, name, dist_utl.dist_to_qdist_infer_hierarchy(rv))

    def update_random_variable(self, name, rv):
        q_rv = getattr(self, name)
        for key, _ in q_rv.named_buffers(recurse=False):
            if key == borch.graph.TENSOR_ATTR:
                continue
            setattr(q_rv, key, getattr(rv, key))
        q_rv()
