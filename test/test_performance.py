from optimizer.data.base_data import BaseData
from optimizer.data.performance_data import PerformanceData
from optimizer.model import Model
from test.framework import Expect


def test_with_sufficient_resources():
    """The service has enough resources to host the VM."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
    )

    model = Model(base_data.validate()).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_0": 8},
            virtual_machine_min_cpu_count={"vm_0": 3},
            service_ram={"s_0": 8},
            service_cpu_count={"s_0": 3},
        ).validate(base_data)
    )

    Expect(model).to_be_feasible().with_cost(5).test()


def test_with_insufficient_ram():
    """The only service does not have enough RAM for the VM."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
    )

    model = Model(base_data.validate()).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_0": 3},
            virtual_machine_min_cpu_count={"vm_0": 0},
            service_ram={"s_0": 2},
            service_cpu_count={"s_0": 10},
        ).validate(base_data)
    )

    Expect(model).to_be_infeasible().test()


def test_with_insufficient_cpu_count():
    """The only service does not have enough vCPUs for the VM."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 5},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
    )

    model = Model(base_data.validate()).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_0": 0},
            virtual_machine_min_cpu_count={"vm_0": 3},
            service_ram={"s_0": 10},
            service_cpu_count={"s_0": 2},
        ).validate(base_data)
    )

    Expect(model).to_be_infeasible().test()


def test_resource_matching():
    """Each VM has one service matching its requirements exactly.

    There is only one valid matching: Assigning each VM to their matching service.
    """
    count = 100

    base_data = BaseData(
        virtual_machines=[f"vm_{v}" for v in range(count)],
        services=[f"s_{s}" for s in range(count)],
        virtual_machine_services={
            f"vm_{v}": [f"s_{s}" for s in range(count)] for v in range(count)
        },
        # Some arbitrary costs to make sure the constraints are actually enforced
        service_base_costs={
            f"s_{s}": (s + 4) % 7 + (s % 3) * (s % 10) for s in range(count)
        },
        time=[0],
        virtual_machine_demand={(f"vm_{v}", 0): 1 for v in range(count)},
    )

    model = Model(base_data.validate()).with_performance(
        PerformanceData(
            virtual_machine_min_ram={f"vm_{v}": v for v in range(count)},
            virtual_machine_min_cpu_count={
                f"vm_{v}": (v + 25) % count for v in range(count)
            },
            service_ram={f"s_{s}": s for s in range(count)},
            service_cpu_count={f"s_{s}": (s + 25) % count for s in range(count)},
        ).validate(base_data)
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {(f"vm_{i}", f"s_{i}", 0): 1 for i in range(count)}
    ).test()


def test_cheap_insufficient_service():
    """There are two services, but the cheaper one has insufficient resources."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0", "s_1"],
        virtual_machine_services={"vm_0": ["s_0", "s_1"]},
        # Some arbitrary costs to make sure the constraints are actually enforced
        service_base_costs={"s_0": 2, "s_1": 10},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
    )

    model = Model(base_data.validate()).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_0": 3},
            virtual_machine_min_cpu_count={"vm_0": 2},
            service_ram={"s_0": 2, "s_1": 3},
            service_cpu_count={"s_0": 1, "s_1": 2},
        ).validate(base_data)
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {("vm_0", "s_1", 0): 1}
    ).with_cost(10).test()


def test_allowed_incomplete_data():
    """Make sure that the user is allowed to leave data undefined where it makes sense."""
    base_data = BaseData(
        virtual_machines=["vm_0"],
        services=["s_0"],
        virtual_machine_services={"vm_0": ["s_0"]},
        service_base_costs={"s_0": 1},
        time=[0],
        virtual_machine_demand={("vm_0", 0): 1},
    )

    model = Model(base_data.validate()).with_performance(
        # Leave min requirements undefined
        PerformanceData(
            virtual_machine_min_ram={},
            virtual_machine_min_cpu_count={},
            service_ram={"s_0": 1},
            service_cpu_count={"s_0": 1},
        ).validate(base_data)
    )

    Expect(model).to_be_feasible()
