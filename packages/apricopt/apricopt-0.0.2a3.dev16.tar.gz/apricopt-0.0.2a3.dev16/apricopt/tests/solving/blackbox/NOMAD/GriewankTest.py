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

from apricopt.solving.blackbox.NOMAD.NOMADSolver import NOMADSolver
from apricopt.tests.solving.blackbox.GriewankBB import TestBlackBox

black_box = TestBlackBox(2)

solver = NOMADSolver()
solver_params = {"solver_params": []}

result = solver.solve(black_box, solver_params)

print(result)
