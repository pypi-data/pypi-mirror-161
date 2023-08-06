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

from typing import Type, Dict, List

from apricopt.model.Model import Model
from apricopt.model.ModelInstance import ModelInstance
from apricopt.simulation.SimulationEngine import SimulationEngine

import roadrunner
from roadrunner import RoadRunner
import numpy as np

from apricopt.simulation.roadrunner.RoadRunnerModelInstance import RoadRunnerModelInstance


class RoadRunnerEngine(SimulationEngine):

    def __init__(self):
        super().__init__()

    def load_model(self, model_filename: str, **exec_info) -> ModelInstance:
        model_obj: RoadRunner = roadrunner.RoadRunner(model_filename)
        return RoadRunnerModelInstance(model_obj)

    def simulate_trajectory(self, model: Model, horizon: float) -> Dict[str, List[float]]:
        sim_output = self._run_simulation_task(model, horizon)
        model_obj: RoadRunner = model.instance.model_obj
        model_obj.resetAll()
        return sim_output

    def simulate_trajectory_and_set(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        model_obj: RoadRunner = model.instance.model_obj
        observed_outputs = model_obj.model.getFloatingSpeciesIds() + \
                           model_obj.model.getGlobalParameterIds() + \
                           model_obj.model.getCompartmentIds()

        sim_output = self._run_simulation_task(model, horizon, observed_outputs)
        exclude_from_set = self._exclude_from_simulate_and_set(model, exclude)

        changed_values: Dict[str, List[float]] = dict()
        for out_id, traj in sim_output.items():
            if out_id == 'time':
                changed_values['time'] = traj
                continue

            if out_id not in exclude_from_set:
                changed_values[out_id] = traj
                model_obj.model[f'init({out_id})'] = traj[-1]

        model_obj.resetAll()
        return changed_values

    def simulate_trajectory_and_get_state(self, model: Model, horizon: float, exclude=None) -> Dict[str, float]:
        model_obj: RoadRunner = model.instance.model_obj
        observed_outputs = model_obj.model.getFloatingSpeciesIds() + \
                           model_obj.model.getGlobalParameterIds() + \
                           model_obj.model.getCompartmentIds()

        sim_output = self._run_simulation_task(model, horizon, observed_outputs)
        exclude_from_set = self._exclude_from_simulate_and_set(model, exclude)
        changed_values: Dict[str, float] = dict()
        for out_id, traj in sim_output.items():
            if out_id == 'time':
                continue

            if out_id not in exclude_from_set:
                changed_values[out_id] = traj[-1]

        model_obj.resetAll()
        return changed_values

    def restore_state(self, model: Model, changed_values: Dict[str, float]) -> None:
        model_obj: RoadRunner = model.instance.model_obj
        for var_id, state_value in changed_values.items():
            model_obj[f'init({var_id})'] = state_value
        model_obj.resetAll()

    def model_instance_class(self) -> Type[ModelInstance]:
        return RoadRunnerModelInstance

    def _exclude_from_simulate_and_set(self, model: Model, exclude: List[str] = None) -> List[str]:
        model_obj = model.instance.model_obj

        init_exclude: List[str] = []
        if exclude:
            init_exclude = list(exclude)

        for init_ass in model_obj.getInitialAssignmentIds():
            if init_ass not in init_exclude:
                init_exclude.append(init_ass)

        for ass in model_obj.getAssignmentRuleIds():
            if ass not in init_exclude:
                init_exclude.append(ass)
        return init_exclude

    def _get_simulation_output(self, model: Model, time_series: np.ndarray, observed) -> Dict[str, List[float]]:
        if not isinstance(model.instance, RoadRunnerModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'RoadRunnerEngine::simulate_trajectory' method must have type 'RoadRunnerModelInstance'.")
        sim_output: Dict[str, List[float]] = dict()
        sim_output['time'] = time_series[:, 0]
        for i in range(1, len(observed)):
            sim_output[observed[i]] = list(time_series[:, i])

        return sim_output

    def _run_simulation_task(self, model: Model, horizon: float, observed_outputs=None) -> np.ndarray:
        if not isinstance(model.instance, RoadRunnerModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'RoadRunnerEngine::simulate_trajectory' method must have type 'RoadRunnerModelInstance'.")
        model_obj: RoadRunner = model.instance.model_obj
        if model.instance.time_step == -1:
            raise RuntimeError("The time step must be set before running the simulation.")
        observed: List[str]

        if observed_outputs:
            observed = observed_outputs
        elif model.observed_outputs:
            observed = model.observed_outputs
        else:
            observed = model_obj.model.getFloatingSpeciesIds()

        time_observation = None
        for observation in observed:
            if observation.lower() == 'time':
                time_observation = observation

        if time_observation:
            observed.remove(time_observation)

        observed = ['time'] + observed
        model_obj.timeCourseSelections = observed
        trajectory = model_obj.simulate(0, horizon, steps=int(horizon / model.instance.time_step))
        return self._get_simulation_output(model, trajectory, observed)
