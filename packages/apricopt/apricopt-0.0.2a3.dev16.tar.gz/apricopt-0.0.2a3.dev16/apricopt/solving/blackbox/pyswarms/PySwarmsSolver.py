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
from typing import Dict, Any

from apricopt.solving.blackbox.BlackBox import BlackBox
from apricopt.solving.blackbox.BlackBoxSolver import BlackBoxSolver
import numpy as np

DEFAULT_N_PARTICLES = 10
DEFAULT_ITERATIONS = 1000
DEFAULT_SEARCH_N_PARTICLES = 10
DEFAULT_SEARCH_ITERATIONS = 10
DEFAULT_SEARCH_N_SELECTION_ITERS = 100

def random_search(black_box: BlackBox, n_particles=10, iters=10, n_selection_iters=100):
    print("Starting random search for hyperparameter optimization")
    from pyswarms.utils.search.random_search import RandomSearch
    from pyswarms.single.global_best import GlobalBestPSO
    options = {'c1': [1, 5],
               'c2': [1, 10],
               'w': [2, 5],
               'p': [1, 2],
               'k': [3, 10]}
    g = RandomSearch(GlobalBestPSO, n_particles=n_particles, dimensions=black_box.get_optimization_parameters_number(),
                     options=options, objective_func=black_box.evaluate_objective_multiple_inputs_np_array,
                     iters=iters, n_selection_iters=n_selection_iters, bounds=(black_box.get_optimization_parameters_lower_bounds_nparray(),
                  black_box.get_optimization_parameters_upper_bounds_nparray()))
    best_score, best_options = g.search()
    return best_options


class PySwarmsSolver(BlackBoxSolver):
    def solve(self, black_box: BlackBox, solver_params: Dict[str, Any]) -> (
            Dict[str, float], float, float, float, float):
        import pyswarms as ps
        n_particles = DEFAULT_N_PARTICLES if "n_particles" not in solver_params else solver_params["n_particles"]
        iterations = DEFAULT_ITERATIONS if "iterations" not in solver_params else solver_params["iterations"]

        bounds = (black_box.get_optimization_parameters_lower_bounds_nparray(),
                  black_box.get_optimization_parameters_upper_bounds_nparray())

        if "init_pos" in solver_params.keys():
            inits = solver_params['init_pos']
            init_list = []
            for start in inits:
                init_list.append(
                    [start[param] for param in black_box.get_optimization_parameters_ids()]
                )
            init_pos = np.asarray(init_list, dtype=np.double)

        else:
            init_pos = None

        # Perform hyperparameter optimization if requested, via random search
        if "search" in solver_params and solver_params["search"]:
            search_n_particles = DEFAULT_SEARCH_N_PARTICLES if "search_n_particles" not in solver_params \
                else solver_params["search_n_particles"]
            search_iters = DEFAULT_SEARCH_ITERATIONS if "search_iters" not in solver_params \
                else solver_params["search_iters"]
            search_n_selection_iters = DEFAULT_SEARCH_N_SELECTION_ITERS if \
                "search_n_selection_iters" not in solver_params else solver_params["search_n_selection_iters"]

            options = random_search(black_box, n_particles=search_n_particles, iters=search_iters,
                                    n_selection_iters=search_n_selection_iters)
        else:
            options = solver_params



        optimizer = ps.single.GlobalBestPSO(
            n_particles=n_particles,
            dimensions=black_box.get_optimization_parameters_number(),
            options=options,
            bounds=bounds,
            init_pos=init_pos)

        # Avoids checking whether the variables are inside their bounds at each evaluation of the black-box
        kwargs = {"check_input": False}

        # Perform optimization
        cost, best_x = optimizer.optimize(black_box.evaluate_objective_multiple_inputs_np_array,
                                          iters=iterations, **kwargs)

        optimal_params = best_x
        f_return = cost
        h_return = 0
        nb_evals = iterations * n_particles
        nb_iters = iterations

        return optimal_params, f_return, h_return, nb_evals, nb_iters
