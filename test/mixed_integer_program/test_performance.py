from optimizer.extensions.data.base_data import BaseData
from optimizer.extensions.data.performance_data import PerformanceData
from optimizer.optimizer.default import DefaultOptimizer
from test.framework import Expect


def test_with_sufficient_resources():
    """The service has enough resources to host the VM."""
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 5},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1},
                max_service_instances={},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 8},
                virtual_machine_min_cpu_count={"vm_0": 3},
                service_ram={"s_0": 8},
                service_cpu_count={"s_0": 3},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_cost(5).with_service_instance_count(
        {("s_0", 0): 1}
    ).test()


def test_with_insufficient_ram():
    """The only service does not have enough RAM for the VM."""
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 5},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1},
                max_service_instances={"s_0": 1},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 3},
                virtual_machine_min_cpu_count={"vm_0": 0},
                service_ram={"s_0": 2},
                service_cpu_count={"s_0": 10},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_infeasible().test()


def test_with_insufficient_cpu_count():
    """The only service does not have enough vCPUs for the VM."""
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 5},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1},
                max_service_instances={"s_0": 1},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 0},
                virtual_machine_min_cpu_count={"vm_0": 3},
                service_ram={"s_0": 10},
                service_cpu_count={"s_0": 2},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_infeasible().test()


def test_resource_matching():
    """Each VM has one service matching its requirements exactly.

    There is only one valid matching: Assigning each VM to their matching service.
    """
    count = 100

    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=[f"vm_{v}" for v in range(count)],
                services=[f"s_{s}" for s in range(count)],
                virtual_machine_services={
                    f"vm_{v}": [f"s_{s}" for s in range(count)] for v in range(count)
                },
                # Arbitrary costs to make sure the constraints are actually enforced
                service_base_costs={
                    f"s_{s}": (s + 4) % 7 + (s % 3) * (s % 10) for s in range(count)
                },
                time=[0],
                virtual_machine_demand={(f"vm_{v}", 0): 1 for v in range(count)},
                max_service_instances={f"s_{s}": 1 for s in range(count)},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={f"vm_{v}": v for v in range(count)},
                virtual_machine_min_cpu_count={
                    f"vm_{v}": (v + 25) % count for v in range(count)
                },
                service_ram={f"s_{s}": s for s in range(count)},
                service_cpu_count={f"s_{s}": (s + 25) % count for s in range(count)},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {(f"vm_{i}", f"s_{i}", 0): 1 for i in range(count)}
    ).test()


def test_cheap_insufficient_service():
    """There are two services, but the cheaper one has insufficient resources."""
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0", "s_1"],
                virtual_machine_services={"vm_0": ["s_0", "s_1"]},
                # Arbitrary costs to make sure the constraints are actually enforced
                service_base_costs={"s_0": 2, "s_1": 10},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1},
                max_service_instances={"s_0": 1, "s_1": 1},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 3},
                virtual_machine_min_cpu_count={"vm_0": 2},
                service_ram={"s_0": 2, "s_1": 3},
                service_cpu_count={"s_0": 1, "s_1": 2},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_1", 0): 1}
    ).with_cost(10).test()


def test_allowed_incomplete_data():
    """
    Make sure that the user is allowed to leave data undefined where it makes sense.
    """
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1},
                max_service_instances={},
            )
        )
        .with_performance_data(
            # Leave min requirements undefined
            PerformanceData(
                virtual_machine_min_ram={},
                virtual_machine_min_cpu_count={},
                service_ram={"s_0": 1},
                service_cpu_count={"s_0": 1},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible()


def test_should_work_with_higher_virtual_machine_demand():
    """Some virtual machines have a demand higher than 1."""
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 2},
                max_service_instances={},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 1},
                virtual_machine_min_cpu_count={"vm_0": 1},
                service_ram={"s_0": 2},
                service_cpu_count={"s_0": 2},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching({("vm_0", "s_0", 0): 2})


def test_should_buy_multiple_services_if_needed():
    """There are two virtual machines and one service instance can only host one VM."""
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0", "vm_1"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
                max_service_instances={},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 1},
                virtual_machine_min_cpu_count={"vm_0": 1},
                service_ram={"s_0": 1},
                service_cpu_count={"s_0": 1},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_0", 0): 1}
    ).with_service_instance_count({("s_0", 0): 2}).with_cost(2)


def test_should_be_feasible_if_service_can_be_bought_enough_times_two_instances():
    """There is demand for two VM instances, which each occupy the service fully.
    Two service instances can be bought to cover this demand.
    """
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 2},
                max_service_instances={"s_0": 2},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 1},
                virtual_machine_min_cpu_count={"vm_0": 1},
                service_ram={"s_0": 1},
                service_cpu_count={"s_0": 1},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_cost(2).with_vm_service_matching(
        {("vm_0", "s_0", 0): 2}
    ).with_service_instance_count({("s_0", 0): 2}).test()


def test_should_be_feasible_if_service_can_be_bought_enough_times_two_vms():
    """There is demand for two VMs, which each occupy the service fully.
    Two service instances can be bought to cover this demand.
    """
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0", "vm_1"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"], "vm_1": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 1, ("vm_1", 0): 1},
                max_service_instances={"s_0": 2},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 1, "vm_1": 1},
                virtual_machine_min_cpu_count={"vm_0": 1, "vm_1": 1},
                service_ram={"s_0": 1},
                service_cpu_count={"s_0": 1},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_feasible().with_cost(2).with_vm_service_matching(
        {("vm_0", "s_0", 0): 1, ("vm_1", "s_0", 0): 1}
    ).with_service_instance_count({("s_0", 0): 2}).test()


def test_should_be_infeasible_if_vms_cant_be_split():
    """There is a service with performance 3 and max instance count of 2.
    There is a demand of VMs with performance 2 and demand 3.

    In total, the two services have enough performance to serve all 3 VMs.
    But this would require to "split" one VM between the two service instances,
    which is not possible.
    """
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 3},
                max_service_instances={"s_0": 2},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 2},
                virtual_machine_min_cpu_count={"vm_0": 2},
                service_ram={"s_0": 3},
                service_cpu_count={"s_0": 3},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_infeasible().test()


def test_should_be_infeasible_if_not_enough_service_instances_can_be_bought():
    """There is demand for two VMs, which each occupy the service fully.
    But only one instance of the service may be bought.
    """
    optimizer = (
        DefaultOptimizer(
            BaseData(
                virtual_machines=["vm_0"],
                services=["s_0"],
                virtual_machine_services={"vm_0": ["s_0"]},
                service_base_costs={"s_0": 1},
                time=[0],
                virtual_machine_demand={("vm_0", 0): 2},
                max_service_instances={"s_0": 1},
            )
        )
        .with_performance_data(
            PerformanceData(
                virtual_machine_min_ram={"vm_0": 1},
                virtual_machine_min_cpu_count={"vm_0": 1},
                service_ram={"s_0": 1},
                service_cpu_count={"s_0": 1},
            )
        )
        .validate()
    )

    Expect(optimizer).to_be_infeasible().test()
