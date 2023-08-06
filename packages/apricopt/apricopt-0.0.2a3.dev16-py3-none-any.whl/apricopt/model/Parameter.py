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


class Parameter:

    def __init__(self, param_id: str, name: str, lower_bound: float = float("-inf"),
                 upper_bound: float = float("inf"), nominal_value: float = float("-inf"),
                 distribution: str = 'uniform', mu: float = 0, sigma: float = 0,
                 granularity: float = 0, optimize: bool = True):
        self.id = param_id
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.nominal_value = nominal_value
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma
        self.granularity = granularity
        self.optimize = optimize
