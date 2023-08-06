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

from apricopt.model.Observable import Observable
from apricopt.model.ObservableFunction import *

obs_function: Callable = MaxDistanceFromBounds
o = Observable('obs_0', "test", ["x + y", "z", "70"], obs_function)

assignment = {'time': [0, 1, 2, 3, 4, 5, 6, 7],
              "x": [0, 1, 2, 3, 4, 5, 6, 7],
              "y": [54, 24, 65, 67, 23, 45, 76, 12],
              "z": [5, 5, 5, 5, 5, 5, 5, 5]}

print(o.evaluate(assignment))
