from typing import List, Callable, Dict

from apricopt.model.Observable import Observable, compute_expressions_values_from_assignment, compute_expressions_values


class LogObservable(Observable):

    def __init__(self, param_id: str, name: str, expression: List[str], function: Callable,
                 message: str, format_mode: str = "append"):
        super(LogObservable, self).__init__(param_id, name, expression, function)
        self.message: str = message
        self.format_mode: str = format_mode

    def evaluate(self, trajectory: Dict[str, List[float]]) -> str:
        expressions_values = compute_expressions_values(trajectory, self.expressions, self.function)
        value: float = self.function(*expressions_values)
        return self.format_message(value)

    def value(self, trajectory: Dict[str, List[float]]) -> float:
        expressions_values = compute_expressions_values(trajectory, self.expressions, self.function)
        return self.function(*expressions_values)

    def format_message(self, value: float) -> str:
        if self.format_mode == "append":
            return self.message + str(value)
        else:
            return self.message.format(value)
