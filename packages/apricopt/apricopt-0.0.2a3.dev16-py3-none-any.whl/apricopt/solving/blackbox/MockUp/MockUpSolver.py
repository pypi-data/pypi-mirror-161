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

from typing import Dict
import random

from apricopt.solving.blackbox.BlackBox import BlackBox
from apricopt.solving.blackbox.BlackBoxSolver import BlackBoxSolver


class MockUpSolver(BlackBoxSolver):

    def __init__(self):
        super().__init__()

    def solve(self, black_box: BlackBox,
              solver_params: list) -> (Dict[str, float], float, float):
        min_obj = float("Inf")
        min_params = None
        for i in range(solver_params[0]):
            print(f"Iteration {i+1}")
            params = dict()
            for param_id in black_box.get_optimization_parameters_ids():
                params[param_id] = random.uniform(black_box.get_optimization_parameter_lower_bound(param_id),
                                                  black_box.get_optimization_parameter_upper_bound(param_id))
            print(f"Parameters: {params}")

            params_values_dict = params
            print(f"\nTrying with params: {params_values_dict}")
            result: Dict[str, float] = black_box.evaluate(params_values_dict)
            extreme_barrier_violated = False
            for extreme_barrier_id in black_box.get_extreme_barrier_constraints_ids():
                if result[extreme_barrier_id] > 0:
                    extreme_barrier_violated = True
                    print(f"Violated Extreme Barrier Constraint: {extreme_barrier_id} with value "
                          f"{result[extreme_barrier_id]}")
                    break

            if not extreme_barrier_violated:
                objective: float = result[black_box.get_objective_id()]
                print(f"Objective value: {objective}")
                if objective <= min_obj:
                    min_obj = objective
                    min_params = params

        return min_params, min_obj, solver_params[0], solver_params[0], solver_params[0]
