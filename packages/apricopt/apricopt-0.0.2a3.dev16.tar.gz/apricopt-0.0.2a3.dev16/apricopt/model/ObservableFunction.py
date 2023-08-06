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

from typing import List, Callable, Set

from apricopt.model.ObservableFunctionNotFoundError import ObservableFunctionNotFoundError


class ObservableFunction:
    @staticmethod
    def Identity(*args: List[float]) -> float:
        return ObservableFunction.LastValue(*args)

    @staticmethod
    def LastValue(*args: List[float]) -> float:
        return args[0][-1]

    @staticmethod
    def Average(*args: List[float]) -> float:
        if len(args[0]) == 0:
            return 0
        return sum(args[0]) / len(args[0])

    @staticmethod
    def Min(*args: List[float]) -> float:
        return min(args[0])

    @staticmethod
    def Max(*args: List[float]) -> float:
        return max(args[0])

    @staticmethod
    def Sum(*args: List[float]) -> float:
        return sum(args[0])

    @staticmethod
    def MaxDistanceFromLowerBound(*args: List[float]) -> float:
        value: List[float] = args[0]
        lower_bound: List[float] = args[1]

        return max(lower_bound[t] - value[t] for t in range(len(value)))

    @staticmethod
    def MaxDistanceFromUpperBound(*args: List[float]):
        value: List[float] = args[0]
        upper_bound: List[float] = args[1]

        return max(value[t] - upper_bound[t] for t in range(len(value)))

    @staticmethod
    def MaxDistanceFromBounds(*args: List[float]) -> float:
        value: List[float] = args[0]
        lower_bound: List[float] = args[1]
        upper_bound: List[float] = args[2]

        return max(
            max(lower_bound[t] - value[t], value[t] - upper_bound[t]) for t in range(len(value)))

    @staticmethod
    def FinalDistanceFromUpperBound(*args: List[float]) -> float:
        value: float = args[0][-1]
        upper_bound: float = args[1][-1]
        return value - upper_bound

    @staticmethod
    def CumSumSpikes(*args: List[float]):
        value: List[float] = args[0]

        cumsum: float = value[0]
        for t in range(1, len(value)):
            if value[t] > value[t - 1]:
                cumsum += value[t] - value[t - 1]
        return cumsum

    @staticmethod
    def CumSumSpikesDistanceFromLowerBound(*args: List[float]) -> float:
        cumsum: float = ObservableFunction.CumSumSpikes(*args)
        return args[1][-1] - cumsum

    @staticmethod
    def CumSumSpikesDistanceFromUpperBound(*args: List[float]) -> float:
        cumsum: float = ObservableFunction.CumSumSpikes(*args)
        return cumsum - args[1][-1]

    @staticmethod
    def CumSumSpikesDistanceFromBounds(*args: List[float]) -> float:
        cumsum: float = ObservableFunction.CumSumSpikes(*args)
        return max(args[1][-1] - cumsum, cumsum - args[2][-1])

    @staticmethod
    def MaxDifferenceInPeriod(*args: List[float]) -> float:
        value: List[float] = args[0]
        period_length: int = int(args[1][0])

        return max(value[t] - value[t - period_length - 1] for t in range(period_length, len(value)))

    @staticmethod
    def MaxDifferenceInPeriodDistanceFromAbove(*args: List[float]) -> float:
        return ObservableFunction.MaxDifferenceInPeriod(*args) - args[2][0]

    @staticmethod
    def MaxSpikesSumDifferenceInPeriodDistanceFromAbove(*args: List[float]) -> float:
        value: List[float] = args[0]
        period_length = args[1]
        upper_bound = args[2]

        cumsum: List[float] = [value[0]]
        for t in range(1, len(value)):
            if value[t] > value[t - 1]:
                cumsum[t] = value[t] - value[t - 1]
            else:
                cumsum[t] = value[t - 1]
        return ObservableFunction.MaxDifferenceInPeriodDistanceFromAbove(cumsum, period_length, upper_bound)

    @staticmethod
    def IndexOfFirstGE(*args: List[float]) -> float:
        value: List[float] = args[0]
        lower_bound: List[float] = args[1]
        for t in range(len(value)):
            if value[t] >= lower_bound[t]:
                return t
        return len(value)

    @staticmethod
    def IndexOfFirstGT(*args: List[float]) -> float:
        value: List[float] = args[0]
        lower_bound: List[float] = args[1]
        for t in range(len(value)):
            if value[t] > lower_bound[t]:
                return t
        return len(value)

    @staticmethod
    def IndexOfFirstEQ(*args: List[float]) -> float:
        value: List[float] = args[0]
        target: List[float] = args[1]
        for t in range(len(value)):
            if value[t] == target[t]:
                return t
        return len(value)

    @staticmethod
    def IndexOfFirstLE(*args: List[float]) -> float:
        value: List[float] = args[0]
        upper_bound: List[float] = args[1]
        for t in range(len(value)):
            if value[t] <= upper_bound[t]:
                return t
        return len(value)

    @staticmethod
    def IndexOfFirstLT(*args: List[float]) -> float:
        value: List[float] = args[0]
        upper_bound: List[float] = args[1]
        for t in range(len(value)):
            if value[t] < upper_bound[t]:
                return t
        return len(value)

    __function_names = {"max": Max,
                        "min": Min,
                        "avg": Average, "mean": Average,
                        "maxdistancefrombounds": MaxDistanceFromBounds,
                        "maxdistancefromlowerbound": MaxDistanceFromLowerBound,
                        "maxdistancefromupperbound": MaxDistanceFromUpperBound,
                        "cumsumspikes": CumSumSpikes,
                        "maxdifferenceinperiod": MaxDifferenceInPeriod,
                        "maxdifferenceinperioddistancefromabove": MaxDifferenceInPeriodDistanceFromAbove,
                        "maxspikessumdifferenceinperioddistancefromabove":
                            MaxSpikesSumDifferenceInPeriodDistanceFromAbove,
                        "indexoffirstge": IndexOfFirstGE,
                        "indexoffirstgt": IndexOfFirstGT,
                        "indexoffirsteq": IndexOfFirstEQ,
                        "indexoffirstle": IndexOfFirstLE,
                        "indexoffirstlt": IndexOfFirstLT,
                        "finaldistancefromupperbound": FinalDistanceFromUpperBound}

    @staticmethod
    def get_function(function_name: str) -> Callable:
        if function_name.lower() in ObservableFunction.__function_names:
            return ObservableFunction.__function_names[function_name.lower()]
        else:
            raise ObservableFunctionNotFoundError(function_name)

    @staticmethod
    def add_function(function_name: str, function: Callable):
        if function_name not in ObservableFunction.__function_names:
            ObservableFunction.__function_names[function_name.lower()] = function

    @staticmethod
    def get_function_names() -> Set[str]:
        return {n for n in ObservableFunction.__function_names.keys()}
