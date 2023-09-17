"""
Solution code for the Hackerrank challenge

'Classes: Dealing with Complex Numbers'
https://www.hackerrank.com/challenges/class-1-dealing-with-complex-numbers/problem
"""

import math


class Complex(object):
    """
    This class defines how to perform common mathematical operators on two
    complex numbers.

    Example, if:
    C = 1.00 + 2.00i
    D = 5.00 + 6.00i

    Complex Number C:
        self.real = 1.00
        self.imaginary = 2.00i

    Complex Number D:
        self.real = 5.00
        self.imaginary = 6.00i

    The __add__ method defines how the '+' operator adds
    these components together, resulting in:
    C + D = 6.00 + 8.00i
    """

    def __init__(self, real, imaginary):
        """
        Initialize and separate a complex number into real and
        imaginary components.
        """
        self.number = complex(real, imaginary)
        self.real = real
        self.imaginary = imaginary

    def __add__(self, complex_two):
        """
        Add two complex numbers together.
        """
        return Complex(self.real + complex_two.real,
                       self.imaginary + complex_two.imaginary)

    def __sub__(self, complex_two):
        """
        Subtract one complex number from another.
        """
        return Complex(self.real - complex_two.real,
                       self.imaginary - complex_two.imaginary)

    def __mul__(self, complex_two):
        """
        Multiply two complex numbers.

        Uses the formula:
        (a + bi) * (c + di) = (ac - bd) + (ad + bc)i

        Where:
        a = self.real
        b = self.imaginary
        c = complex_two.real
        d = complex_two.imaginary
        """
        result_real = (self.real * complex_two.real) - \
                      (self.imaginary * complex_two.imaginary)
        result_imaginary = (self.real * complex_two.imaginary) + \
                           (self.imaginary * complex_two.real)

        return Complex(result_real, result_imaginary)

    def __truediv__(self, complex_two):
        """
        Divide two complex numbers.

        Uses the formula:
        (a + bi) / (c + di) = ((a + bi) * (c - di)) / (c^2 + d^2)

        We can find the equivalent real and imaginary numerators of
        the numerator portion of the formula '((a + bi) * (c - di))'
        via the equivalent:
        numerator_real = (a * c) + (b * d)
        numerator_imaginary = (b * c) - (a * d)

        Where:
        a = self.real
        b = self.imaginary
        c = complex_two.real
        d = complex_two.imaginary
        """
        if complex_two.real == 0.0 and complex_two.imaginary == 0.0:
            raise ZeroDivisionError("Division by zero is not allowed")

        # numerator_real = (a * c) + (b * d)
        numerator_real = (self.real * complex_two.real) + \
                         (self.imaginary * complex_two.imaginary)
        # numerator_imaginary = (b * c) - (a * d)
        numerator_imaginary = (self.imaginary * complex_two.real) - \
                              (self.real * complex_two.imaginary)

        denominator = complex_two.real**2 + complex_two.imaginary**2
        result_real = numerator_real / denominator
        result_imaginary = numerator_imaginary / denominator
        return Complex(result_real, result_imaginary)

    def mod(self):
        """
        Compute the modulus of a complex number.
        """
        result = ((self.real ** 2) + (self.imaginary ** 2)) ** 0.5
        return Complex(result, 0)

    def __str__(self):
        """
        Return a formatted string representation of a complex number
        with two decimal places.
        """
        if self.imaginary == 0:
            result = "%.2f+0.00i" % (self.real)
        elif self.real == 0:
            if self.imaginary >= 0:
                result = "0.00+%.2fi" % (self.imaginary)
            else:
                result = "0.00-%.2fi" % (abs(self.imaginary))
        elif self.imaginary > 0:
            result = "%.2f+%.2fi" % (self.real, self.imaginary)
        else:
            result = "%.2f-%.2fi" % (self.real, abs(self.imaginary))
        return result


if __name__ == '__main__':
    c = map(float, input().split())
    d = map(float, input().split())
    x = Complex(*c)
    y = Complex(*d)
    print(*map(str, [x+y, x-y, x*y, x/y, x.mod(), y.mod()]), sep='\n')
