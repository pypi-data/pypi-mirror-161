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

from typing import List, Dict, Callable, Any

from apricopt.solving.blackbox.BlackBox import BlackBox
from apricopt.solving.blackbox.BlackBoxSolver import BlackBoxSolver
import time


def build_bounds_x0_granularity_lists(black_box: BlackBox) -> (list, list, list):
    bb_params_number: int = black_box.get_optimization_parameters_number()
    lower_bounds: List[float] = [0] * bb_params_number
    upper_bounds: List[float] = [0] * bb_params_number
    x0: List[float] = [0] * bb_params_number

    params_ids: List[str] = black_box.get_optimization_parameters_ids()
    params_ids.sort()  # this can be removed, since it is responsibility of the BB to sort the ids

    granularity_string = "("

    for p_idx in range(bb_params_number):
        lower_bounds[p_idx] = black_box.get_optimization_parameter_lower_bound(params_ids[p_idx])
        upper_bounds[p_idx] = black_box.get_optimization_parameter_upper_bound(params_ids[p_idx])
        x0[p_idx] = black_box.get_optimization_parameter_initial_value(params_ids[p_idx])
        granularity_string += " " + str(black_box.get_optimization_parameter_granularity(params_ids[p_idx]))

    granularity_string += ")"

    return lower_bounds, upper_bounds, x0, granularity_string


def build_output_type_string(black_box: BlackBox) -> str:
    obj = "OBJ"
    eb = " ".join(["EB"] * black_box.get_extreme_barrier_constraints_number())
    pb = " ".join(["PB"] * black_box.get_progressive_barrier_constraints_number())
    return f"{obj} {eb} {pb}"


def build_params_value_dict(black_box: BlackBox, eval_point) -> Dict[str, float]:
    """

    :param black_box:
    :param eval_point: an instance of PyNomad.PyNomadEvalPoint
    :return:
    """
    import PyNomad
    params_values: List[float] = [eval_point.get_coord(i) for i in range(eval_point.size())]
    return build_params_value_dict_from_list(black_box, params_values)


def build_params_value_dict_from_list(black_box: BlackBox, params_values: List[float]) -> Dict[str, float]:
    params_ids: List[str] = black_box.get_optimization_parameters_ids()
    params_ids.sort()  # should be removed

    values_dict: Dict[str, float] = dict()

    for idx in range(len(params_ids)):
        values_dict[params_ids[idx]] = params_values[idx]

    return values_dict


def build_output_string(black_box: BlackBox, sim_output: Dict[str, float]) -> str:
    obj = str(sim_output[black_box.get_objective_id()])

    progressive_constraints_str: str = build_constraints_values_string(
        black_box.get_progressive_barrier_constraints_ids(),
        sim_output)

    extreme_constraints_str: str = build_constraints_values_string(black_box.get_extreme_barrier_constraints_ids(),
                                                                   sim_output)

    return f"{obj} {extreme_constraints_str} {progressive_constraints_str}"


def build_constraints_values_string(constraints_ids: List[str],
                                    sim_output: Dict[str, float]) -> str:
    c: List[str] = list()
    for idx in range(len(constraints_ids)):
        c.append(str(sim_output[constraints_ids[idx]]))
    constraints_string: str = " ".join(c)
    return constraints_string


class NOMADSolver(BlackBoxSolver):

    def __init__(self):
        super().__init__()

    def build_bb_function(self, black_box: BlackBox, print_bb_evals: bool) -> Callable:
        def bb(x, dict_given=False) -> int:

            eval_ok = 1
            sim_output: Dict[str, float]
            try:
                if not dict_given:
                    params_values_dict = build_params_value_dict(black_box, x)
                else:
                    params_values_dict = x

                if print_bb_evals: print(f"\nTrying with params: {params_values_dict}")
                sim_output = black_box.evaluate(params_values_dict)

                line: str

                for extreme_barrier_constraint_id in black_box.get_extreme_barrier_constraints_ids():
                    line = f"\tExtreme barrier constraint '{extreme_barrier_constraint_id}' value: " \
                           f"{sim_output[extreme_barrier_constraint_id]}"
                    if print_bb_evals:
                        print(line, flush=True)

                for progressive_barrier_constraint_id in black_box.get_progressive_barrier_constraints_ids():
                    line = f"\tProgressive barrier constraint '{progressive_barrier_constraint_id}' value: " \
                           f"{sim_output[progressive_barrier_constraint_id]}"
                    if print_bb_evals:
                        print(line, flush=True)

                line = f"\tObjective value: {sim_output[black_box.get_objective_id()]}"
                if print_bb_evals:
                    print(line, flush=True)

                output_string: str = build_output_string(black_box, sim_output)
                x.setBBO(output_string
                         .encode("UTF-8"))

            except Exception as e:
                eval_ok = 0
                sim_output = {}
                print(e)

            if eval_ok == 1:
                self.execution_info(black_box, sim_output)

            return eval_ok

        return bb

    def initialize_storage(self, black_box: BlackBox) -> None:
        super().initialize_storage(black_box)
        self.set_start_time(time.perf_counter())

    def execution_info(self, black_box: BlackBox, sim_output: Dict[str, float]):
        line: str
        extreme_barrier_violated: bool = False
        for extreme_barrier_constraint_id in black_box.get_extreme_barrier_constraints_ids():
            value: float = sim_output[extreme_barrier_constraint_id]
            self.add_extreme_barrier_constraint_value(extreme_barrier_constraint_id, value)
            if value > 0:
                extreme_barrier_violated = True
            line = f"\tExtreme barrier constraint '{extreme_barrier_constraint_id}' value: " \
                   f"{value}"
            self.log.append(line)
        if not extreme_barrier_violated:
            for progressive_barrier_constraint_id in black_box.get_progressive_barrier_constraints_ids():
                value: float = sim_output[progressive_barrier_constraint_id]
                self.add_progressive_barrier_constraint_value(progressive_barrier_constraint_id, value)
                line = f"\tProgressive barrier constraint '{progressive_barrier_constraint_id}' value: " \
                       f"{value}"
                self.log.append(line)

            self.add_objective_value(sim_output[black_box.get_objective_id()])

        self.times.append(time.perf_counter() - self.start_time)

    def solve(self, black_box: BlackBox, solver_params: Dict[str, Any], print_bb_evals=False) -> (Dict[str, float], float, float):
        import PyNomad
        lower_bounds, upper_bounds, x0, granularity_string = build_bounds_x0_granularity_lists(black_box)
        output_type_string = build_output_type_string(black_box)

        black_box_function = self.build_bb_function(black_box, print_bb_evals)

        solve_parameters = [] if "solver_params" not in solver_params else solver_params["solver_params"][:]
        solve_parameters.append(f"BB_OUTPUT_TYPE {output_type_string}")
        solve_parameters.append(" GRANULARITY " + granularity_string)

        print(f"NOMAD parameters: {solve_parameters}", flush=True)

        self.initialize_storage(black_box)

        try:
            #[x_return, f_return, h_return, nb_evals, nb_iters, stopflag] = \
            result = PyNomad.optimize(black_box_function, x0, lower_bounds, upper_bounds, solve_parameters)
            optimal_params = build_params_value_dict_from_list(black_box, result['x_best'])

            black_box.finalize()

            return optimal_params, result['f_best'], result['h_best'], result['nb_evals'], result['nb_iters']
        except Exception as exc:
            print("There was an error invoking the solver:")
            print(exc)
            exit(1)
