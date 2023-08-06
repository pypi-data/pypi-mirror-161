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

import random

from apricopt.solving.blackbox.FunctionBlackBox import FunctionBlackBox
from apricopt.solving.blackbox.pyswarms.PySwarmsSolver import PySwarmsSolver
from apricopt.tests.solving.blackbox.sphere import sphere

random.seed(14)

dimension = 20

lower_bounds = [-5.12] * dimension
upper_bounds = [5.12] * dimension

black_box = FunctionBlackBox(dimension, sphere, lower_bounds, upper_bounds)

solver = PySwarmsSolver()
options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
result = solver.solve(black_box, options)

print(result)
