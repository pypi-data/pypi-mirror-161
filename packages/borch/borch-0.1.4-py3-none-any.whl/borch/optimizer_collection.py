"""
Wrapper to automatically start new optimizer for new tensors as they gets added
"""


class OptimizersCollection:
    """An organizer for a `torch.optim.Optimize` where one can add
    parameters dynamically.

    It is designed to handel models where parameters is added in the forward
    and parameters are not guaranteed to be included in the forward pass.

    Example:
        >>> import torch
        >>> x = torch.tensor([10.], requires_grad=True)
        >>> y = torch.tensor([10.], requires_grad=True)
        >>> optimizer = OptimizersCollection(optimizer=torch.optim.Adam, lr=1)
        >>> def objective(x, y):
        ...    return x*y

        >>> for ii in range(2):
        ...     optimizer.zero_grad()
        ...     loss = objective(x, y)
        ...     loss.backward()
        ...     optimizer.step([x, y])

    """

    def __init__(self, optimizer, *args, **kwargs):
        self.optimizer_creator = optimizer
        self.args = args
        self.kwargs = kwargs
        self.optimizer = None

    def step(self, params, closure=None):
        """Preforms one optimizer step

        Args:
          params: The params to apply the step to
          closure: closure as for the torch.optim interface (Default value = None)

        Returns:
          None

        """
        if self.optimizer is None:
            self.optimizer = self.optimizer_creator(params, *self.args, **self.kwargs)

        update_opt_params(self.optimizer, params)
        self.optimizer.step(closure=closure)

    def zero_grad(self):
        r"""Clears the gradients of all optimized :class:`torch.Tensor` s."""
        if self.optimizer is not None:
            for group in self.optimizer.param_groups:
                for param in group["params"]:
                    param.grad = None


def update_opt_params(optimizer, parameters):
    """
    Update optimizer with new parameters

    Args:
        optimizer (torch.optim.Optimizer): a optimizer to update
        parameters (iterable): iterbale with `torch.Tensor`s

    """
    id_opt_params = [id(x) for pg in optimizer.param_groups for x in pg["params"]]
    new_pars = []
    for par in parameters:
        if not id(par) in id_opt_params:
            new_pars.append(par)
    if new_pars:
        optimizer.add_param_group({"params": new_pars})
