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

import sympy
import numpy as np
from typing import Dict
import re
from .ObservableFunction import *

REPLACEMENTS: Dict[str, str] = {"^": "**", ".": "__DOT__"}


def make_compliant_with_sympy(expressions: List[str]) -> List[str]:
    result: List[str] = list()
    for expr in expressions:
        for old, new in REPLACEMENTS.items():
            expr = expr.replace(old, new)
        expr = expr.strip()
        result.append(expr)
    return result


def get_assignment_at_step(assignment: Dict[str, List[float]], t: int) -> Dict[str, float]:
    assign: Dict[str, float] = dict()
    for v_id, sequence in assignment.items():
        assign[v_id] = sequence[t]
    return assign


def compute_expressions_values(trajectory: Dict[str, List[float]], expressions: List[str], obs_function: Callable) -> \
        List[List[float]]:
    # matches <decimal> e.g. 1, 0.1, 10.23, 1e12, 1.3e-12
    pattern_0 = re.compile(r"((-?\d+(\.\d+)?)(e-?\d+)?)")
    # matches <var_id> <op> <decimal>
    pattern_1 = re.compile(r"([A-Za-z0-9_]+)\s*([+\-*{1,2}/^])\s*((-?\d+(\.\d+)?)(e-?\d+)?)")
    # matches <decimal> <op> <var_id>
    pattern_2 = re.compile(
        r"((-?\d+(\.\d+)?)([e,E]-?\d+)?)\s*([+\-*{1,2}/^])\s*([A-Za-z0-9_]+)")
    # matches <decimal> <op> <var_id>
    pattern_3 = re.compile(r"([A-Za-z0-9_]+)\s*([+\-*{1,2}/^])\s*([A-Za-z0-9_]+)")
    expressions_values: List[List[float]] = []
    traj_length: int = len(trajectory['time'])
    
    # Symbols id adjustment 
    #tmp_replaced_trajectory: Dict[str, List[float]] = dict()
    for x in list(trajectory.keys()):
        if "." in x:
            x_no_dots: str = x.replace(".", REPLACEMENTS["."])
            trajectory[x_no_dots] = trajectory[x]
        #else:
        #    tmp_replaced_trajectory[x] = traj_x    
    #trajectory = tmp_replaced_trajectory

    for expr in expressions:
        sympy_expr = sympy.sympify(expr)
        symbols = list(sympy_expr.free_symbols)
        simple = False
        if len(symbols) == 0:
            match_0 = pattern_0.match(expr)
            if match_0.end() == len(expr):
                simple = True
                value = float(match_0.group(1))
                expressions_values.append([value] * traj_length)
        elif len(symbols) == 1 and str(symbols[0]) in trajectory:
            if not any(op in expr for op in ["+", "-", "*", "-", "^", "**", "/"]):
                expressions_values.append(trajectory[str(symbols[0])])
                simple = True
            else:
                match_1 = pattern_1.match(expr)
                match_2 = pattern_2.match(expr)

                variable = ""
                operation = ""
                decimal = float("Nan")
                match_type = 0
                if match_1 and match_1.end() == len(expr):
                    variable = match_1.group(1).strip()
                    operation = match_1.group(2).strip()
                    decimal = float(match_1.group(3).strip())
                    match_type = 1
                elif match_2 and match_2.end() == len(expr):
                    decimal = float(match_2.group(1).strip())
                    operation = match_2.group(5).strip()
                    variable = match_2.group(6).strip()
                    match_type = 2
                if variable != "":
                    simple = True
                    values = np.array(trajectory[str(symbols[0])])
                    if match_type == 1:
                        a = values
                        b = decimal
                    else:
                        a = decimal
                        b = values
                    if operation == "+":
                        expressions_values.append(list(a + b))
                    elif operation == "-":
                        expressions_values.append(list(a - b))
                    elif operation == "*":
                        expressions_values.append(list(a * b))
                    elif operation == "/":
                        expressions_values.append(list(a / b))
                    else:  # if operation in ["^", "**"]:
                        expressions_values.append(list(a ** b))
        elif len(symbols) == 2 and str(symbols[0]) in trajectory and str(symbols[1]) in trajectory:
            match = pattern_3.match(expr)
            if match and match.end() == len(expr):
                simple = True
                var_1 = match.group(1).strip()
                var_2 = match.group(3).strip()
                operation = match.group(2).strip()
                values_1 = np.array(trajectory[var_1])
                values_2 = np.array(trajectory[var_2])
                if operation == "+":
                    expressions_values.append(list(values_1 + values_2))
                elif operation == "-":
                    expressions_values.append(list(values_1 - values_2))
                elif operation == "*":
                    expressions_values.append(list(values_1 * values_2))
                elif operation == "/":
                    expressions_values.append(list(values_1 / values_2))
                elif operation in ["^", "**"]:
                    expressions_values.append(list(values_1 ** values_2))

        if not simple:
            local_assignment: Dict[str, List[float]] = dict()
            for symbol in symbols:
                local_assignment[str(symbol)] = trajectory[str(symbol)]

            if obs_function in [ObservableFunction.Identity, ObservableFunction.LastValue]:
                expressions_values.append([float(
                    sympy.parse_expr(expr, local_dict=get_assignment_at_step(local_assignment, traj_length - 1)))])
            else:
                expressions_values.append(
                    [float(
                        sympy.parse_expr(expr, local_dict=get_assignment_at_step(local_assignment, t))) for t in
                        range(traj_length)])
    return expressions_values

def compute_expressions_values_from_assignment(assignment: Dict[str, float], expressions: List[str],
                                               obs_function: Callable) -> List[List[float]]:
    trajectory: Dict[str, List[float]] = {v_id: [assignment[v_id]] for v_id in assignment}
    trajectory['time'] = [0]
    expressions_values: List[List[float]] = compute_expressions_values(trajectory, expressions, obs_function)
    return expressions_values


class Observable:
    def __init__(self, obs_id: str, name: str, expressions: List[str],
                 function: Callable = ObservableFunction.Identity,
                 lower_bound: float = float("-Inf"), upper_bound: float = float("Inf")):
        self.id: str = obs_id
        self.name: str = name
        self.expressions: List[str] = make_compliant_with_sympy(expressions)
        self.function: Callable = function
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def evaluate(self, trajectory: Dict[str, List[float]]) -> float:
        expressions_values = compute_expressions_values(trajectory, self.expressions, self.function)
        return self.function(*expressions_values)

    def test(self, assignment: Dict[str, float]) -> float:
        test_trajectory: Dict[str, List[float]] = {"time": [0]}
        for param_id, param_value in assignment.items():
            test_trajectory[param_id] = [param_value]
        return self.evaluate(test_trajectory)

