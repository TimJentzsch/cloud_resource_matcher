from optimizer.data import BaseData, PerformanceData
from optimizer.model import Model
from test.framework import Expect


def test_with_sufficient_resources():
    """The service has enough resources to host the VM."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": ["s_1"]},
            service_base_costs={"s_1": 5},
        )
    ).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_1": 8},
            virtual_machine_min_cpu_count={"vm_1": 3},
            service_ram={"s_1": 8},
            service_cpu_count={"s_1": 3},
        )
    )

    Expect(model).to_be_feasible().with_cost(5).test()


def test_with_insufficient_ram():
    """The only service does not have enough RAM for the VM."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": ["s_1"]},
            service_base_costs={"s_1": 5},
        )
    ).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_1": 3},
            virtual_machine_min_cpu_count={"vm_1": 0},
            service_ram={"s_1": 2},
            service_cpu_count={"s_1": 10},
        )
    )

    Expect(model).to_be_infeasible().test()


def test_with_insufficient_cpu_count():
    """The only service does not have enough vCPUs for the VM."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1"],
            virtual_machine_services={"vm_1": ["s_1"]},
            service_base_costs={"s_1": 5},
        )
    ).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_1": 0},
            virtual_machine_min_cpu_count={"vm_1": 3},
            service_ram={"s_1": 10},
            service_cpu_count={"s_1": 2},
        )
    )

    Expect(model).to_be_infeasible().test()


def test_resource_matching():
    """Each VM has one service matching its requirements exactly.

    There is only one valid matching: Assigning each VM to their matching service.
    """
    count = 100

    model = Model(
        BaseData(
            virtual_machines=[f"vm_{v}" for v in range(count)],
            services=[f"s_{s}" for s in range(count)],
            virtual_machine_services={
                f"vm_{v}": [f"s_{s}" for s in range(count)] for v in range(count)
            },
            # Some arbitrary costs to make sure the constraints are actually enforced
            service_base_costs={
                f"s_{s}": (s + 4) % 7 + (s % 3) * (s % 10) for s in range(count)
            },
        )
    ).with_performance(
        PerformanceData(
            virtual_machine_min_ram={f"vm_{v}": v for v in range(count)},
            virtual_machine_min_cpu_count={
                f"vm_{v}": (v + 25) % count for v in range(count)
            },
            service_ram={f"s_{s}": s for s in range(count)},
            service_cpu_count={f"s_{s}": (s + 25) % count for s in range(count)},
        )
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {f"vm_{i}": f"s_{i}" for i in range(count)}
    ).test()


def test_cheap_insufficient_service():
    """There are two services, but the cheaper one has insufficient resources."""
    model = Model(
        BaseData(
            virtual_machines=["vm_1"],
            services=["s_1", "s_2"],
            virtual_machine_services={"vm_1": ["s_1", "s_2"]},
            # Some arbitrary costs to make sure the constraints are actually enforced
            service_base_costs={"s_1": 2, "s_2": 10},
        )
    ).with_performance(
        PerformanceData(
            virtual_machine_min_ram={"vm_1": 3},
            virtual_machine_min_cpu_count={"vm_1": 2},
            service_ram={"s_1": 2, "s_2": 3},
            service_cpu_count={"s_1": 1, "s_2": 2},
        )
    )

    Expect(model).to_be_feasible().with_vm_service_matching(
        {f"vm_1": f"s_2"}
    ).with_cost(10).test()
