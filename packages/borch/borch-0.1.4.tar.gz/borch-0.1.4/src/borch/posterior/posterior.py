"""Base class to create a custom posterior"""
from torch.nn import Module


class Posterior(Module):
    """Base class to create a posterior"""

    def register_random_variable(self, name, rv):
        r"""Called the first time a RandomVariable gets added"""
        raise NotImplementedError

    def update_random_variable(self, name, rv):
        """Code that gets run every time a random variable is added to a model"""

    def set_random_variable(self, name, rv):
        """If __setattr__ gets called on a model it will call here"""
        if not hasattr(self, name):
            self.register_random_variable(name, rv)
        self.update_random_variable(name, rv)
        return getattr(self, name)

    def forward(self):
        """Don't call this, not supported"""
        raise RuntimeError(f"{self.__class__.__name__} does not support a forward call")
