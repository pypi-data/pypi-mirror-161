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
from apricopt.tests.solving.blackbox.ackley import ackley

random.seed(14)

dimension = 20

lower_bounds = [-32.768] * dimension
upper_bounds = [32.768] * dimension

black_box = FunctionBlackBox(dimension, ackley, lower_bounds, upper_bounds)

solver = PySwarmsSolver()

options = {'iterations': 1000, 'n_particles': 10,
           'search': True,
           'search_n_particles': 10,
           'search_iters': 10,
           'search_n_selection_iters': 100}
result = solver.solve(black_box, options)

print(result)
