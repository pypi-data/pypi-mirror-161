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
import math

from apricopt.model.Model import Model
from apricopt.model.Parameter import Parameter
from apricopt.simulation.SimulationEngine import SimulationEngine
from typing import Dict, List, Collection
import numpy as np
from scipy import stats


def sample_parameters(parameters: Collection[Parameter]) -> Dict[str, float]:
    result: Dict[str, float] = dict()
    samples = np.random.rand(len(parameters))
    for i, param in enumerate(parameters):
        if not param.optimize:
            # parameter is fixed (e.g. measured)
            result[param.id] = param.nominal_value
            continue
        if param.distribution == 'uniform':
            result[param.id] = \
                round(param.lower_bound + (
                        param.upper_bound - param.lower_bound) * samples[i])
        elif param.distribution == 'loguniform':
            result[param.id] = 10 ** \
                                         (math.log(param.lower_bound, 10) + (
                                                 math.log(param.upper_bound, 10) - math.log(param.lower_bound,
                                                                                            10))
                                          * samples[i])
        elif param.distribution == 'lognormal':
            result[param.id] = stats.lognorm(param.sigma, scale=param.mu).ppf(
                samples[i])
    return result


class Sampler:
    def __init__(self, model: Model, sim_engine: SimulationEngine, horizon: float, seed: int):
        self.model = model
        self.sim_engine = sim_engine
        self.horizon = horizon
        self.seed = seed
        np.random.seed(seed)

    def random_sampling_admissible_parameter_with_respect_constraints(self) -> Dict[str, float]:
        sampled_parameters = self.parameters_random_sampling()
        self.model.set_fixed_params(sampled_parameters)
        evaluated_constraints = self.sim_engine.simulate(self.model, self.horizon)
        admissible = all(evaluated_constraints[constraint.id] <= 0 for constraint in self.model.constraints)
        while not admissible:
            sampled_parameters = self.parameters_random_sampling()
            self.model.set_fixed_params(sampled_parameters)
            evaluated_constraints = self.sim_engine.simulate(self.model, self.horizon)
            admissible = all(evaluated_constraints[constraint.id] <= 0 for constraint in self.model.constraints)
        return sampled_parameters

    def random_sampling_admissible_parameter_with_respect_fast_constraints(self) -> Dict[str, float]:
        pass

    def random_sampling_admissible_parameter_with_respect_all_constraints(self) -> Dict[str, float]:
        pass

    def parameters_random_sampling(self) -> Dict[str, float]:
        parameters: List[Parameter] = list(self.model.parameters.values())
        parameters.sort(key=lambda x: x.id)
        sample = np.random.rand(len(parameters))
        sampled_parameters: Dict[str, float] = dict()
        for i in range(len(parameters)):
            param = parameters[i]
            if param.distribution == 'uniform':
                sampled_parameters[param.id] = \
                    round(param.lower_bound + (
                            param.upper_bound - param.lower_bound) * sample[i])
        return sampled_parameters

