from optiframe import Optimizer

from optimizer.packages.base import BaseData, base_package
from optimizer.packages.performance import PerformanceData, performance_package
from test.framework import Expect


OPTIMIZER = Optimizer("test_performance").add_package(base_package).add_package(performance_package)


def test_with_sufficient_resources() -> None:
    """The service has enough resources to host the VM."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        ),
        PerformanceData(
            performance_criteria=["vCPU", "RAM"],
            performance_demand={("vm_0", "vCPU"): 8, ("vm_0", "RAM"): 3},
            performance_supply={("s_0", "vCPU"): 8, ("s_0", "RAM"): 4},
        ),
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_service_instance_count(
        {("s_0", 0): 1}
    ).test()


def test_with_insufficient_performance() -> None:
    """The only service does not have enough RAM for the VM."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 5},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={"s_0": 1},
        ),
        PerformanceData(
            performance_criteria=["vCPU", "RAM"],
            performance_demand={("vm_0", "vCPU"): 8, ("vm_0", "RAM"): 3},
            performance_supply={("s_0", "vCPU"): 8, ("s_0", "RAM"): 2},
        ),
    )

    Expect(optimizer).to_be_infeasible().test()


def test_resource_matching() -> None:
    """Each VM has one service matching its requirements exactly.

    There is only one valid matching: Assigning each VM to their matching service.
    """
    count = 100

    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=[f"vm_{v}" for v in range(count)],
            services=[f"s_{s}" for s in range(count)],
            virtual_machine_services={
                f"vm_{v}": [f"s_{s}" for s in range(count)] for v in range(count)
            },
            # Arbitrary costs to make sure the constraints are actually enforced
            service_base_costs={f"s_{s}": (s + 4) % 7 + (s % 3) * (s % 10) for s in range(count)},
            time=[0],
            virtual_machine_demand={(f"vm_{v}", 0): 1 for v in range(count)},
            max_service_instances={f"s_{s}": 1 for s in range(count)},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={(f"vm_{v}", "RAM"): v for v in range(count)},
            performance_supply={(f"s_{s}", "RAM"): s for s in range(count)},
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {(f"vm_{i}", f"s_{i}", 0): 1 for i in range(count)}
    ).test()


def test_cheap_insufficient_service() -> None:
    """There are two services, but the cheaper one has insufficient resources."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0", "s_1"],
            virtual_machine_services={"vm_0": ["s_0", "s_1"]},
            # Arbitrary costs to make sure the constraints are actually enforced
            service_base_costs={"s_0": 2, "s_1": 10},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={"s_0": 1, "s_1": 1},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={("vm_0", "RAM"): 3},
            performance_supply={("s_0", "RAM"): 2, ("s_1", "RAM"): 3},
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching({("vm_0", "s_1", 0): 1}).with_cost(
        10
    ).test()


def test_allowed_incomplete_data() -> None:
    """
    Make sure that the user is allowed to leave data undefined where it makes sense.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 1},
            max_service_instances={},
        ),
        # Leave min requirements undefined
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={},
            performance_supply={("s_0", "RAM"): 1},
        ),
    )

    Expect(optimizer).to_be_feasible()


def test_should_work_with_higher_virtual_machine_demand() -> None:
    """Some virtual machines have a demand higher than 1."""
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 2},
            max_service_instances={},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={("vm_0", "RAM"): 3},
            performance_supply={("s_0", "RAM"): 3},
        ),
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching({("vm_0", "s_0", 0): 2})


def test_should_be_infeasible_if_not_enough_service_instances_can_be_bought() -> None:
    """There is demand for two VMs, which each occupy the service fully.
    But only one instance of the service may be bought.
    """
    optimizer = OPTIMIZER.initialize(
        BaseData(
            virtual_machines=["vm_0"],
            services=["s_0"],
            virtual_machine_services={"vm_0": ["s_0"]},
            service_base_costs={"s_0": 1},
            time=[0],
            virtual_machine_demand={("vm_0", 0): 2},
            max_service_instances={"s_0": 1},
        ),
        PerformanceData(
            performance_criteria=["RAM"],
            performance_demand={("vm_0", "RAM"): 1},
            performance_supply={("s_0", "RAM"): 1},
        ),
    )

    Expect(optimizer).to_be_infeasible().test()
