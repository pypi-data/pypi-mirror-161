"""Transform

A ``borch.Graph`` that groups a transformation function(``transform``) and
a parameter(``param``). Where the ``transform`` is applied to the ``param``.
Since it is a ``borch.Graph`` it can be used both as a ``torch.Tensor`` and a
``torch.nn.Module``.

It is useful in cases where we want to optimise a value with some kind of constraint.
For example, standard deviation of a normal distribution is not allowed to be
negative. Therefore we use a Transform with transformation exp(param) and this
transformed tensor will only be defined in the region (0, inf).
"""

from borch.graph import Graph


class Transform(Graph):
    """Apply a transformation to a parameter

    This can come in usefull in situations where one wants to apply some
    from of constraint for a parameter. For example, standard deviation of a normal
    distribution is not allowed to be negative. Therefore we use a ``Transform``
    with transformation exp(param) and this transformed tensor will only be
    defined in the region (0, inf).

    Examples:
        >>> import torch
        >>> sin = Transform(torch.sin, torch.ones(2))
        >>> torch.exp(sin)
        tensor([2.3198, 2.3198])

        The same thing can be acchived by nesting ``Transform``s
        >>> exp = Transform(torch.exp, sin)
        >>> exp*1
        tensor([2.3198, 2.3198])
    """

    def __init__(self, transform, param, posterior=None):
        super().__init__(posterior=posterior)
        self.transform = transform
        self.register_param_or_buffer("param", param)

    def forward(self):
        """Apply the transformation"""
        return self.transform(self.param)
