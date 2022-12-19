from optimizer.data import BaseData, PerformanceData, MultiCloudData
from optimizer.model import Model


def main():
    VM_COUNT = 10
    SERVICE_COUNT = 30
    CSP_COUNT = 3

    base_data = BaseData(
        virtual_machines=[f"vm_{v}" for v in range(VM_COUNT)],
        services=[f"service_{s}" for s in range(SERVICE_COUNT)],
        service_base_costs={f"service_{s}": s % 10 + 10 for s in range(SERVICE_COUNT)},
        virtual_machine_services={
            f"vm_{v}": [
                f"service_{s}" for s in range(SERVICE_COUNT) if ((v + s) % 4) == 0
            ]
            for v in range(VM_COUNT)
        },
    )

    perf_data = PerformanceData(
        virtual_machine_min_ram={f"vm_{v}": (v % 4) * 2 + 1 for v in range(VM_COUNT)},
        virtual_machine_min_cpu_count={
            f"vm_{v}": (v + 2) % 5 + 1 for v in range(VM_COUNT)
        },
        service_ram={f"service_{s}": (s + 4) % 10 + 1 for s in range(SERVICE_COUNT)},
        service_cpu_count={f"service_{s}": s % 7 + 1 for s in range(SERVICE_COUNT)},
    )

    multi_data = MultiCloudData(
        cloud_service_providers=[f"csp_{k}" for k in range(CSP_COUNT)],
        cloud_service_provider_services={
            f"csp_{k}": [
                f"service_{s}" for s in range(SERVICE_COUNT) if s % CSP_COUNT == k
            ]
            for k in range(CSP_COUNT)
        },
        min_cloud_service_provider_count=2,
        max_cloud_service_provider_count=3,
    )

    print(base_data)
    print(perf_data)
    print(multi_data)

    model = Model(base_data).with_performance(perf_data).with_multi_cloud(multi_data)

    solution = model.solve()
    print(solution)
