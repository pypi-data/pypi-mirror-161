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

from apricopt.model.Model import Model
from apricopt.simulation.executable.ExecutableEngine import ExecutableEngine

from typing import Dict, List

import os


class ModelicaExecutableEngine(ExecutableEngine):

    def simulate_trajectory_and_set(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        raise NotImplementedError

    def simulate_trajectory_and_get_state(self, model: Model, horizon: float, exclude=None) -> Dict[str, float]:
        raise NotImplementedError

    def restore_state(self, model: Model, changed_values: Dict[str, float]) -> None:
        raise NotImplementedError

    def read_simulation_output(self) -> Dict[str, List[float]]:
        results: Dict[str, List[float]] = dict()
        with open(f'{self.cwd}/{self.sim_out_filename}', 'r') as f:
            for line in f.readlines():
                words = line.split()
                results[words[0]] = [float(words[1])]
        
        self._clean_simulation_files()
        return results

    def write_simulation_input(self, params_values: Dict[str, float]) -> None:
        #start = True
        write_out_file_name = False
        #rewrite_file = False
        if not os.path.exists(f'{self.cwd}/{self.sim_in_filename}') and self.sim_out_param_name is not None:
            write_out_file_name = True

        #if os.path.exists(f'{self.cwd}/{self.sim_in_filename}'):
        #    rewrite_file = True
     
        with open(f'{self.cwd}/{self.sim_in_filename}', 'a') as f:
            if write_out_file_name:
                f.write(f'{self.sim_out_param_name}={self.sim_out_filename}\n')

            for name, val in params_values.items():
                f.write(f'{name}={val}\n')
                '''
                if start and not rewrite_file:
                    f.write(f'{name}={val}')
                    start = False
                else:
                    f.write('\n')
                    f.write(f'{name}={val}')
                '''

    def get_simulation_cmd(self, horizon: float, observed_outputs=None) -> str:
        return f'./{self.executable_name} -overrideFile={self.sim_in_filename}'
