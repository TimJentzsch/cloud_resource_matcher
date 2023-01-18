from optimizer.data.base_data import BaseData
from optimizer.data.network_data import NetworkData
from optimizer.data.performance_data import PerformanceData
from optimizer.data.multi_cloud_data import MultiCloudData
from optimizer.model import Model, SolveError
from optimizer.solver import Solver


def main():
    vm_count = 50
    service_count = 50
    time_count = 500
    csp_count = 3
    location_count = 5

    base_data = BaseData(
        virtual_machines=[f"vm_{v}" for v in range(vm_count)],
        services=[f"service_{s}" for s in range(service_count)],
        service_base_costs={
            f"service_{s}": s % 100 + (s % 20) * (s % 5) + 10
            for s in range(service_count)
        },
        virtual_machine_services={
            f"vm_{v}": [
                f"service_{s}" for s in range(service_count) if ((v + s) % 4) == 0
            ]
            for v in range(vm_count)
        },
        time=list(range(time_count)),
        virtual_machine_demand={
            (f"vm_{v}", t): (v % 2) * (t % 3) + 1
            for v in range(vm_count)
            for t in range(time_count)
        },
    )

    # TODO: Fix this making the model infeasible
    perf_data = PerformanceData(
        virtual_machine_min_ram={f"vm_{v}": (v % 4) * 2 + 1 for v in range(vm_count)},
        virtual_machine_min_cpu_count={
            # f"vm_{v}": (v + 2) % 5 + 1 for v in range(vm_count)
        },
        service_ram={f"service_{s}": (s + 4) % 30 + 5 for s in range(service_count)},
        service_cpu_count={f"service_{s}": s % 23 + 1 for s in range(service_count)},
    )

    multi_data = MultiCloudData(
        cloud_service_providers=[f"csp_{k}" for k in range(csp_count)],
        cloud_service_provider_services={
            f"csp_{k}": [
                f"service_{s}" for s in range(service_count) if s % csp_count == k
            ]
            for k in range(csp_count)
        },
        min_cloud_service_provider_count=2,
        max_cloud_service_provider_count=3,
    )

    network_data = NetworkData(
        locations=set(f"loc_{loc}" for loc in range(location_count)),
        service_location={
            f"service_{s}": f"loc_{s % location_count}" for s in range(service_count)
        },
        location_latency={
            (f"loc_{loc1}", f"loc_{loc2}"): abs(loc2 - loc1) * 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        location_traffic_cost={
            (f"loc_{loc1}", f"loc_{loc2}"): 0
            if loc1 == loc2
            else (loc1 + loc2 * 2) % 20 + 5
            for loc1 in range(location_count)
            for loc2 in range(location_count)
        },
        virtual_machine_location_traffic={
            (f"vm_{v}", f"loc_{loc}"): abs(loc - v) if loc % 4 == v % 2 else 0
            for v in range(vm_count)
            for loc in range(location_count)
        },
        virtual_machine_location_max_latency={
            (f"vm_{v}", f"loc_{loc}"): v % 20 + 10
            for v in range(vm_count)
            for loc in range(location_count)
        },
        virtual_machine_virtual_machine_max_latency={},
        virtual_machine_virtual_machine_traffic={},
    )

    model = (
        Model(base_data.validate())
        # .with_performance(perf_data.validate(base_data))
        .with_multi_cloud(multi_data.validate(base_data)).with_network(
            network_data.validate(base_data)
        )
    )

    try:
        solution = model.solve(solver=Solver.DEFAULT)
        print("=== SOLUTION FOUND ===\n")
        print(f"Cost: {solution.cost}")
    except SolveError as e:
        print("=== PROBLEM INFEASIBLE ===\n")
        print(f"{e.reason}")
        exit(101)
