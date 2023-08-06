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

from unittest import TestCase, main

from apricopt.model.Model import Model
from apricopt.model.Observable import Observable
from apricopt.model.Parameter import Parameter
from apricopt.simulation.MockUp.MockUpSimulationEngine import MockUpSimulationEngine
from apricopt.solving.blackbox.MockUp.MockUpSolver import MockUpSolver
from apricopt.tests.solving.blackbox.mockup.MockUpBlackBox import MockUpBlackBox


class TestMockUp(TestCase):
    def test(self):
        sim_engine = MockUpSimulationEngine()
        black_box: MockUpBlackBox = MockUpBlackBox(sim_engine)
        solver = MockUpSolver()
        iterations = 1000
        min_params, min_obj, _, _, _ = solver.solve(black_box, [iterations])
        print(f"\n\n==================================\nSolution: {min_params}\nBest Objective Value: {min_obj}")


if __name__ == "__main__":
    main()
