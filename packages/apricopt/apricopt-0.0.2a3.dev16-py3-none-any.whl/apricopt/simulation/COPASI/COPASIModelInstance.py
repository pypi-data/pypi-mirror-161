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

from typing import *

from apricopt.model.ModelInstance import ModelInstance


class COPASIModelInstance(ModelInstance):

    def __init__(self, model_obj: COPASI.CDataModel):
        super().__init__(model_obj)
        self.cached_metabolites_ids = None
        self.cached_values_ids = None
        self.cached_compartments_ids = None
        self.cached_value_objects = dict()
        self.cached_metabolite_objects = dict() # added merge

    def __delete__(self, instance):
        model_obj: COPASI.CDataModel = self.model_obj
        model_obj.destruct()

    def set_parameters(self, params_values: Dict[str, float]) -> None:
        copasi_model = self.model_obj.getModel()

        changed_objects = COPASI.ObjectStdVector()
        assert changed_objects is not None
        for param_id, value in params_values.items():
            param_obj = self.getModelValueBySBMLId(copasi_model, param_id)
            param_obj.setInitialValue(value)
            ivr = param_obj.getInitialValueReference()
            changed_objects.push_back(ivr)
        copasi_model.updateInitialValues(changed_objects)

    def getModelValueBySBMLId(self, copasi_model: COPASI.CModel, value_id: str) -> COPASI.CModelValue:
        if not value_id in self.cached_value_objects:
            found = False
            for value in copasi_model.getModelValues():
                if value.getSBMLId() == value_id:
                    self.cached_value_objects[value_id] = value
                    found = True
                    break
            if not found:
                raise ValueError(f"Could not find model parameter with id {value_id}")

        return self.cached_value_objects[value_id]

    def getModelValueBySBMLIdIfPresent(self, copasi_model: COPASI.CModel, value_id: str) -> Union[COPASI.CModelValue, None]:
        if not value_id in self.cached_value_objects:
            for value in copasi_model.getModelValues():
                if value.getSBMLId() == value_id:
                    self.cached_value_objects[value_id] = value
                    return self.cached_value_objects[value_id]
            return None
        return self.cached_value_objects[value_id]

    def getMetaboliteBySBMLIdIfPresent(self, copasi_model: COPASI.CModel, value_id: str) -> Union[COPASI.CMetab, None]:
        if not value_id in self.cached_metabolite_objects:
            for value in copasi_model.getMetabolites():
                if value.getSBMLId() == value_id:
                    self.cached_metabolite_objects[value_id] = value
                    return self.cached_metabolite_objects[value_id]
            return None
        return self.cached_metabolite_objects[value_id]

    def set_compartments_initial_sizes(self, compartments_values: Dict[str, float]) -> None:
        copasi_model: COPASI.CModel = self.model_obj.getModel()
        changed_objects = COPASI.ObjectStdVector()
        assert changed_objects is not None
        for compartment_id, compartment_size in compartments_values.items():
            # compartment_obj: COPASI.CCompartment = self.get_compartment_by_id(compartment_id)
            compartment_obj: COPASI.CCompartment = self.model_obj.getModel().getCompartment(compartment_id)
            compartment_obj.setInitialValue(compartment_size)
            ivr = compartment_obj.getInitialValueReference()
            changed_objects.push_back(ivr)

            # self.model_obj.getModel().getCompartment(compartment_id).setInitialValue(compartment_size)

            copasi_model.updateInitialValues(changed_objects)

    def set_species_initial_values(self, values: Dict[str, float]) -> None:
        changedObjects = COPASI.ObjectStdVector()
        for met_id, met_value in values.items():
            found = False
            for metabolite_obj in self.model_obj.getModel().getMetabolites():
                if metabolite_obj.getSBMLId() == met_id:
                    found = True
                    metabolite_obj.setInitialValue(metabolite_obj.getValue())
                    icr = metabolite_obj.getInitialValueReference()
                    changedObjects.push_back(icr)
            if not found:
                raise Exception(f"ERROR: Metabolite with id {met_id} not found in the model.")
        self.model_obj.getModel().updateInitialValues(changedObjects)

    def set_species_initial_values_OLD(self, values: Dict[str, float]) -> None:
        for met_id, met_value in values.items():
            self.set_species_initial_value(met_id, met_value)

    def set_species_initial_value(self, metabolite_id: str, metabolite_value: float) -> None:
        '''metabolite_obj: COPASI.CMetab = self.get_metabolite_by_id(metabolite_id)
        metabolite_obj.setInitialConcentration(metabolite_value)
        self.model_obj.getModel().updateInitialValues(metabolite_obj.getInitialConcentrationReference())'''

        for metabolite_obj in self.model_obj.getModel().getMetabolites():
            if metabolite_obj.getSBMLId() == metabolite_id:
                # metabolite_obj.setInitialConcentration(metabolite_value)
                metabolite_obj.setInitialValue(metabolite_obj.getValue())
                # metabolite_obj.setInitialConcentration(metabolite_obj.getConcentration())
                changedObjects = COPASI.ObjectStdVector()
                # icr = metabolite_obj.getInitialConcentrationReference()
                icr = metabolite_obj.getInitialValueReference()
                changedObjects.push_back(icr)
                self.model_obj.getModel().updateInitialValues(changedObjects)
                return
        raise Exception(f"Metabolite with id {metabolite_id} not found in the model")
        # metabolite_obj: COPASI.CMetab = self.model_obj.getModel().getMetabolite(metabolite_id)

    def get_parameters_initial_values(self) -> Dict[str, float]:
        copasi_model: COPASI.CModel = self.model_obj.getModel()
        result: Dict[str, float] = dict()
        for param in copasi_model.getModelValues():
            result[param.getSBMLId()] = param.initial_value
        return result

    def get_compartment_initial_volumes(self) -> Dict[str, float]:
        copasi_model: COPASI.CModel = self.model_obj.getModel()
        result: Dict[str, float] = dict()
        for comp in copasi_model.getModelValues():
            result[comp.getSBMLId()] = comp.getInitialValue()
        return result

    def set_parameter(self, param_id: str, value: float) -> None:
        self.set_parameters({param_id: value})

    def set_simulation_configuration(self, abs_tol: float, rel_tol: float, step_size: float) -> None:
        simulation_task = self.model_obj.getTask("Time-Course")
        assert simulation_task is not None

        # Relative and absolute tolerance
        method = simulation_task.getMethod()
        absolute_tolerance = method.getParameter("Absolute Tolerance")
        assert absolute_tolerance is not None
        assert absolute_tolerance.getType() == COPASI.CCopasiParameter.Type_UDOUBLE
        absolute_tolerance.setValue(abs_tol)

        relative_tolerance = method.getParameter("Relative Tolerance")
        assert relative_tolerance is not None
        assert relative_tolerance.getType() == COPASI.CCopasiParameter.Type_UDOUBLE
        relative_tolerance.setValue(rel_tol)

        simulation_problem = simulation_task.getProblem()
        assert simulation_problem is not None

        simulation_problem.setModel(self.model_obj.getModel())
        simulation_problem.setStepSize(step_size)
        simulation_problem.setTimeSeriesRequested(True)

    def set_simulation_duration(self, duration: float) -> None:
        simulation_task = self.model_obj.getTask("Time-Course")
        assert simulation_task is not None
        simulation_problem: COPASI.CTrajectoryProblem = simulation_task.getProblem()
        assert simulation_problem is not None

        simulation_problem.setModel(self.model_obj.getModel())
        simulation_problem.setDuration(duration)

        simulation_problem.setStepNumber(int(duration / simulation_problem.getStepSize()))

    def set_simulation_duration_with_step_size(self, duration: float, step_size: float) -> None:
        simulation_task = self.model_obj.getTask("Time-Course")
        assert simulation_task is not None
        simulation_problem: COPASI.CTrajectoryProblem = simulation_task.getProblem()
        assert simulation_problem is not None

        simulation_problem.setModel(self.model_obj.getModel())
        simulation_problem.setDuration(duration)

        simulation_problem.setStepNumber(int(duration / step_size))

    def get_metabolites_ids(self) -> Set[str]:
        if not self.cached_metabolites_ids:
            self.cached_metabolites_ids: Set[str] = set()
            metabolites: COPASI.MetabVector = self.model_obj.getModel().getMetabolites()
            for metabolite in metabolites:
                self.cached_metabolites_ids.add(metabolite.getSBMLId())

        return self.cached_metabolites_ids

    def get_values_ids(self) -> Set[str]:
        if not self.cached_values_ids:
            self.cached_values_ids: Set[str] = set()
            model_values: COPASI.ModelValueVectorN = self.model_obj.getModel().getModelValues()
            for model_value in model_values:
                self.cached_values_ids.add(model_value.getSBMLId())
        return self.cached_values_ids

    def get_compartments_ids(self) -> Set[str]:
        if not self.cached_compartments_ids:
            self.cached_compartments_ids: Set[str] = set()
            compartments: COPASI.CompartmentVectorNS = self.model_obj.getModel().getCompartments()
            for compartment in compartments:
                self.cached_compartments_ids.add(compartment.getSBMLId())
        return self.cached_compartments_ids

    '''def get_metabolites_by_id(self) -> Dict[str, COPASI.CMetab]:
        if not self.cached_metabolites_by_id:
            self.cached_metabolites_by_id: Dict[str, COPASI.CMetab] = dict()
            metabolites: COPASI.MetabVector = self.model_obj.getModel().getMetabolites()
            for metabolite in metabolites:
                self.cached_metabolites_by_id[metabolite.getSBMLId()] = metabolite

        return self.cached_metabolites_by_id

    def get_metabolite_by_id(self, met_id:str) -> COPASI.CMetab:
        return self.get_metabolites_by_id()[met_id]

    def get_values_by_id(self) -> Dict[str, COPASI.CModelValue]:
        if not self.cached_values_by_id:
            self.cached_values_by_id: Dict[str, COPASI.CModelValue] = dict()
            model_values: COPASI.ModelValueVectorN = self.model_obj.getModel().getModelValues()
            for model_value in model_values:
                self.cached_values_by_id[model_value.getSBMLId()] = model_value
        return self.cached_values_by_id

    def get_value_by_id(self, value_id: str) -> COPASI.CModelValue:
        return self.get_values_by_id()[value_id]

    def get_compartments_by_id(self) -> Dict[str, COPASI.CCompartment]:
        if not self.cached_compartments_by_id:
            self.cached_compartments_by_id: Dict[str, COPASI.CCompartment] = dict()
            compartments: COPASI.CompartmentVectorNS = self.model_obj.getModel().getCompartments()
            for compartment in compartments:
                self.cached_compartments_by_id[compartment.getSBMLId()] = compartment
        return self.cached_compartments_by_id

    def get_compartment_by_id(self, compartment_id: str) -> COPASI.CCompartment:
        return self.get_compartments_by_id()[compartment_id]'''
