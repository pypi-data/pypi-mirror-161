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
from typing import Dict, Any, List, Tuple

from apricopt.solving.blackbox.BlackBox import BlackBox
from apricopt.solving.blackbox.BlackBoxSolver import BlackBoxSolver

DEFAULT_MAX_RESTARTS = 1
DEFAULT_MAX_NON_IMPROVING_RESTARTS = 1

custom_options_names = ['method', 'max_restarts', 'max_non_improving_restarts', 'restart_points', 'jac']


class SciPySolver(BlackBoxSolver):

    def solve(self, black_box: BlackBox, solver_params: Dict[str, Any]) \
            -> (Dict[str, float], float, float, float, float):
        # TODO check validity of solver params (e.g. max_restarts > 0)
        from scipy.optimize import minimize

        if 'method' not in solver_params:
            raise ValueError("Please specify an optimization method.")
        max_restarts = DEFAULT_MAX_RESTARTS if 'max_restarts' not in solver_params else solver_params["max_restarts"]

        if max_restarts > 1:
            try:
                restart_points = solver_params["restart_points"]
            except KeyError:
                raise KeyError("If requesting more than one restart, you must provide a list of initial points using "
                               "the option 'restart_points'")
        else:
            restart_points = [black_box.get_np_array_initial_values()]

        max_non_improving_restarts = DEFAULT_MAX_NON_IMPROVING_RESTARTS \
            if 'max_non_improving_restarts' not in solver_params else solver_params['max_non_improving_restarts']

        restart = 0
        non_improving = 0

        best_result = None
        best_result_cost = float('Inf')
        if black_box.get_optimization_parameters_upper_bounds_nparray() is None:
            bounds = None
        else:
            bounds: List[Tuple[float, float]] = []
            param_ids = black_box.get_optimization_parameters_ids()
            for param_ind, param_id in enumerate(param_ids):
                bounds += [(black_box.get_optimization_parameter_lower_bound(param_id),
                            black_box.get_optimization_parameter_upper_bound(param_id))]
        jac_method = None
        if 'jac' in solver_params:
            jac_method = solver_params['jac']
        while restart < max_restarts and non_improving < max_non_improving_restarts:
            print("[SciPySolver:solve] Starting restart {}".format(restart))
            x0 = restart_points[restart]
            result = minimize(black_box.evaluate_objective_np_array, x0, args=(),
                              method=solver_params['method'],
                              bounds=bounds,
                              jac=jac_method,
                              options={k: solver_params[k] for k in solver_params if k not in custom_options_names})
            if result['fun'] < best_result_cost:
                best_result = result
                best_result_cost = result['fun']
                non_improving = 0
                print(
                    "[SciPySolver:solve] Restart {} found a new minimum with cost {}".format(restart, best_result_cost))
            else:
                non_improving += 1
                print("[SciPySolver:solve] Restart {} did not find a new minimum".format(restart))
            restart += 1

        if non_improving == max_non_improving_restarts:
            print("[SciPySolver:solve] Reached maximum number of consecutive restarts without improvements. Stopping.")
        print("[SciPySolver:solve] {} restart{} completed".format(restart,
                                                                  "" if restart == 1 else "s"))
        optimal_params = best_result['x']
        f_return = best_result['fun']
        h_return = 0
        nb_evals = best_result['nfev']
        nb_iters = best_result['nit'] if 'nit' in best_result else 1

        return optimal_params, f_return, h_return, nb_evals, nb_iters
