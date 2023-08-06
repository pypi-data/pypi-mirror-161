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

Copyright (C) 2020-2022 Marco Esposito, Leonardo Picchiami.
"""

from apricopt.model.Model import Model
from apricopt.simulation.SimulationEngine import SimulationEngine
from apricopt.model.ModelInstance import ModelInstance
from apricopt.simulation.executable.ExecutableModelInstance import ExecutableModelInstance

from abc import abstractmethod
import subprocess as sub
import os


from typing import Dict, List, Type


class ExecutableEngine(SimulationEngine):
    def __init__(self):
        super().__init__()
        self.sim_in_filename = None
        self.sim_out_filename = None
        self.sim_out_param_name = None
        self.cwd = None
        self.executable_name = None

    def load_model(self, model_filename: str, **exec_info) -> ModelInstance:
        info = list(exec_info.keys())
        self._executable_info_check(info)

        self.executable_name = model_filename
        self.sim_in_filename = exec_info['sim_in_filename']
        self.sim_out_filename = exec_info['sim_out_filename']
        self.cwd = exec_info['cwd']
        if 'sim_out_param_name' in exec_info:
            self.sim_out_param_name = exec_info['sim_out_param_name']

        # Simulation input ad output files cleaning
        self._clean_simulation_files()

        model_obj: str = model_filename
        return ExecutableModelInstance(self, model_obj)

    def simulate_trajectory(self, model: Model, horizon: float) -> Dict[str, List[float]]:
        sim_output = self._run_simulation_task(model, horizon, model.observed_outputs)
        return sim_output

    @abstractmethod
    def simulate_trajectory_and_set(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        pass

    @abstractmethod
    def simulate_trajectory_and_get_state(self, model: Model, horizon: float, exclude=None) -> Dict[str, float]:
        pass

    @abstractmethod
    def restore_state(self, model: Model, changed_values: Dict[str, float]) -> None:
        pass

    @abstractmethod
    def read_simulation_output(self) -> Dict[str, List[float]]:
        pass

    @abstractmethod
    def write_simulation_input(self, params_values: Dict[str, float]) -> None:
        pass

    def model_instance_class(self) -> Type[ModelInstance]:
        return ExecutableModelInstance

    @abstractmethod
    def get_simulation_cmd(self, horizon: float, observed_outputs=None) -> str:
        pass

    def _executable_info_check(self, exec_info: List[str]) -> None:
        if 'sim_in_filename' not in exec_info:
            raise ValueError("The ExecutableEngine needs the simulation input file to simulate the executable model")

        if 'sim_out_filename' not in exec_info:
            raise ValueError("The ExecutableEngine needs the simulation output file to read "
                             " all simulation output trajectories")

        if 'cwd' not in exec_info:
            raise ValueError("The ExecutableEngine needs the current working directory (CWD) to run the executable")

    def _get_simulation_output(self, model: Model, observed: List[str]) -> Dict[str, List[float]]:
        if not isinstance(model.instance, ExecutableModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'ExecutableEngine::simulate_trajectory' method must have type 'ExecutableModelInstance'.")

        trajectories = self.read_simulation_output()
        sim_output: Dict[str, List[float]] = dict()
        if 'time' not in trajectories.keys():
            sim_output['time'] = [0]
            
        for obs_output in trajectories:
            if obs_output in observed or not observed:
                sim_output[obs_output] = trajectories[obs_output]
        return sim_output

    def _run_simulation_task(self, model: Model, horizon: float, observed_outputs: List[str]=None) -> Dict[str, List[float]]:
        if not isinstance(model.instance, ExecutableModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'ExecutableEngine::simulate_trajectory' method must have type 'ExecutableModelInstance'.")

        sub.check_output(self.get_simulation_cmd(horizon, observed_outputs), shell=True, cwd=self.cwd)
        return self._get_simulation_output(model, observed_outputs)

    def _clean_simulation_files(self) -> None:
        if os.path.isfile(f'{self.cwd}/{self.sim_in_filename}'):
            os.remove(f'{self.cwd}/{self.sim_in_filename}')

        if os.path.isfile(f'{self.cwd}/{self.sim_out_filename}'):
            os.remove(f'{self.cwd}/{self.sim_out_filename}')


