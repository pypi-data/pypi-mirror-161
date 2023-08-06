"""
Fraxtionz, by Elia Toselli.
A module to manage fractions with precision.
"""


class Fraction(object):
    """
The main fraction class.
    """
    def __init__(self, n, d):
        """Creates a Fraction object.
        Arguments: n : numerator
                   d : denominator > 0"""
        assert isinstance(n, int)
        assert isinstance(d, int)
        if d == 0:
            raise ZeroDivisionError
        if d < 0:
            raise NotImplementedError("Can't handle denominators <0")
        self.n = n
        self.d = d
