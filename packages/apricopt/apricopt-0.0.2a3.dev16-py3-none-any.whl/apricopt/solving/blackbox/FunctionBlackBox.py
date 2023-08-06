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
from typing import List, Dict, Callable

import numpy as np
from apricopt.solving.blackbox.BlackBox import BlackBox


class FunctionBlackBox(BlackBox):

    def __init__(self, dimension: int, function: Callable,
                 lower_bounds=None, upper_bounds=None):
        """

        :param function: A multivariate real function that takes a list of float and returns a float
        :param lower_bounds: A list of float such that the i-th element is the lower bound of the i-th variable
        :param upper_bounds: A list of float such that the i-th element is the upper bound of the i-th variable
        """
        self.d: int = dimension

        if lower_bounds is None:
            self.lower_bounds: List[float] = [float("-Inf") for _ in range(self.d)]
        else:
            if len(lower_bounds) != self.d:
                raise ValueError("The length of the lower bounds list must be equal to the dimension of the black box")
            self.lower_bounds = lower_bounds

        if upper_bounds is None:
            self.upper_bounds: List[float] = [float("Inf") for _ in range(self.d)]
        else:
            if len(lower_bounds) != self.d:
                raise ValueError("The length of the upprt bounds list must be equal to the dimension of the black box")
            self.upper_bounds = upper_bounds

        if len(self.lower_bounds) != len(self.upper_bounds):
            raise ValueError("The length of the lower bounds list must be equal to the length of the upper bounds list")

        for i in range(self.d):
            if self.lower_bounds[i] >= self.upper_bounds[i]:
                raise ValueError(f"The lower bound of the variable with index {i} is larger than the upper bound")

        self.function = function
        self._total_evaluations: int = 0
        self.parameters_ids: List[str] = []


    def is_input_valid(self, parameters: Dict[str, float]) -> bool:
        """

        :param parameters:
        :return:
        """
        try:
            if len(parameters) != self.d:
                return False
            low_ok: bool = all((parameters[x] >= self.lower_bounds[int(x)] for x in parameters.keys()))
            up_ok: bool = all((parameters[x] <= self.upper_bounds[int(x)] for x in parameters.keys()))
            return low_ok and up_ok
        except Exception as e:
            raise e

    def is_input_valid_array(self, parameters_array) -> bool:
        """

        :param parameters_array:
        :return:
        """
        param_ids = self.get_optimization_parameters_ids()
        parameters = {param_ids[i]: parameters_array[i] for i in range(len(parameters_array))}
        try:
            if len(parameters) != self.d:
                return False
            low_ok: bool = all((parameters[x] >= self.lower_bounds[int(x)] for x in parameters.keys()))
            up_ok: bool = all((parameters[x] <= self.upper_bounds[int(x)] for x in parameters.keys()))
            return low_ok and up_ok
        except Exception as e:
            raise e

    def evaluate(self, parameters: Dict[str, float], check_input=True) -> Dict[str, float]:
        """

        :param check_input:
        :param parameters:
        :return:
        """
        if check_input and not self.is_input_valid(parameters):
            raise ValueError("The provided input is not valid.")

        x = []
        for i in range(self.d):
            x.append(parameters[str(i)])

        self._total_evaluations += 1
        return {self.get_objective_id(): self.function(x)}

    def evaluate_np_array(self, parameters: np.array, check_input=False) -> Dict[str, float]:
        """

        :param check_input:
        :param parameters:
        :return:
        """
        if check_input and not self.is_input_valid_array(parameters):
            raise ValueError("The provided input is not valid.")
        self._total_evaluations += 1
        return {self.get_objective_id(): self.function(parameters)}

    def evaluate_objective_np_array(self, parameters: np.array, check_input=False) -> float:
        # param_ids = self.get_optimization_parameters_ids()
        # params = {param_ids[i]: parameters[i] for i in range(len(parameters))}
        if check_input and not self.is_input_valid_array(parameters):
            raise ValueError("The provided input is not valid.")
        self._total_evaluations += 1
        return self.function(parameters)
        # return self.evaluate(params, check_input)[self.get_objective_id()]

    def evaluate_objective_multiple_inputs_np_array(self, parameters_list: np.ndarray, check_input=False) \
            -> List[float]:
        results: List[float] = [0] * len(parameters_list)
        for i in range(len(parameters_list)):
            results[i] = self.evaluate_objective_np_array(parameters_list[i].tolist(), check_input)

        # results = self.function(parameters_list)
        return results

    def get_total_evaluations(self):
        return self._total_evaluations

    def get_optimization_parameters_number(self) -> int:
        return self.d

    def get_optimization_parameters_ids(self) -> List[str]:
        if not self.parameters_ids:
            self.parameters_ids = [str(i) for i in range(self.d)]
        return self.parameters_ids

    def get_optimization_parameter_lower_bound(self, param_id) -> float:
        return self.lower_bounds[int(param_id)]

    def get_optimization_parameter_upper_bound(self, param_id) -> float:
        return self.upper_bounds[int(param_id)]

    def get_optimization_parameters_lower_bounds_nparray(self) -> np.array:
        return np.array([self.get_optimization_parameter_lower_bound(p_id)
                         for p_id in self.get_optimization_parameters_ids()])

    def get_optimization_parameters_upper_bounds_nparray(self) -> np.array:
        return np.array([self.get_optimization_parameter_upper_bound(p_id)
                         for p_id in self.get_optimization_parameters_ids()])

    def get_optimization_parameter_initial_value(self, param_id) -> float:
        return random_in_range(self.get_optimization_parameter_lower_bound(param_id),
                               self.get_optimization_parameter_upper_bound(param_id))

    def get_random_optimization_parameters_initial_values(self) -> Dict[str, float]:
        return {param_id: random_in_range(self.get_optimization_parameter_lower_bound(param_id),
                                          self.get_optimization_parameter_upper_bound(param_id))
                for param_id in self.get_optimization_parameters_ids()}

    def get_random_initial_values_np_array(self) -> np.array:
        return np.array([random_in_range(self.get_optimization_parameter_lower_bound(param_id),
                                         self.get_optimization_parameter_upper_bound(param_id))
                         for param_id in self.get_optimization_parameters_ids()])

    def set_optimization_parameters_initial_values(self, param_values: Dict[str, float]) -> None:
        pass

    def get_optimization_parameter_granularity(self, param_id) -> float:
        return 0

    def get_extreme_barrier_constraints_number(self) -> int:
        return 0

    def get_progressive_barrier_constraints_number(self) -> int:
        return 0

    def get_extreme_barrier_constraints_ids(self) -> List[str]:
        return []

    def get_progressive_barrier_constraints_ids(self) -> List[str]:
        return []

    def get_objective_id(self) -> str:
        return "result"

    def get_objective_upper_bound(self) -> float:
        return float('Inf')

    @staticmethod
    def get_raisable_exception_type():
        return ValueError

    def finalize(self) -> None:
        pass


def random_in_range(lower_bound: float, upper_bound: float) -> float:
    """
    Returns a pseudo-random number in the given interval
    Restituisce un numero reale (pseudo-)casuale nell'intervallo dato
    :param lower_bound: the lower bound of the interval
    :param upper_bound: the upper bound of the interval
    :return: a random flaot c such that lower_bound <= c <= upper_bound
    """
    lb = 0 if lower_bound == float("-Inf") else lower_bound
    ub = 1 if upper_bound == float("Inf") else upper_bound
    return lb + random.random() * (ub - lb)
