"""A bigger demo, demonstrating an example based on real-life pricing."""
import sys

from optiframe import InfeasibleError, Optimizer, SolutionObjValue
from pulp import LpMinimize

from cloud_resource_matcher.modules.base import BaseData, BaseSolution, base_module
from cloud_resource_matcher.modules.multi_cloud import (
    MultiCloudData,
    MultiCloudSolution,
    multi_cloud_module,
)
from cloud_resource_matcher.modules.network import NetworkData, network_module
from cloud_resource_matcher.modules.performance import PerformanceData, performance_module


def main() -> None:
    """Run the demo."""
    base_data = BaseData(
        cloud_services=[
            # == AWS ==
            "a1.large_us-east-1",
            "a1.xlarge_eu-west-1",
            "ebs_us-east-1",
            "ebs_eu-west-1",
            # == Google Cloud ==
            "e2-standard-4_us-central1",
            "e2-standard-2_europe-west2",
            "standard_us-central-1",
            "standard_europe-west2",
        ],
        cs_to_base_cost={
            # == AWS ==
            # Costs are entirely usage-based
            "a1.large_us-east-1": 0,
            "a1.xlarge_eu-west-1": 0,
            "ebs_us-east-1": 0,
            "ebs_eu-west-1": 0,
            # == Google Cloud ==
            # Costs are entirely usage-based
            "e2-standard-4_us-central1": 0,
            "e2-standard-2_europe-west2": 0,
            "standard_us-central-1": 0,
            "standard_europe-west2": 0,
        },
        cloud_resources=["vm-1", "vm-2", "data"],
        cr_to_instance_demand={
            "vm-1": 1,
            "vm-2": 1,
            "data": 1,
        },
        cr_to_cs_list={
            "vm-1": [
                "a1.large_us-east-1",
                "a1.xlarge_eu-west-1",
                "e2-standard-4_us-central1",
                "e2-standard-2_europe-west2",
            ],
            "vm-2": [
                "a1.large_us-east-1",
                "a1.xlarge_eu-west-1",
                "e2-standard-4_us-central1",
                "e2-standard-2_europe-west2",
            ],
            "data": [
                "ebs_us-east-1",
                "ebs_eu-west-1",
                "standard_us-central-1",
                "standard_europe-west2",
            ],
        },
    )

    performance_data = PerformanceData(
        performance_criteria=["vCPUs", "RAM", "compute", "storage"],
        performance_demand={
            # vm-1
            ("vm-1", "vCPUs"): 2,
            ("vm-1", "RAM"): 4,
            ("vm-1", "compute"): 700,  # h
            ("vm-1", "storage"): 0,
            # vm-2
            ("vm-2", "vCPUs"): 4,
            ("vm-2", "RAM"): 8,
            ("vm-2", "compute"): 200,  # h
            ("vm-2", "storage"): 0,
            # data
            ("data", "vCPUs"): 0,
            ("data", "RAM"): 0,
            ("data", "compute"): 0,
            ("data", "storage"): 100,  # GB-month
        },
        performance_supply={
            # == AWS ==
            # a1.large_us-east-1
            ("a1.large_us-east-1", "vCPUs"): 2,
            ("a1.large_us-east-1", "RAM"): 4,
            ("a1.large_us-east-1", "compute"): sys.maxsize,
            ("a1.large_us-east-1", "storage"): 0,
            # a1.xlarge_eu-west-1
            ("a1.xlarge_eu-west-1", "vCPUs"): 4,
            ("a1.xlarge_eu-west-1", "RAM"): 8,
            ("a1.xlarge_eu-west-1", "compute"): sys.maxsize,
            ("a1.xlarge_eu-west-1", "storage"): 0,
            # ebs_us-east-1
            ("ebs_us-east-1", "vCPUs"): 0,
            ("ebs_us-east-1", "RAM"): 0,
            ("ebs_us-east-1", "compute"): 0,
            ("ebs_us-east-1", "storage"): sys.maxsize,
            # ebs_eu-west-1
            ("ebs_eu-west-1", "vCPUs"): 0,
            ("ebs_eu-west-1", "RAM"): 0,
            ("ebs_eu-west-1", "compute"): 0,
            ("ebs_eu-west-1", "storage"): sys.maxsize,
            # == Google Cloud ==
            # e2-standard-4_us-central1
            ("e2-standard-4_us-central1", "vCPUs"): 4,
            ("e2-standard-4_us-central1", "RAM"): 16,
            ("e2-standard-4_us-central1", "compute"): sys.maxsize,
            ("e2-standard-4_us-central1", "storage"): 0,
            # e2-standard-2_europe-west2
            ("e2-standard-2_europe-west2", "vCPUs"): 2,
            ("e2-standard-2_europe-west2", "RAM"): 8,
            ("e2-standard-2_europe-west2", "compute"): sys.maxsize,
            ("e2-standard-2_europe-west2", "storage"): 0,
            # standard_us-central-1
            ("standard_us-central-1", "vCPUs"): 0,
            ("standard_us-central-1", "RAM"): 0,
            ("standard_us-central-1", "compute"): 0,
            ("standard_us-central-1", "storage"): sys.maxsize,
            # standard_europe-west2
            ("standard_europe-west2", "vCPUs"): 0,
            ("standard_europe-west2", "RAM"): 0,
            ("standard_europe-west2", "compute"): 0,
            ("standard_europe-west2", "storage"): sys.maxsize,
        },
        cost_per_unit={
            # == AWS ==
            ("a1.large_us-east-1", "compute"): 0.051,  # per h
            ("a1.xlarge_eu-west-1", "compute"): 0.1152,  # per h
            ("ebs_us-east-1", "storage"): 0.08,  # per GB-month
            ("ebs_eu-west-1", "storage"): 0.0928,  # per GB-month
            # == Google Cloud ==
            ("e2-standard-4_us-central1", "compute"): 0.134012,  # per h
            ("e2-standard-2_europe-west2", "compute"): 0.086334,  # per h
            ("standard_us-central-1", "storage"): 0.020,  # per GB-month
            ("standard_europe-west2", "storage"): 0.023,  # per GB-month
        },
    )

    locations = {"aws_eu-west-1", "aws_us-east-1", "gc_europe-west2", "gc_us-central1"}

    network_data = NetworkData(
        locations=locations,
        cs_to_loc={
            # == AWS ==
            "a1.large_us-east-1": "aws_us-east-1",
            "a1.xlarge_eu-west-1": "aws_eu-west-1",
            "ebs_us-east-1": "aws_us-east-1",
            "ebs_eu-west-1": "aws_eu-west-1",
            # == Google Cloud ==
            "e2-standard-4_us-central1": "gc_us-central1",
            "e2-standard-2_europe-west2": "gc_europe-west2",
            "standard_us-central-1": "gc_us-central1",
            "standard_europe-west2": "gc_europe-west2",
        },
        cr_and_cr_to_traffic={
            ("vm-1", "vm-2"): 10,  # per month
            ("vm-2", "data"): 100,  # per month
            ("data", "vm-2"): 250,  # per month
        },
        loc_and_loc_to_cost={
            # == AWS ==
            # aws_eu-west-1
            ("aws_eu-west-1", "aws_eu-west-1"): 0.01,
            ("aws_eu-west-1", "aws_us-east-1"): 0.02,
            ("aws_eu-west-1", "gc_europe-west2"): 0.09,
            ("aws_eu-west-1", "gc_us-central1"): 0.09,
            # aws_us-east-1
            ("aws_us-east-1", "aws_eu-west-1"): 0.02,
            ("aws_us-east-1", "aws_us-east-1"): 0.01,
            ("aws_us-east-1", "gc_europe-west2"): 0.09,
            ("aws_us-east-1", "gc_us-central1"): 0.09,
            # == Google Cloud ==
            # gc_europe-west2
            ("gc_europe-west2", "aws_eu-west-1"): 0.12,
            ("gc_europe-west2", "aws_us-east-1"): 0.12,
            ("gc_europe-west2", "gc_europe-west2"): 0.0,
            ("gc_europe-west2", "gc_us-central1"): 0.08,
            # gc_us-central1
            ("gc_us-central1", "aws_eu-west-1"): 0.12,
            ("gc_us-central1", "aws_us-east-1"): 0.12,
            ("gc_us-central1", "gc_europe-west2"): 0.08,
            ("gc_us-central1", "gc_us-central1"): 0.0,
        },
        loc_and_loc_to_latency={(loc1, loc2): 0 for loc1 in locations for loc2 in locations},
        cr_and_loc_to_traffic={},
        cr_and_loc_to_max_latency={},
        cr_and_cr_to_max_latency={},
    )

    multi_cloud_data = MultiCloudData(
        cloud_service_providers=["aws", "google-cloud"],
        csp_to_cs_list={
            "aws": [
                "a1.large_us-east-1",
                "a1.xlarge_eu-west-1",
                "ebs_us-east-1",
                "ebs_eu-west-1",
            ],
            "google-cloud": [
                "e2-standard-4_us-central1",
                "e2-standard-2_europe-west2",
                "standard_us-central-1",
                "standard_europe-west2",
            ],
        },
        csp_to_cost={
            "aws": 0,
            "google-cloud": 0,
        },
        max_csp_count=2,
        min_csp_count=1,
    )

    optimizer = (
        # Create a new optimizer, minimizing the costs
        Optimizer("Modular Demo", LpMinimize)
        # Add the needed modules to solve the problem
        .add_modules(base_module, performance_module, network_module, multi_cloud_module)
        # Initialize the data of the problem instance
        .initialize(base_data, performance_data, network_data, multi_cloud_data)
    )

    try:
        # Solve the problem
        solution_data = optimizer.solve()
    except InfeasibleError:
        print("The given problem is infeasible!")
        exit(1)

    # Extract the solution
    cost = solution_data[SolutionObjValue].objective_value
    base_solution: BaseSolution = solution_data[BaseSolution]
    multi_cloud_solution: MultiCloudSolution = solution_data[MultiCloudSolution]

    print(f"Total cost: {cost:.2f}")
    print(f"Matching: {base_solution.cr_to_cs_matching}")
    print(f"Selected CSPs: {multi_cloud_solution.selected_csps}")


if __name__ == "__main__":
    main()
