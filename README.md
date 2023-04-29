# Cloud Resource Matcher [![PyPI Version](https://img.shields.io/pypi/v/cloud_resource_matcher)](https://pypi.org/project/cloud_resource_matcher/) [![License](https://img.shields.io/github/license/TimJentzsch/cloud_resource_matcher)](./LICENSE)

A framework to optimize cloud computing costs, using [mixed integer programming](https://en.wikipedia.org/wiki/Integer_programming).

This library should be used together with [`optiframe`](https://github.com/TimJentzsch/optiframe) and [`pulp`](https://github.com/coin-or/pulp).
`optiframe` is the underlying optimization framework. This library provides modules for cloud computing that you can use with `optiframe`.
`pulp` is used to implement the mixed integer program. You only need to use it if you want to add additional modules or if you want to configure the solver.

## Prerequisites

- [Python](https://www.python.org/downloads/) >= 3.11
- [optiframe](https://github.com/TimJentzsch/optiframe)

## Installation

```cli
pip install optiframe
```

## Usage

### The Modules

This library provides multiple modules that you can use in `optiframe` for modeling cloud cost optimization problems:

- `base_module`: This module represents the basic decision of which cloud resources should be deployed on which cloud services.
    It also adds instance demands and flat (upfront) base costs for cloud services.
    This module must always be added, all other modules depend on it.
- `performance_module`: A module for performance requirements.
    It allows you to define performance criteria (such as vCPUs and RAM) and the corresponding demand & supply.
    Use-based pricing models can also be represented with this module.
- `network_module`: This module provides the means to encode network connections, maximum latency requirements and network traffic costs.
- `multi_cloud_module`: If multiple cloud service providers are considered for the decision, this module can be used.
    It allows you to assign the cloud services to the providers, specify migration cost and enforce a minimum and maximum number of providers to be used.
- `service_limits_module`: If a cloud service is under very high demand and only a limited number of instances is available for purchase, this module can encode these requirements.

### Code Example

Here is a small example demonstrating how to use this library:

```py
from pulp import LpMinimize
from optiframe import Optimizer, SolutionObjValue
from cloud_resource_matcher.modules.base import BaseData, BaseSolution, base_module
from cloud_resource_matcher.modules.performance import PerformanceData, performance_module

# Specify the data of the problem instance
base_data = BaseData(...)
performance_data = PerformanceData(...)

solution = (
    Optimizer("cloud_cost_optimization", sense=LpMinimize)
    # Configure which modules you want to use
    .add_modules(base_module, performance_module)
    # Add the data of the problem instance
    .initialize(base_data, performance_data)
    # Obtain the optimal solution to the problem
    .solve()
)

# Extract the total cost of the solution
cost = solution[SolutionObjValue].objective_value
# Determine which cloud resource should be matched to which cloud service
matching = solution[BaseSolution]
```

You can also take a look at the `examples` folder for a more detailed example.
The `test/case_studies` folder also contains examples based on the pricing examples from cloud service providers.

### Configuring the Solver

This library uses `pulp` under the hood and is therefore agnostic to the solver backend that you can use.
By default, it uses the CBC solver, which is pre-bundled with `pulp`.
However, it's not very fast, so you probably want to change it.

You can pass any solver object from `pulp` into the `.solve(...)` method.
Take a look at [this documentation](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html) for instructions on how to install and configure the solvers.

## Glossary

Here is a small glossary of terms that are used across this project:

- **Cloud resource** (CR): Anything you want to deploy on the cloud, such as virtual machines, serverless functions or databases.
- **Cloud service** (CS): An offer that you can buy in the cloud, for example Google Cloud C3, Amazon S3 or Azure Functions.
- **Cloud service provider** (CSP): A company offering cloud services. For example Google Cloud, AWS or Microsoft Azure.
- **Mixed integer program** (MIP): A mathematical description of optimization problems.
    Solvers can use this to return an optimal solution to the problem.
    See also [mixed integer programming](https://en.wikipedia.org/wiki/Integer_programming).
- **Module**: A component that implements one set of decision criteria for the optimization problem.
    For example, the network module implements functionality to represent network traffic and latencies.
    By choosing the modules you want to use, you can configure the functionality of the optimizer.
    If a decision criteria or pricing model you need to use is not implemented yet, you can define your own modules.
- **Solver**: A program implementing multiple algorithms to solve mixed integer programs to optimality.
    Examples include [CBC](https://github.com/coin-or/Cbc) (open source), [SCIP](https://www.scipopt.org/) (open source) and [Gurobi](https://www.gurobi.com/solutions/gurobi-optimizer/) (commercial).

## Development

We use [Poetry](https://python-poetry.org/docs/#installation) as a package manager, so you have to install it to properly run the project locally.
Then you can fork and clone the repository and run `poetry install` to install all dependencies.

We use several tools to ensure a consistent level of code quality:

- Run `poetry run pytest` to run the test suit for the whole project.
- Run `poetry run mypy .` to check for typing errors.
- Run `poetry run black .` to format all Python files.
- Run `poetry run ruff .` to lint all Python files.

## License

This project is available under the terms of the [MIT license](./LICENSE)
