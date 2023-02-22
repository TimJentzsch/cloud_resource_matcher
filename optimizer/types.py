from pulp import LpVariable

from optimizer.extensions.data.types import Service, VirtualMachine, TimeUnit

VarVmServiceMatching = dict[tuple[VirtualMachine, Service], LpVariable]

VmServiceMatching = dict[tuple[VirtualMachine, Service, TimeUnit], int]
ServiceInstanceCount = dict[tuple[Service, TimeUnit], int]

ServiceVirtualMachines = dict[Service, set[VirtualMachine]]
