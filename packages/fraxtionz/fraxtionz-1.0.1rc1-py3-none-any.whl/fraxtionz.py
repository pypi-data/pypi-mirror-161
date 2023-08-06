"""
Fraxtionz, by Elia Toselli.
A module to manage fractions with precision.
"""

import math


class Fraction(object):
    """
The main fraction class.
    """
    def __init__(self, n, d=1):
        """Creates a Fraction object.
        Arguments: n : numerator
                   d : denominator > 0"""
        assert isinstance(n, int)
        assert isinstance(d, int)
        if d == 0:
            raise ZeroDivisionError
        if d < 0:
            raise NotImplementedError("Can't handle denominators <0")
        div = math.gcd(n, d)
        self.n = n // div
        self.d = d // div

    def __str__(self):
        return "{}/{}".format(self.n, self.d)
    def __repr__(self):
        return self.__str__()

    @staticmethod
    def lcm(n, m):
        """ Calculates the lesser common multiple """
        return (n * m) / math.gcd(n, m)

    def lcden(self, other):
        """ Calculates the lesser common denominator """
        return Fraction.lcm(self.d, other.d)

    def __add__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.n * other.d + other.n * self.d,
                            self.d * other.d)
        elif isinstance(other, int):
            other = Fraction(other)
            return Fraction(self.n * other.d + other.n * self.d,
                            self.d * other.d)

    def __radd__(self, other):
        return self.__add__(other)
