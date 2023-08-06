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

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Set

from apricopt.model.Model import Model
from apricopt.model.ModelInstance import ModelInstance
from apricopt.model.Observable import Observable


class SimulationEngine(ABC):

    def __init__(self):
        pass

    def simulate(self, model: Model, horizon: float) -> Dict[str, float]:
        trajectory: Dict[str, List[float]] = self.simulate_trajectory(model, horizon)
        result = model.evaluate_constraints(trajectory)
        return result

    def simulate_and_set(self, model: Model, horizon: float, exclude=None, evaluate_constraints=True) -> Dict[str, float]:
        if exclude is None:
            exclude = []
        trajectory = self.simulate_trajectory_and_set(model, horizon, exclude=exclude)

        if evaluate_constraints:
            result = model.evaluate_constraints(trajectory)
        else:
            result = None
        return result

    def simulate_for_initialisation(self, model: Model, horizon: float, initialization_constraints: Set[Observable]) \
            -> (bool, float, Dict[str, List[float]]):
        trajectory: Dict[str, List[float]] = self.simulate_trajectory(model, horizon)
        trajectory_length = len(trajectory['time'])
        init_time_idx = 0
        for obs in initialization_constraints:
            # init_value = next((v for v in trajectory[obs.id] if v <= 0), None)
            obs_init_time_idx: int = model.compute_first_satisfaction_index(obs, trajectory)
            if obs_init_time_idx == trajectory_length:
                return False, trajectory_length, dict()
            init_time_idx = max(init_time_idx, obs_init_time_idx)

        trajectory_up_to_init = dict()
        for obs_id, obs_traj in trajectory.items():
            # returns the trajectory up to the moment when the model is initialized
            trajectory_up_to_init[obs_id] = obs_traj[:init_time_idx]

        return True, trajectory['time'][init_time_idx], trajectory_up_to_init

    @abstractmethod
    def load_model(self, model_filename: str, **kwargs) -> ModelInstance:
        pass

    @abstractmethod
    def simulate_trajectory(self, model: Model, horizon: float) -> Dict[str, List[float]]:
        pass

    @abstractmethod
    def simulate_trajectory_and_set(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        pass

    @abstractmethod
    def simulate_trajectory_and_get_state(self, model: Model, horizon: float, exclude=None) -> Dict[str, float]:
        pass

    @abstractmethod
    def restore_state(self, model: Model, changed_values: dict) -> None:
        pass

    @abstractmethod
    def model_instance_class(self) -> Type[ModelInstance]:
        pass
