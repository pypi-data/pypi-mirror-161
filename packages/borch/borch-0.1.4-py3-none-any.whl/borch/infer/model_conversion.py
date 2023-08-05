"""
Functions to convert models to callable functions
"""
from borch.infer.log_prob import log_prob, log_prob_volume_adjustment
from borch.module import pq_to_infer


def model_to_neg_log_prob_closure(closure, model):
    """Create a closure that calculates the log_prob of the model with volume
    adjustments.

    Args:
      closure: Closure that evaluates the model, with the model object.
      model:  borch.Module.

    Returns:
        Function closure to evaluate the negative log probability.

    Example:
        >>> from borch import RandomVariable, distributions, Module
        >>> from borch.posterior import PointMass
        >>> import torch
        >>>
        >>> def model(bm):
        ...     bm.weight = distributions.Normal(0,1)
        >>>
        >>> def closure():
        ...     model(bm)
        >>>
        >>> bm = Module(posterior=PointMass())
        >>> bm.observe(weight=torch.tensor(1.))
        >>> log_prob = model_to_neg_log_prob_closure(closure, bm)
        >>> print(log_prob())
        tensor(1.4189)
    """

    def model_closure():
        """Closure for the negative log_prob"""
        closure()
        kwargs = pq_to_infer(model)
        log_joint = log_prob(**kwargs) + log_prob_volume_adjustment(**kwargs)
        return -log_joint

    return model_closure
