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

from typing import Dict, List, Type
import COPASI
import sys

from apricopt.model.Model import Model
from apricopt.simulation.COPASI.COPASIModelInstance import COPASIModelInstance
from apricopt.simulation.SimulationEngine import SimulationEngine


class COPASIEngine(SimulationEngine):

    def __init__(self):
        super().__init__()

    def load_model(self, model_filename: str, **exec_info) -> COPASIModelInstance:
        data_model = COPASI.CRootContainer.addDatamodel()
        assert (isinstance(data_model, COPASI.CDataModel))
        try:
            res = data_model.importSBML(model_filename)

            if not res:
                sys.stderr.write("There was an error loading the SBML model.\n")
                exit(1)
            return COPASIModelInstance(data_model)
        except COPASI.CCopasiException:
            sys.stderr.write("There was an error loading the SBML model.\n")
            exit(2)

    def simulate_trajectory(self, model: Model, horizon: float) -> Dict[str, List[float]]:
        if not isinstance(model.instance, COPASIModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'COPASIEngine::simulate_trajectory_and_set' method must have type 'COPASIModelInstance'.")
        time_series: COPASI.CTimeSeries = self._run_simulation_task(model, horizon)
        return self._get_simulation_output(model, time_series)

    def simulate_trajectory_and_set(self, model: Model, horizon: float, exclude=None) -> Dict[str, List[float]]:
        if not isinstance(model.instance, COPASIModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'COPASIEngine::simulate_trajectory_and_set' method must have type 'COPASIModelInstance'.")
        if exclude is None:
            exclude = []
        time_series: COPASI.CTimeSeries = self._run_simulation_task(model, horizon)
        model_instance: COPASIModelInstance = model.instance
        data_model: COPASI.CDataModel = model_instance.model_obj
        changed_params: Dict[str, float] = dict()
        changed_metabolites: Dict[str, float] = dict()
        changed_compartments: Dict[str, float] = dict()

        for out_i in range(1, time_series.getNumVariables()):
            output_id = time_series.getSBMLId(out_i, data_model)
            if output_id not in exclude:
                if output_id in model_instance.get_metabolites_ids():
                    changed_metabolites[output_id] = time_series.getConcentrationData(
                        time_series.getRecordedSteps() - 1,
                        out_i)
                elif output_id in model_instance.get_values_ids():
                    changed_params[output_id] = time_series.getData(time_series.getRecordedSteps() - 1, out_i)
                elif output_id in model_instance.get_compartments_ids():
                    changed_compartments[output_id] = time_series.getData(time_series.getRecordedSteps() - 1, out_i)
                elif output_id == data_model.getModel().getObjectName():
                    continue
                else:
                    # sys.stderr.write(f"There was an error collecting the output for variable with id {output_id}.\n")
                    continue

        model_instance.set_species_initial_values(changed_metabolites)
        model_instance.set_parameters(changed_params)
        model_instance.set_compartments_initial_sizes(changed_compartments)

        return self._get_simulation_output(model, time_series)

    def simulate_trajectory_and_get_state(self, model: Model, horizon: float, exclude=None) -> \
            Dict[str, Dict[str, float]]:
        if not isinstance(model.instance, COPASIModelInstance):
            raise TypeError(
                "The object in the field 'instance' of a 'Model' object passed to "
                "'COPASIEngine::simulate_trajectory_and_get_state' method must have type 'COPASIModelInstance'.")

        if exclude is None:
            exclude = []
        time_series: COPASI.CTimeSeries = self._run_simulation_task(model, horizon)
        model_instance: COPASIModelInstance = model.instance
        data_model: COPASI.CDataModel = model_instance.model_obj
        changed_params: Dict[str, float] = dict()
        changed_metabolites: Dict[str, float] = dict()
        changed_compartments: Dict[str, float] = dict()

        for out_i in range(1, time_series.getNumVariables()):
            output_id = time_series.getSBMLId(out_i, data_model)
            if output_id not in exclude:
                if output_id in model_instance.get_metabolites_ids():
                    changed_metabolites[output_id] = time_series.getConcentrationData(
                        time_series.getRecordedSteps() - 1,
                        out_i)
                elif output_id in model_instance.get_values_ids():
                    changed_params[output_id] = time_series.getData(time_series.getRecordedSteps() - 1, out_i)
                elif output_id in model_instance.get_compartments_ids():
                    changed_compartments[output_id] = time_series.getData(time_series.getRecordedSteps() - 1, out_i)
                elif output_id == data_model.getModel().getObjectName():
                    continue
                else:
                    # sys.stderr.write(f"There was an error collecting the output for variable with id {output_id}.\n")
                    continue

        result = dict()
        result['changed_metabolites'] = changed_metabolites
        result['changed_params'] = changed_params
        result['changed_compartments'] = changed_compartments

        return result

    def restore_state(self, model: Model, changed_values: dict) -> None:
        model_instance = model.instance
        if not isinstance(model_instance, COPASIModelInstance):
            raise TypeError(
                "The object in the field 'instance' of a 'Model' object passed to "
                "'COPASIEngine::simulate_trajectory_and_get_state' method must have type 'COPASIModelInstance'.")
        model_instance.set_species_initial_values(changed_values['changed_metabolites'])
        model_instance.set_parameters(changed_values['changed_params'])
        model_instance.set_compartments_initial_sizes(changed_values['changed_compartments'])

    def _get_simulation_output(self, model: Model, time_series: COPASI.CTimeSeries) -> Dict[str, List[float]]:
        if not isinstance(model.instance, COPASIModelInstance):
            raise TypeError(
                "The object in the field 'instance' of a 'Model' object passed to "
                "'COPASIEngine::simulate_trajectory_and_set' method must have type 'COPASIModelInstance'.")
        sim_output: Dict[str, List[float]] = dict()
        sim_output['time'] = [time_series.getData(s, 0) for s in range(time_series.getRecordedSteps())]

        for i in range(time_series.getNumVariables()):
            output_id = time_series.getSBMLId(i, model.instance.model_obj)
            if output_id in model.observed_outputs or not model.observed_outputs:
                # model_instance: COPASIModelInstance = model.instance
                # if output_id in model_instance.get_values_ids() or output_id in model_instance.get_compartments_ids():
                # if the observable was the concentration of a species we should use time_series.getConcentrationData(s,i)
                sim_output[output_id] = [time_series.getData(s, i)
                                         for s in range(time_series.getRecordedSteps())]
        return sim_output

    def _run_simulation_task(self, model: Model, horizon: float) -> COPASI.CTimeSeries:
        if not isinstance(model.instance, COPASIModelInstance):
            raise TypeError("The object in the field 'instance' of a 'Model' object passed to "
                            "'COPASIEngine::simulate_trajectory_and_set' method must have type 'COPASIModelInstance'.")
        model_instance: COPASIModelInstance = model.instance
        data_model: COPASI.CDataModel = model_instance.model_obj
        simulation_task = data_model.getTask("Time-Course")
        assert simulation_task is not None
        copasi_model = data_model.getModel()

        copasi_model.setInitialTime(0.0)
        simulation_task.setMethodType(COPASI.CTaskEnum.Method_deterministic)
        simulation_task.setScheduled(True)

        model_instance.set_simulation_duration_with_step_size(horizon, model.time_step)

        # TODO better error handling
        '''
        sim_ok = True
        try:
            sim_ok = simulation_task.process(True)
        except:
            sys.stderr.write("Error. Running the time course simulation failed.\n")
            sys.stderr.write("{0}\n".format(simulation_task.getProcessWarning()))
            sys.stderr.write("{0}\n".format(simulation_task.getProcessError())) 
            # Check if there are additional error messages
            if COPASI.CCopasiMessage.size() > 0:
                # print the messages in chronological order
                sys.stderr.write("{0}\n".format(COPASI.CCopasiMessage.getAllMessageText(True)))
            #exit(-1)
        if not sim_ok:
            sys.stderr.write("An error occured while running the time course simulation.\n")
            sys.stderr.write("{0}\n".format(simulation_task.getProcessWarning()))
            sys.stderr.write("{0}\n".format(simulation_task.getProcessError()))
            # Check if there are additional error messages
            if COPASI.CCopasiMessage.size() > 0:
                # Print the messages in chronological order
                sys.stderr.write("{0}\n".format(COPASI.CCopasiMessage.getAllMessageText(True)))
            #exit(-1)
        '''

        sim_ok = simulation_task.process(True)
        time_series: COPASI.CTimeSeries = simulation_task.getTimeSeries()
        return time_series

    def model_instance_class(self) -> Type[COPASIModelInstance]:
        return COPASIModelInstance
