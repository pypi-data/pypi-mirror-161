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


import COPASI
from apricopt.solving.whitebox.COPASI.COPASIOptimisationMethod import COPASIOptimisationMethod
from apricopt.solving.whitebox.COPASI.COPASISolverParameter import COPASISolverParameter
from typing import List


class COPASIParticleSwarm(COPASIOptimisationMethod):
    ITERATION_LIMIT = 'Iteration Limit'
    SWARM_SIZE = 'Swarm Size'
    STD_DEVIATION = 'Std. Deviation'
    RANDOM_NUMBER_GENERATOR = "Random Number Generator"
    SEED = "Seed"
    STOP_AFTER_N_STALLED_GENERATIONS = "Stop after # Stalled Generations"

    def __init__(self):
        super(COPASIParticleSwarm, self).__init__()
        self.solver_parameters = [
            COPASISolverParameter(COPASIParticleSwarm.ITERATION_LIMIT, 2000),
            COPASISolverParameter(COPASIParticleSwarm.SWARM_SIZE, 50),
            COPASISolverParameter(COPASIParticleSwarm.STD_DEVIATION, 1e-6)
        ]

    def set_parameters_configuration(self, opt_task: COPASI.COptTask,
                                     solver_parameters: List[COPASISolverParameter] = None) -> None:
        solver_params = self.solver_parameters if solver_parameters is None else solver_parameters
        self.set_optimisation_task(opt_task)
        self.opt_task.setMethodType(COPASI.CTaskEnum.Method_ParticleSwarm)
        self.set_and_check_solver_parameters(solver_params)
