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

from typing import Dict, List, Type

from apricopt.model.Model import Model
from apricopt.model.ModelInstance import ModelInstance
from apricopt.simulation.MockUp.MockUpModelInstance import MockUpModelInstance
from apricopt.simulation.SimulationEngine import SimulationEngine

import random


class MockUpSimulationEngine(SimulationEngine):

    def __init__(self):
        super().__init__()

    def load_model(self, model_filename: str) -> ModelInstance:
        return MockUpModelInstance(model_filename)

    def simulate_trajectory(self, model: Model, horizon: float) -> Dict[str, List[float]]:
        return {"time": list(range(int(horizon))),
                "output": [random.random() for _ in range(int(horizon))]}

    def simulate_trajectory_and_set(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        return self.simulate_trajectory(model, horizon)

    def model_instance_class(self) -> Type[ModelInstance]:
        return MockUpModelInstance

    def simulate_trajectory_and_get_state(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        return self.simulate_trajectory(model, horizon)

    def restore_state(self, model: Model, changed_values: dict) -> None:
        pass
