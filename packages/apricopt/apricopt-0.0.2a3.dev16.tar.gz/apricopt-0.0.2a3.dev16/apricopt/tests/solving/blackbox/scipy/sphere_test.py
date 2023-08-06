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
from apricopt.solving.blackbox.scipy.SciPySolver import SciPySolver
# from apricopt.tests.solving.blackbox.sphere import sphere
from apricopt.tests.solving.blackbox.ackley import ackley
random.seed(14)

dimension = 20

# lower_bounds = [-5.12] * dimension
# upper_bounds = [5.12] * dimension

# Since Nelder-Mead does not support bound constraints, we set them to None
# (we could have called FunctionBlackBox without the last two arguments)
lower_bounds = [-100] * dimension# None
upper_bounds = [100] * dimension# None
#upper_bounds = None
# black_box = FunctionBlackBox(dimension, sphere, lower_bounds, upper_bounds)
black_box = FunctionBlackBox(dimension, ackley, lower_bounds, upper_bounds)

solver = SciPySolver()
max_restarts = 100
max_non_improving_restarts = 10
restart_points = [black_box.get_random_initial_values_np_array() for _ in range(max_restarts)]
options = {"method": "trust-constr",
           'max_restarts': max_restarts,
           'max_non_improving_restarts': max_non_improving_restarts,
           'restart_points': restart_points,
           'jac': '2-point'}

result = solver.solve(black_box, options)

print("\n\nOptimization results:")
print(result)
