from typing import List

from apricopt.IO.data_input import get_observable_formula
from apricopt.model.Model import Model
from apricopt.model.Observable import Observable
from apricopt.model.ObservableFunction import ObservableFunction
import math

from apricopt.model.Parameter import Parameter


def test_user_function(*args: List[float]) -> float:
    return math.cos(args[0][0]) + math.sin(args[1][0])


ObservableFunction.add_function("TestFunction", test_user_function)
print(ObservableFunction.get_function_names())

m = Model(sim_engine=None, model_filename="", abs_tol=0, rel_tol=0, time_step=0)
func, expressions = get_observable_formula("TestFunction(p1,p2)")

m.objective = Observable("obj", "objName", expressions, function=func,
                         lower_bound=-2, upper_bound=2)

p1 = Parameter("p1", "param1", -1, 1, 0)
p2 = Parameter("p2", "param2", -1, 1, 0)

m.set_parameter_space({p1, p2})

for v1 in [0, math.pi/6, math.pi/4, math.pi/3, math.pi/2, math.pi/2+math.pi/6, math.pi/2+math.pi/3, math.pi]:
    for v2 in [0, math.pi/6, math.pi/4, math.pi/3, math.pi/2, math.pi/2+math.pi/6, math.pi/2+math.pi/3, math.pi]:
        print(f"obj({v1}, {v2}) = {m.objective.test({'p1': v1, 'p2': v2})}")
