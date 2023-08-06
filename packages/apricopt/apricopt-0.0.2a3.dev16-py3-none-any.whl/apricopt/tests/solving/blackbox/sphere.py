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

import numpy as np

def sphere_array(x):
    return np.square(x).sum(axis=1)

def sphere(x):
    return np.square(x).sum()

def sphere_py(x):
    """
    This method implements the function sum_{i in [1..N]} x^2.
    Its global minimum is 0 in point (0,...,0)
    :param x: a list of float, where the i-th element is the i-th coordinate of the point to test
    :return: a float
    """
    res = 0
    for xi in x:
        res += xi ** 2
    return res
