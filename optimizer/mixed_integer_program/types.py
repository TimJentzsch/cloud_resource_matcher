from pulp import LpVariable

from optimizer.optimizer_toolbox_model.data import VirtualMachine, Service, TimeUnit

VarVmServiceMatching = dict[tuple[VirtualMachine, Service], LpVariable]

VmServiceMatching = dict[tuple[VirtualMachine, Service, TimeUnit], int]
ServiceInstanceCount = dict[tuple[Service, TimeUnit], int]

ServiceVirtualMachines = dict[Service, set[VirtualMachine]]
