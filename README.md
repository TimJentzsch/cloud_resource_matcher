# Optimizer

An optimizer for cloud computing costs, using mixed integer programming.

## Prerequisites

- [Python](https://www.python.org/downloads/) >=3.11
- [Poetry](https://python-poetry.org/docs/#installation) (package manager)

## Installation

- Clone the repository (or a fork of the repository if you plan to make changes)
- Run `poetry install` to install the dependencies

## Usage

### Demo

Run `poetry run start` to solve an artificially created cloud cost problem.
See `poetry run start --help` for the available configuration options.

### Code Quality

- Run `poetry run pytest` to run the test suit for the whole project.
- Run `poetry run pyright` to check for typing errors.
- Run `poetry run black .` to format all Python files.
- Run `poetry run ruff .` to lint all Python files.

## Configuring a Solver

The optimizer supports multiple solvers:

- CBC (included in PuLP, default)
- SCIP
- Gurobi

Take a look at [this documentation](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html) for instructions on how to install and configure the solvers.

Once set up, you can specify the `--solver` command line option to change the solver.
