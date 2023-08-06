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

from abc import ABC, abstractmethod
from typing import Dict

from apricopt.model.Model import Model
from apricopt.simulation.SimulationEngine import SimulationEngine


class WhiteBoxSolver(ABC):

    def __init__(self):
        self.times = []
        self.objective_values = []
        self.admissible = []
        self.constraints_values = {}
        self.fast_constraints_values = {}
        self.log = []

    @abstractmethod
    def solve(self, model: Model, time_horizon: float, sim_engine: SimulationEngine,
              solver_params: list) -> (Dict[str, float], float, float, float, float):
        pass

    def initialize_storage(self, model: Model) -> None:
        self.times = []
        self.objective_values = []
        self.constraints_values = {}
        self.fast_constraints_values = {}
        for fc in model.constraints:
            self.constraints_values[fc.id] = []
        for fast_c in model.fast_constraints:
            self.fast_constraints_values[fast_c.id] = []
        self.log = []
