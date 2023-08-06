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
from typing import List, Dict

import numpy as np

from apricopt.model.Model import Model
from apricopt.simulation.SimulationEngine import SimulationEngine
from apricopt.solving.blackbox.BlackBox import BlackBox


class SimulableModelBlackBox(BlackBox):

    def __init__(self, sim_engine: SimulationEngine, model: Model, horizon: float):
        if sim_engine.model_instance_class() != model.instance.__class__:
            raise TypeError("The provided SimulationEngine object must be able to simulate the model.")
        self.sim_engine = sim_engine
        self.model = model
        self.horizon = horizon
        self.param_ids = None
        self.eb_constraint_ids = None
        self.pb_constraint_ids = None

    def evaluate(self, parameters: Dict[str, float], check_input=True) -> Dict[str, float]:
        # ME: Force parameters within bounds
        for p_id, p_value in parameters.items():
            if p_value < self.get_optimization_parameter_lower_bound(p_id):
                parameters[p_id] = self.get_optimization_parameter_lower_bound(p_id)
            elif p_value > self.get_optimization_parameter_upper_bound(p_id):
                parameters[p_id] = self.get_optimization_parameter_upper_bound(p_id)
        # Set parameters in the model
        self.model.set_params(parameters)
        # Simulate the model using its simulation engine
        trajectory = self.sim_engine.simulate_trajectory(self.model, self.horizon)

        # Extract the results from the trajectory produced by the simulator
        result: Dict[str, float] = dict()

        result[self.get_objective_id()] = trajectory[self.get_objective_id()][-1]
        for ebc_id in self.get_extreme_barrier_constraints_ids():
            result[ebc_id] = trajectory[ebc_id][-1]
        for pbc_id in self.get_progressive_barrier_constraints_ids():
            result[pbc_id] = trajectory[pbc_id][-1]
        return result

    def evaluate_np_array(self, params: np.array, check_input=False) -> Dict[str, float]:
        param_dict: Dict[str, float] = dict()
        params_ids = self.get_optimization_parameters_ids()
        for i in range(len(params_ids)):
            param_dict[params_ids[i]] = params[i]
        return self.evaluate(param_dict)

    def evaluate_objective_np_array(self, params: np.array, check_input=False) -> float:
        param_dict: Dict[str, float] = dict()
        params_ids = self.get_optimization_parameters_ids()
        for i in range(len(params_ids)):
            param_dict[params_ids[i]] = params[i]
        return self.evaluate_objective(param_dict)

    def is_input_valid(self, parameters: Dict[str, float]) -> bool:
        return True

    def get_optimization_parameters_number(self) -> int:
        return len(self.model.parameters)

    def get_optimization_parameters_ids(self) -> List[str]:
        if not self.param_ids:
            p_ids = [param.id for param in self.model.parameters.values()]
            p_ids.sort()
            self.param_ids = p_ids
        return self.param_ids

    def get_optimization_parameter_lower_bound(self, param_id) -> float:
        return self.model.parameters[param_id].lower_bound

    def get_optimization_parameter_upper_bound(self, param_id) -> float:
        return self.model.parameters[param_id].upper_bound

    def get_optimization_parameters_lower_bounds_nparray(self) -> np.array:
        lb = []
        for param_id in self.get_optimization_parameters_ids():
            lb += [self.model.parameters[param_id].lower_bound]
        return np.array(lb)

    def get_optimization_parameters_upper_bounds_nparray(self) -> np.array:
        ub = []
        for param_id in self.get_optimization_parameters_ids():
            ub += [self.model.parameters[param_id].upper_bound]
        return np.array(ub)

    def get_optimization_parameter_initial_value(self, param_id) -> float:
        return self.model.parameters[param_id].nominal_value

    # TODO implement caching
    def get_optimization_parameters_initial_values(self) -> np.array:
        res: Dict[str, float] = dict()
        for param_id in self.get_optimization_parameters_ids():
            res[param_id] = self.model.parameters[param_id].nominal_value
        return res

    def get_optimization_parameters_initial_values_np_array(self) -> np.array:
        nv = []
        for param_id in self.get_optimization_parameters_ids():
            nv += [self.model.parameters[param_id].nominal_value]
        return np.array(nv)

    def set_optimization_parameters_initial_values(self, param_values: Dict[str, float]) -> None:
        self.model.set_parameters_nominal_values(param_values)

    def get_optimization_parameter_granularity(self, param_id) -> float:
        return self.model.parameters[param_id].granularity

    def get_extreme_barrier_constraints_number(self) -> int:
        return len(self.model.fast_constraints)

    def get_progressive_barrier_constraints_number(self) -> int:
        return len(self.model.constraints)

    def get_extreme_barrier_constraints_ids(self) -> List[str]:
        if not self.eb_constraint_ids:
            c_ids = [constraint.id for constraint in self.model.fast_constraints]
            c_ids.sort()
            self.eb_constraint_ids = c_ids
        return self.eb_constraint_ids

    def get_progressive_barrier_constraints_ids(self) -> List[str]:
        if not self.pb_constraint_ids:
            c_ids = [constraint.id for constraint in self.model.constraints]
            c_ids.sort()
            self.pb_constraint_ids = c_ids
        return self.pb_constraint_ids

    def get_objective_id(self) -> str:
        return self.model.objective.id

    def get_objective_upper_bound(self) -> float:
        return self.model.objective.upper_bound

    @staticmethod
    def get_raisable_exception_type():
        return TypeError

    def finalize(self) -> None:
        pass
