"""
Transformation functions
"""


class IdentityTransform:
    """Applies an identity transform, i.e. it returns the input whit out any
     modification to it.

    Args:
      val: any python object or callable

    Returns:
      the input

    """

    def __call__(self, val):
        return self.transormation(val)

    def inv(self, val):  # pylint: disable=R
        """
        applies inverse of the transormation to val
        :param val: torch.tensor
        :return: torch.tensor
        """
        return val

    def transormation(self, val):  # pylint: disable=R
        """
        applies transformation to val
        :param val: torch.tensor
        :return: torch.tensor
        """
        return val
