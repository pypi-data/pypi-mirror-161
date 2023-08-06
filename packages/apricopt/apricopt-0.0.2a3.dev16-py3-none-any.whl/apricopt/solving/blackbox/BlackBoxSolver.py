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
from typing import Dict, Any

from apricopt.solving.blackbox.BlackBox import BlackBox


class BlackBoxSolver(ABC):

    def __init__(self):
        self.times = []
        self.objective_values = []
        self.admissible = []
        self.extreme_barrier_constraints_values = {}
        self.progressive_barrier_constraints_values = {}
        self.log = []
        self.start_time = -1

    @abstractmethod
    def solve(self, black_box: BlackBox,
              solver_params: Dict[str, Any]) -> (Dict[str, float], float, float, float, float):
        pass

    def initialize_storage(self, black_box: BlackBox) -> None:
        self.times = []
        self.objective_values = []
        self.extreme_barrier_constraints_values = {}
        self.progressive_barrier_constraints_values = {}
        for extreme_constraint_id in black_box.get_extreme_barrier_constraints_ids():
            self.extreme_barrier_constraints_values[extreme_constraint_id] = []
        for progressive_constraint_id in black_box.get_progressive_barrier_constraints_ids():
            self.progressive_barrier_constraints_values[progressive_constraint_id] = []
        self.log = []

    def set_start_time(self, start_time) -> None:
        self.start_time = start_time

    def add_extreme_barrier_constraint_value(self, constraint_id, value):
        self.extreme_barrier_constraints_values[constraint_id].append(value)

    def add_progressive_barrier_constraint_value(self, constraint_id, value):
        self.progressive_barrier_constraints_values[constraint_id].append(value)

    def add_objective_value(self, value):
        self.objective_values.append(value)
