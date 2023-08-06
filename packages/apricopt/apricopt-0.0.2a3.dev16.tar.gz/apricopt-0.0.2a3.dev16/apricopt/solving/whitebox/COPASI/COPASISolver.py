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

import COPASI
from apricopt.solving.whitebox.WhiteBoxSolver import WhiteBoxSolver
from apricopt.model.Model import Model
from apricopt.solving.whitebox.COPASI.COPASIOptimisationMethod import COPASIOptimisationMethod
from apricopt.simulation.COPASI.COPASIModelInstance import COPASIModelInstance
from apricopt.simulation.SimulationEngine import SimulationEngine
from apricopt.sampling.Sampler import Sampler
from typing import Dict, Union, Tuple, List
import sys


def copasi_solver_log(data_model: COPASI.CDataModel, opt_task: COPASI.COptTask):
    opt_problem = opt_task.getProblem()
    standard_reports = data_model.getReportDefinitionList()
    report = standard_reports.createReportDefinition("Apricopt Report", "Output for optimization")
    # std = standard_reports.get(3)
    report.setTaskType(COPASI.CTaskEnum.Task_optimization)
    report.setIsTable(False)
    report.setSeparator(COPASI.CCopasiReportSeparator("\t\t\t"))

    header = report.getHeaderAddr()
    body = report.getBodyAddr()
    footer = report.getFooterAddr()

    header.push_back(
        COPASI.CRegisteredCommonName(COPASI.CDataString("======= APRICOPT =========\n\n").getCN().getString()))
    header.push_back(
        COPASI.CRegisteredCommonName(
            COPASI.CDataString("=== Optimization through COPASI solver ===\n\n\n").getCN().getString()))
    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString(f"Solver settings: \n\n").getCN().getString()))
    header.push_back(
        COPASI.CRegisteredCommonName(
            COPASI.CDataString(f"{opt_task.getMethod().printToString()}\n\n\n").getCN().getString()))
    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString(f"Optimization Log:\n\n").getCN().getString()))

    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("Function Evaluation").getCN().getString()))
    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("\t").getCN().getString()))
    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("Objective Value").getCN().getString()))
    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("\t\t").getCN().getString()))
    header.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("Optimization Parameters").getCN().getString()))

    body.push_back(
        COPASI.CRegisteredCommonName(opt_problem.getObject(
            COPASI.CCommonName("Reference=Function Evaluations")).getCN().getString()))
    body.push_back(COPASI.CRegisteredCommonName(report.getSeparator().getCN().getString()))

    body.push_back(COPASI.CRegisteredCommonName(opt_problem.getObject(
        COPASI.CCommonName("Reference=Best Value")).getCN().getString()))
    body.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("\t\t\t").getCN().getString()))

    body.push_back(
        COPASI.CRegisteredCommonName(opt_problem.getObject(
            COPASI.CCommonName("Reference=Best Parameters")).getCN().getString()))

    footer.push_back(COPASI.CRegisteredCommonName(COPASI.CDataString("\n\n\n").getCN().getString()))
    footer.push_back(COPASI.CRegisteredCommonName(opt_task.getObject(
        COPASI.CCommonName("Object=Result")).getCN().getString()))

    return report


def get_optimisation_item_from_sbml(model: Model, item_id: str) -> \
        Union[Union[COPASI.CModelValue, COPASI.CMetab], None]:
    data_model: COPASI.CDataModel = model.instance.model_obj
    if isinstance(model.instance, COPASIModelInstance):
        sbml_obj = model.instance.getModelValueBySBMLIdIfPresent(data_model.getModel(), item_id)
        if sbml_obj:
            return sbml_obj
        sbml_obj = model.instance.getMetaboliteBySBMLIdIfPresent(data_model.getModel(), item_id)
        if not sbml_obj:
            raise ValueError("The Objective function or constraint is not encoded in the model")
    else:
        raise ValueError("It is not possibile to use a Simulation Engine different from COPASI")
    return sbml_obj


class COPASISolver(WhiteBoxSolver):
    MINIMISE = 0
    MAXIMISE = 1

    def __init__(self, optimisation_method: COPASIOptimisationMethod, log_filename: str):
        super(COPASISolver, self).__init__()
        self.optimisation_method = optimisation_method
        self.log_filename = log_filename
        self.n_restarts = 0
        self.seed = None
        self.restart_treatments: List[Dict[str, float]] = []
        self.restart_log_folder = None
        self.minimize_maximize = COPASISolver.MINIMISE

    def build_copasi_optimisation_problem(self, model: Model, opt_problem: COPASI.COptProblem) -> None:
        if not isinstance(model.instance, COPASIModelInstance):
            raise TypeError("The instance field of the model must contain an object of type COPASIModelInstance.")

        if self.minimize_maximize == COPASISolver.MAXIMISE:
            opt_problem.setMaximize(True)

        data_model: COPASI.CDataModel = model.instance.model_obj
        objective_obj = get_optimisation_item_from_sbml(model, model.objective.id)
        objective_function = f'<{objective_obj.getObject(COPASI.CCommonName("Reference=Value")).getCN().getString()}>'
        opt_problem.setObjectiveFunction(objective_function)

        copasi_optimisation_constraints = opt_problem.getParameter("OptimizationConstraintList")
        for constr in model.constraints:
            constr_sbml = get_optimisation_item_from_sbml(model, constr.id)
            item = COPASI.COptItem(data_model)
            item.setObjectCN(COPASI.CCommonName(constr_sbml.getObject(COPASI.CCommonName("Reference=Value")).getCN()))
            item.setUpperBound(COPASI.CCommonName(f"{constr.upper_bound}"))
            item.setLowerBound(COPASI.CCommonName(f"{constr.lower_bound}"))
            copasi_optimisation_constraints.addParameter(item)

        for param_id, param in sorted(model.parameters.items(), key=lambda i: i[1].id):
            param_sbml = get_optimisation_item_from_sbml(model, param.id)
            item = opt_problem.addOptItem(
                COPASI.CCommonName(param_sbml.getObject(COPASI.CCommonName("Reference=InitialValue")).getCN())
            )
            item.setUpperBound(COPASI.CCommonName(f"{param.upper_bound}"))
            item.setLowerBound(COPASI.CCommonName(f"{param.lower_bound}"))
            item.setStartValue(param.nominal_value)

    def _change_starting_point(self, opt_problem: COPASI.COptProblem, treatment: Dict[str, float]) -> None:
        opt_item_list = opt_problem.getParameter('OptimizationItemList')
        param_list = [param for param in treatment.keys()]
        param_list.sort()
        for i in range(opt_item_list.size()):
            item = opt_item_list.getParameter(i)
            item.setStartValue(treatment[param_list[i]])

    def _simulation_config_for_sub_task(self, model: Model, horizon: float) -> None:
        data_model: COPASI.CDataModel = model.instance.model_obj
        simulation_task = data_model.getTask("Time-Course")
        assert simulation_task is not None
        copasi_model = data_model.getModel()

        copasi_model.setInitialTime(0.0)
        simulation_task.setMethodType(COPASI.CTaskEnum.Method_deterministic)
        simulation_task.setScheduled(True)

        model.instance.set_simulation_duration_with_step_size(horizon, model.time_step)

    def _run_and_get_output(self, model: Model, opt_task: COPASI.COptTask, opt_problem: COPASI.COptProblem) \
            -> Tuple[Dict[str, float], float, int, Dict[str, Union[float, list]]]:
        result = False
        try:
            result = opt_task.process(True)
        except:
            sys.stderr.write("Running the optimization failed.\n")
            exit(2)
        if not result:
            sys.stderr.write("Running the optimization failed.\n")
            exit(2)

        params_list = [param_id.id for param_id in model.parameters.values()]
        params_list.sort()
        solution_variables = opt_problem.getSolutionVariables()
        optimized_parameters: Dict[str, float] = dict()
        for i in range(len(params_list)):
            optimized_parameters[params_list[i]] = solution_variables.get(i)

        objective_value = opt_problem.getSolutionValue()
        function_evaluations = opt_problem.getFunctionEvaluations()
        statistics: Dict[str, Union[float, list]] = {
            'failed_func_evaluations_nan': opt_problem.getFailedEvaluationsNaN(),
            'failed_func_evaluations_exception': opt_problem.getFailedEvaluationsExc(),
            'execution_time': opt_problem.getExecutionTime(),
        }
        return optimized_parameters, objective_value, function_evaluations, statistics

    def _change_log_path_for_restart(self, opt_task, index: int, log_report):
        opt_task.getReport().setReportDefinition(log_report)
        opt_task.getReport().setTarget(f"{self.restart_log_folder}/restart_{index}_log.txt")
        opt_task.getReport().setAppend(False)

    def set_objective_maximization(self):
        self.minimize_maximize = COPASISolver.MAXIMISE

    def set_restart_configuration(self, seed: int, n_restarts: int,
                                  restart_treatments: List[Dict[str, float]], restart_log_folder: str) -> None:
        self.seed = seed
        self.n_restarts = n_restarts
        self.restart_treatments = restart_treatments
        self.restart_log_folder = restart_log_folder

    def solve(self, model: Model, H: float, sim_engine: SimulationEngine,
              solver_params: list) -> (Dict[str, float], float, dict):
        # Set Time-Course as subtask
        self._simulation_config_for_sub_task(model, H)

        # Set optimization task and time-course subtask type
        data_model: COPASI.CDataModel = model.instance.model_obj
        opt_task: COPASI.COptTask = data_model.getTask('Optimization')
        assert opt_task is not None
        self.optimisation_method.set_parameters_configuration(opt_task, solver_params)
        opt_problem: COPASI.COptProblem = opt_task.getProblem()
        assert opt_problem is not None
        opt_problem.setSubtaskType(COPASI.CTaskEnum.Task_timeCourse)
        self.build_copasi_optimisation_problem(model, opt_problem)

        log_report = copasi_solver_log(data_model, opt_task)
        opt_task.getReport().setReportDefinition(log_report)
        opt_task.getReport().setTarget(self.log_filename)
        opt_task.getReport().setAppend(False)

        optimized_parameters, objective_value, \
            function_evaluations, statistics = self._run_and_get_output(model, opt_task, opt_problem)

        if self.n_restarts > 0:
            statistics['restarts_info'] = []
            sampler = Sampler(model, sim_engine, H, self.seed)
            for i in range(self.n_restarts):
                print(f"Restart {i+1}")
                if i < len(self.restart_treatments):
                    self._change_starting_point(opt_problem, self.restart_treatments[i])
                else:
                    sampled_starting_point = sampler.random_sampling_admissible_parameter_with_respect_constraints()
                    self._change_starting_point(opt_problem, sampled_starting_point)
                self._change_log_path_for_restart(opt_task, i+1, log_report)
                print(f"\t\tStart optimisation restart {i+1}..")
                result = self._run_and_get_output(model, opt_task, opt_problem)
                statistics['restarts_info'].append(result)

        return optimized_parameters, objective_value, \
                            function_evaluations, statistics

