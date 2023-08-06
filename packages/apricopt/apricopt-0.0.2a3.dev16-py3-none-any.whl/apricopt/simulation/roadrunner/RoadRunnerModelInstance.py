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

from apricopt.model.ModelInstance import ModelInstance
from roadrunner import RoadRunner, ExecutableModel



class RoadRunnerModelInstance(ModelInstance):

    def __init__(self, model_obj: RoadRunner):
        super().__init__(model_obj)
        self.time_step = -1
        self.horizon = -1

    def __delete__(self, instance):
        model_obj: RoadRunner = self.model_obj
        del model_obj

    def set_parameter(self, param_name: str, value: float) -> None:
        model_obj: RoadRunner = self.model_obj
        model_obj.model[f'init({param_name})'] = value
        model_obj.resetAll()

    def set_parameters(self, params_values: Dict[str, float]) -> None:
        model_obj: RoadRunner = self.model_obj
        for param_id, value in params_values.items():
            model_obj.model[f'init({param_id})'] = value
        model_obj.resetAll()

    def get_parameters_initial_values(self) -> Dict[str, float]:
        values: Dict[str, float] = dict()
        model_obj: RoadRunner = self.model_obj
        ex_model: ExecutableModel = model_obj.model
        params_ids = ex_model.getGlobalParameterIds()
        for i in range(len(params_ids)):
            values[params_ids[i]] = ex_model['init('+params_ids[i]+')']
        return values

    def get_compartment_initial_volumes(self) -> Dict[str, float]:
        values: Dict[str, float] = dict()
        model_obj: RoadRunner = self.model_obj
        ex_model: ExecutableModel = model_obj.model
        ids = ex_model.getCompartmentIds()
        init_volumes = ex_model.getCompartmentInitVolumes()
        for i in range(len(ids)):
            values[ids[i]] = init_volumes[i]
        return values

    def set_simulation_configuration(self, abs_tol: float, rel_tol: float, step_size: float) -> None:
        self.model_obj.integrator.stiff = True
        self.model_obj.integrator.initial_time_step = 0
        self.model_obj.integrator.absolute_tolerance = abs_tol
        self.model_obj.integrator.relative_tolerance = rel_tol
        self.time_step = step_size

    def set_simulation_duration(self, duration: float) -> None:
        self.horizon = duration

    def set_simulation_duration_with_step_size(self, horizon, time_step):
        self.set_simulation_duration(horizon)
        self.time_step = time_step
