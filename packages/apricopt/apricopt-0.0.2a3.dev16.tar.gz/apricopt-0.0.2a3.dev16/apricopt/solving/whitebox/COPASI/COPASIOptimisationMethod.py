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
from abc import ABC, abstractmethod
from typing import List, Union
from apricopt.solving.whitebox.COPASI.COPASISolverParameter import COPASISolverParameter


class COPASIOptimisationMethod(ABC):
    def __init__(self):
        self.opt_task: Union[COPASI.COptTask, None] = None
        self.solver_parameters: List[COPASISolverParameter] = []

    def set_and_check_solver_parameters(self, solver_parameters: List[COPASISolverParameter]):
        if self.opt_task is None:
            raise ValueError("Optimisation Task has not been set")

        opt_method = self.opt_task.getMethod()
        if opt_method is None:
            raise ValueError("A valid optimisation method has not been set")

        for param in solver_parameters:
            copasi_param = opt_method.getParameter(param.id)
            if copasi_param is None:
                raise ValueError(f"The parameter {param.id} is wrong for such optimisation method")

            if copasi_param.getType() == COPASI.CCopasiParameter.Type_UINT or \
                                            copasi_param.getType() == COPASI.CCopasiParameter.Type_INT:
                copasi_param.setIntValue(int(param.value))
            elif copasi_param.getType() == COPASI.CCopasiParameter.Type_DOUBLE:
                copasi_param.setDblValue(float(param.value))
            elif copasi_param.getType() == COPASI.CCopasiParameter.Type_UDOUBLE:
                copasi_param.setUDblValue(float(param.value))

    def set_optimisation_task(self, opt_task: COPASI.COptTask):
        self.opt_task = opt_task

    @abstractmethod
    def set_parameters_configuration(self, opt_task: COPASI.COptTask,
                                     solver_parameters: List[COPASISolverParameter] = None) -> None:
        pass
