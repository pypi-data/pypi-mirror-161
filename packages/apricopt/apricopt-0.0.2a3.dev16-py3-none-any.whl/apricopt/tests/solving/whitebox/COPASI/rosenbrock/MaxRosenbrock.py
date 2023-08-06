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

from apricopt.model.Model import Model
from apricopt.simulation.COPASI.COPASIEngine import COPASIEngine
from apricopt.model.Observable import Observable
from apricopt.model.Parameter import Parameter
from apricopt.solving.whitebox.COPASI.COPASISolver import COPASISolver
from apricopt.solving.whitebox.COPASI.method.COPASIGeneticAlgorithm import COPASIGeneticAlgorithm
from apricopt.solving.whitebox.COPASI.COPASISolverParameter import COPASISolverParameter


def define_optimisation_problem(model: Model) -> None:
    '''
    In this function the optimisation problem modeled in SBML is connected with APRICOPT.

    Objective function: such function can be modeled in SBML either as specie or parameter and it must be connected
     through an Observable. It is needed that the obs_id is the respective SBML ID of modeled objective function.

    Optimisation parameters: they can be modeled in SBML either as species or parameters and they must be connected
     through a Parameter. It is needed that the param_id is the respective SBML ID of modeled parameter.
     The inputs upper_bound and lower_bound are needed to define the upper e lower bounds for each optimisation variable.
     If you do not set such values, APRICOPT will set the bounds as, respectively, +Inf and -Inf. The input nominal_value
     is used as x0 value for the specific variable.

    Constraints: they can be modeled in SBML either as species or parameters and they must be connected through an
     Observable. It is needed that the obs_id is the respective SBML ID of modeled objective function.
     The upper_bound and lower_bound are needed to specify the contexts in which a certain constraint is violated.
     If you do not set such values, APRICOPT will set the bounds as, respectively, +Inf and -Inf. In COPASI,
     the constaints are managed by an upper bound an a lower bound and such constraint can assume only the values
     within the bounds (bounds included). If you do not set the nominal value, APRICOPT will set such value as +Inf.

    :param model:
    :return:
    '''

    model.objective = Observable(obs_id='objective', name='objective_function', expressions=["0"])

    model.parameters['x1'] = Parameter(param_id='x1', name='x1 value', lower_bound=-1.5, upper_bound=1.5, nominal_value=0.5)
    model.parameters['x2'] = Parameter(param_id='x2', name='x2 value', lower_bound=-0.5, upper_bound=2.5,
                                       nominal_value=1.0)

    model.constraints.add(
        Observable(obs_id='x1_x2_constraint', name='x1 x2 constraint',
                   expressions=["0"], lower_bound=-1, upper_bound=0)
    )

    model.constraints.add(
        Observable(obs_id='x1_x2_constraint_2', name='x1 x2 constraint',
                   expressions=["0"], lower_bound=-1, upper_bound=0)
    )


def main() -> None:
    '''
    This function shows how to maximise (just to have an example) the Rosenbrock function  with a SBML-based problem
    modeling. Note that, by default, the solver performs a minimisation.

    The optimisation through COPASI Solver is performed as follow:
      1. Create a COPASI Simulation Engine a Model that contains your model with the related simulation configurations.
         In general, different solvers can use different simulation engine. In such context, the COPASI solver can use
         only the COPASI simulation engine.
      2. Create the instance of the chosen optimisation method and then create the COPASI Solver with the chosen
         method and the optimisation log pathname.
      3. Create a list of solver parameters through a COPASISolverParameter object. Note that different solvers can
         have different solver parameters.
      4. Optimise through the solve method.

    :return:
    '''

    sim_engine = COPASIEngine()
    model = Model(sim_engine, "rosenbrock_sbml.xml", abs_tol=1e-12, rel_tol=1e-6, time_step=1)
    define_optimisation_problem(model)

    method = COPASIGeneticAlgorithm()
    solver = COPASISolver(method, "rosenbrock_optimisation_max.log")
    solver_parameters = [
        COPASISolverParameter(COPASIGeneticAlgorithm.NUMBER_OF_GENERATIONS, 40),
        COPASISolverParameter(COPASIGeneticAlgorithm.POPULATION_SIZE, 40),
        COPASISolverParameter(COPASIGeneticAlgorithm.MUTATION_VARIANCE, 0.1),
        COPASISolverParameter(COPASIGeneticAlgorithm.SEED, 1)
    ]

    # To maximise the objectigve function
    solver.set_objective_maximization()

    time_horizon = 100
    optimized_parameters, objective_value, \
        function_evaluations, statistics = solver.solve(model, time_horizon, sim_engine,
                                                        solver_params=solver_parameters)

    x1 = 0.5
    x2 = 1
    a = 1
    b = 100
    rosen_x0 = (a - x1)**2 + b*(x2 - x1**2)**2
    print("==== APRICOPT - COPASI Solver example usage: Rosenbrock ====\n")
    print(f"The objective function evaluated at x0 point: {rosen_x0:.2f}")
    print(f"the objective function value after {function_evaluations} function evaluations: {objective_value:.2f}")
    print(f"The optimised parameters are:\n\t\t x1: {optimized_parameters['x1']}\n\t\t x2: {optimized_parameters['x2']}")


if __name__ == '__main__':
    main()