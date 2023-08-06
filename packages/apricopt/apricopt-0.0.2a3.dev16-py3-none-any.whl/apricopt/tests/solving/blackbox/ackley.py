"""
This file is part of Apricopt.

Apricopt is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Apricopt is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Apricopt.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2020-2021 Marco Esposito, Leonardo Picchiami.
"""

import math

import numpy as np


def ackley(x) -> float:
    """
    The Ackley function
    :param x: the input
    :return: a float
    """
    a = 20
    b = 0.2
    c = 2 * math.pi

    d = len(x)
    sum1 = np.square(x).sum()#axis=1)
    dot = np.dot(c, x)
    cos = np.cos(dot)
    sum2 = cos.sum()#axis=1)

    term1 = -a * np.power(math.e, -b * np.sqrt(sum1 / d))
    term2 = -np.power(math.e, sum2 / d)

    return term1 + term2 + a + math.e

def ackley_py(x) -> float:
    """
    The Ackley function
    :param x: the input
    :return: a float
    """
    d = len(x)
    sum1 = 0
    sum2 = 0
    for xi in x:
        sum1 += xi**2
        sum2 += math.cos(2 * math.pi*xi)

    return -20 * math.pow(math.e, -0.2*math.sqrt(sum1 / d)) + -math.pow(math.e, sum2 / d) + 20 + math.e
