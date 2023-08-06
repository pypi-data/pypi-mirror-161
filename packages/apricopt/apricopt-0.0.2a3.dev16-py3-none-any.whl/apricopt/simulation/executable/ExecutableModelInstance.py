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

Copyright (C) 2020-2022 Sapienza University of Rome, Marco Esposito, Leonardo Picchiami.
"""

from apricopt.model.ModelInstance import ModelInstance

from typing import Dict


class ExecutableModelInstance(ModelInstance):
    def __init__(self, sim_engine, model_obj):
        super().__init__(model_obj)
        self.sim_engine = sim_engine

        self.abs_tol = -1
        self.rel_tol = -1
        self.step_size = -1
        self.duration = -1

    def set_parameters(self, params_values: Dict[str, float]) -> None:
        self.sim_engine.write_simulation_input(params_values)

    def set_parameter(self, param_name: str, value: float) -> None:
        raise NotImplementedError

    def get_parameters_initial_values(self) -> Dict[str, float]:
        return dict()

    def get_compartment_initial_volumes(self) -> Dict[str, float]:
        return dict()

    def set_simulation_configuration(self, abs_tol: float, rel_tol: float, step_size: float) -> None:
        self.abs_tol = abs_tol
        self.rel_tol = rel_tol
        self.step_size = step_size

    def set_simulation_duration(self, duration: float) -> None:
        self.duration = duration

    def set_simulation_duration_with_step_size(self, horizon, time_step):
        self.duration = horizon
        self.step_size = time_step