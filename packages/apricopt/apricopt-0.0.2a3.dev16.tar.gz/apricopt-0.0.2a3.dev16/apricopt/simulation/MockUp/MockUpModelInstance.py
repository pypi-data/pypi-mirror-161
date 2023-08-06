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

Copyright (C) 2020 Marco Esposito, Leonardo Picchiami.
"""

from typing import Dict
from apricopt.model.ModelInstance import ModelInstance


class MockUpModelInstance(ModelInstance):

    def __init__(self, model_obj):
        super().__init__(model_obj)

    def set_parameter(self, param_name: str, value: float) -> None:
        pass

    def set_parameters(self, params_values: Dict[str, float]) -> None:
        pass

    def get_parameters_initial_values(self) -> Dict[str, float]:
        return {"parameter": 0.5}

    def get_compartment_initial_volumes(self) -> Dict[str, float]:
        return dict()

    def set_simulation_configuration(self, abs_tol: float, rel_tol: float, step_size: float) -> None:
        pass

    def set_simulation_duration(self, duration: float) -> None:
        pass

    def set_simulation_duration_with_step_size(self, horizon, time_step):
        pass