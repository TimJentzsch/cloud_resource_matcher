from optimizer.data import BaseData, PerformanceData, MultiCloudData
from optimizer.model import Model, SolveError
from optimizer.solver import Solver


def main():
    vm_count = 50
    service_count = 500
    time_count = 50
    csp_count = 3

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

    perf_data = PerformanceData(
        virtual_machine_min_ram={f"vm_{v}": (v % 4) * 2 + 1 for v in range(vm_count)},
        virtual_machine_min_cpu_count={
            f"vm_{v}": (v + 2) % 5 + 1 for v in range(vm_count)
        },
        service_ram={f"service_{s}": (s + 4) % 30 + 1 for s in range(service_count)},
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

    model = Model(base_data).with_performance(perf_data).with_multi_cloud(multi_data)

    try:
        solution = model.validate_and_solve(solver=Solver.DEFAULT)
        print("=== SOLUTION FOUND ===\n")
        print(f"Cost: {solution.cost}")
    except SolveError as e:
        print("=== PROBLEM INFEASIBLE ===\n")
        print(f"{e.reason}")
