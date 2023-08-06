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

from typing import Dict, List, Callable

from apricopt.model.Observable import Observable, compute_expressions_values_from_assignment


class FastObservable(Observable):

    def __init__(self, param_id: str, name: str, expression: List[str], function: Callable):
        super(FastObservable, self).__init__(param_id, name, expression, function)

    def evaluate(self, assignment: Dict[str, float]) -> float:
        expressions_values = compute_expressions_values_from_assignment(assignment, self.expressions, self.function)
        ret = self.function(*expressions_values)
        return ret
