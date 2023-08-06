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

import re, yaml
from typing import Dict, Set, Tuple, Callable, List

from pandas import DataFrame

from apricopt.model.FastObservable import FastObservable
from apricopt.model.Observable import Observable
from apricopt.model.LogObservable import LogObservable
from apricopt.model.ObservableFunction import ObservableFunction
from apricopt.model.Parameter import Parameter
from apricopt.model.Observable import REPLACEMENTS


def get_parameter_space(parameter_df: DataFrame) -> Set[Parameter]:
    params: Set[Parameter] = set()
    for param_id, data in parameter_df.iterrows():
        params.add(Parameter(str(param_id), data.parameterName,
                             data.lowerBound, data.upperBound, data.nominalValue,
                             data.distribution, data.mu, data.sigma, data.granularity, data.estimate))
    return params


def get_observable_formula(formula: str) -> Tuple[Callable, List[str]]:
    pattern = re.compile(r"(^[A-Za-z0-9_]+)\(([^(]+)\)$")
    match = pattern.match(formula)
    if not match:
        return ObservableFunction.Identity, [formula]
    function_name, expressions_str = match.groups()
    obs_function = ObservableFunction.get_function(function_name)
    if not obs_function:
        return ObservableFunction.Identity, [formula]
    expressions: List[str] = [s.strip() for s in expressions_str.split(',')]
    return obs_function, expressions


def get_objective(objective_df: DataFrame) -> Observable:
    data = objective_df.iloc[0]

    func, expressions = get_observable_formula(data.observableFormula)
    
    result = Observable(data.name, data.observableName, expressions, function=func,
                        lower_bound=data.lowerBound, upper_bound=data.upperBound)
    return result


def get_constraints(constraints_df: DataFrame) -> Set[Observable]:
    result: Set[Observable] = set()
    for obj_id, data in constraints_df.iterrows():
        func, expressions = get_observable_formula(data.observableFormula)
        result.add(Observable(str(obj_id), data.observableName, expressions, function=func))

    return result


def get_log_observables(log_observables_df: DataFrame) -> Set[LogObservable]:
    result: Set[LogObservable] = set()
    for obj_id, data in log_observables_df.iterrows():
        func, expressions = get_observable_formula(data.observableFormula)
        result.add(LogObservable(str(obj_id), data.observableName, expressions, func, data.message, data.formatMode))
    return result

def get_fast_constraints(constraints_df: DataFrame) -> Set[FastObservable]:
    result: Set[FastObservable] = set()
    for obj_id, data in constraints_df.iterrows():
        func, expressions = get_observable_formula(data.observableFormula)
        expressions_no_dots = [x.replace(".", REPLACEMENTS["."]) for x in expressions]
        result.add(FastObservable(str(obj_id), data.observableName, expressions_no_dots, function=func))
    return result


def get_conditions(conditions_df: DataFrame) -> Dict[str, Dict[str, float]]:
    cds: Dict[str, Dict[str, float]] = dict()

    for cd_id, params in conditions_df.iterrows():
        cd_id_str = str(cd_id)
        cds[cd_id_str] = dict()
        for name, value in params.items():
            cds[cd_id_str][name] = value
    return cds


def parse_config_file(config_filename: str) -> dict:
    f = open(config_filename)
    data: dict = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return data


# Needed for COPASI Solver: it could be merged into the get_constraints function
def get_constraints_with_bounds(constraints_df: DataFrame) -> Set[Observable]:
    result: Set[Observable] = set()
    for obj_id, data in constraints_df.iterrows():
        func, expressions = get_observable_formula(data.observableFormula)
        result.add(Observable(str(obj_id), data.observableName, expressions, function=func, lower_bound=data.lowerBound,
                              upper_bound=data.upperBound))

    return result

