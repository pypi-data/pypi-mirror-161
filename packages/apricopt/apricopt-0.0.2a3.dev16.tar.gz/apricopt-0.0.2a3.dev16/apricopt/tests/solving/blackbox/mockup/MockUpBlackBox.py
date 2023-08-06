from typing import List, Dict

from apricopt.model.Model import Model
from apricopt.model.Observable import Observable
from apricopt.model.Parameter import Parameter
from apricopt.simulation.MockUp.MockUpSimulationEngine import MockUpSimulationEngine
from apricopt.solving.blackbox.BlackBox import BlackBox


class MockUpBlackBox(BlackBox):

    def __init__(self, sim_engine: MockUpSimulationEngine):
        self.sim_engine = sim_engine
        self.model = Model(sim_engine, "", 0, 0, 1, observed_outputs=["output"])
        self.model.objective = Observable("output", "output", ["output"])
        parameter = Parameter("parameter", "parameter", lower_bound=0, upper_bound=1, nominal_value=0.5)
        self.model.set_parameter_space({parameter})
        self.horizon = 1

    def evaluate(self, parameters: Dict[str, float]) -> Dict[str, float]:
        return self.sim_engine.simulate(self.model, self.horizon)

    def get_optimization_parameters_number(self) -> int:
        return len(self.model.parameters)

    def get_optimization_parameters_ids(self) -> List[str]:
        ids = [p_id for p_id in self.model.parameters.keys()]
        ids.sort()
        return ids

    def get_optimization_parameter_lower_bound(self, param_id) -> float:
        return self.model.parameters[param_id].lower_bound

    def get_optimization_parameter_upper_bound(self, param_id) -> float:
        return self.model.parameters[param_id].upper_bound

    def get_optimization_parameter_initial_value(self, param_id) -> float:
        return self.model.parameters[param_id].nominal_value

    def set_optimization_parameters_initial_values(self, param_values: Dict[str, float]) -> None:
        for param_id, param_value in param_values.items():
            if self.get_optimization_parameter_lower_bound(param_id) <= \
                    param_value <= self.get_optimization_parameter_upper_bound(param_id):
                self.model.parameters[param_id].nominal_value = param_value
            else:
                raise ValueError(f"Value {param_value} for parameter {param_id} is outside the bounds")

    def get_optimization_parameter_granularity(self, param_id) -> float:
        return self.model.parameters[param_id].granularity

    def get_extreme_barrier_constraints_number(self) -> int:
        return 0

    def get_progressive_barrier_constraints_number(self) -> int:
        return 0

    def get_extreme_barrier_constraints_ids(self) -> List[str]:
        return []

    def get_progressive_barrier_constraints_ids(self) -> List[str]:
        return []

    def get_objective_id(self) -> str:
        return "output"

    def get_objective_upper_bound(self) -> float:
        return 1

    @staticmethod
    def get_raisable_exception_type():
        pass

    def finalize(self) -> None:
        pass
