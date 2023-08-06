# Apricopt #

Apricopt is a python framework for simulation-based optimisation of dynamical systems.

It is agnostic with respect to the optimiser and to the simulator.

Apricopt supports the PEtab format for the definition of the optimisation problem. More info about PEtab [here](https://petab.readthedocs.io/en/latest/).

Currently, we support the following simulators:

* COPASI. A state-of-the-art simulator for models of biological processes. We support SBML models (any level and version).
* RoadRunner. A fast state-of-the-art simulator of biological models.
* Modelica executable. It supports the simulation of Modelica models given as executables.

Currently, we support the following black-box optimisers:

* NOMAD. A state-of the art black-box solver that supports surrogate models. More info [here](https://www.gerad.ca/nomad/).
* SciPy.optimize. A python library that implements several algorithms for multivariate optimization. More info [here](https://docs.scipy.org/doc/scipy/reference/optimize.html).
* PySwarms. A python library that implements various forms of the Particle Swarm Optimization algorithm. More info [here](https://pyswarms.readthedocs.io/en/latest/).

Currently, we support the following white-box optimisers:

* COPASI. It supports several optimisation algorithms for biological processes. More info [here](http://copasi.org/Support/User_Manual/Methods/Optimization_Methods/)

### Info ###

WIP

* Version 0.0.2a3dev16


### Who do I talk to? ###

* Marco Esposito (author) - esposito@di.uniroma1.it
* Leonardo Picchiami (author) - picchiami@di.uniroma1.it


Copyright (C) 2020-2022  Sapienza University of Rome, Marco Esposito, Leonardo Picchiami.

Distributed under GNU General Public License v3.
