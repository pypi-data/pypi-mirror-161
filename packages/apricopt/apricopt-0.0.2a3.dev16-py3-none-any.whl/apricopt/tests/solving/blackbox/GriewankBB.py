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
import random
from typing import List, Dict

from apricopt.solving.blackbox.BlackBox import BlackBox


class TestBlackBox(BlackBox):

    def __init__(self, dimensions: int):
        self.d: int = dimensions

    def evaluate(self, parameters: Dict[str, float]) -> Dict[str, float]:
        """
        Implements the Griewank Function, as shown in https://www.sfu.ca/~ssurjano/griewank.html
        :param parameters:
        :return:
        """
        if len(parameters) != self.d:
            raise ValueError

        xx = []
        for i in range(self.d):
            xx.append(parameters[str(i)])
        s = 0
        p = 1
        for ii in range(self.d):
            xi = xx[ii]
            s += xi ** 2 / 4000
            p *= math.cos(xi / math.sqrt(ii + 1))

        result = s - p + 1
        div7 = result % 7.0
        div6 = result % 6.0

        return {"result": result,
                "dummy_extreme_constraint": -div7 if div7 > 0 else 1,
                "dummy_progressive_constraint": -div6 if div6 > 0 else 1}

    def evaluate_and_set_state(self, parameters: Dict[str, float]) -> Dict[str, float]:
        pass

    def set_fixed_parameters(self, params: Dict[str, float]) -> None:
        pass

    def set_optimization_parameters(self, params: Dict[str, float]) -> None:
        pass

    def get_optimization_parameters_number(self) -> int:
        return self.d

    def get_optimization_parameters_ids(self) -> List[str]:
        return [str(i) for i in range(self.d)]

    def get_optimization_parameter_lower_bound(self, param_id) -> float:
        return -600

    def get_optimization_parameter_upper_bound(self, param_id) -> float:
        return 600

    def get_optimization_parameter_initial_value(self, param_id) -> float:
        return random.randint(-600, 600)

    def get_optimization_parameter_granularity(self, param_id) -> float:
        return 0

    def get_extreme_barrier_constraints_number(self) -> int:
        return 1

    def get_progressive_barrier_constraints_number(self) -> int:
        return 1

    def get_extreme_barrier_constraints_ids(self) -> List[str]:
        return ["dummy_extreme_constraint"]

    def get_progressive_barrier_constraints_ids(self) -> List[str]:
        return ["dummy_progressive_constraint"]

    def get_objective_id(self) -> str:
        return "result"

    def get_objective_upper_bound(self):
        return float('Inf')

    @staticmethod
    def get_raisable_exception_type():
        return ValueError

    def set_optimization_parameters_initial_values(self, param_values: Dict[str, float]) -> None:
        pass

    def finalize(self) -> None:
        pass
