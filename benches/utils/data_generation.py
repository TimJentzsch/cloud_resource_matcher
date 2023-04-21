from optimizer.packages.base.data import CloudService, BaseData, CloudResource
from optimizer.packages.network import NetworkData
from optimizer.packages.network.data import Location


def generate_base_data(cr_count: int, cs_count: int, cs_count_per_cr: int) -> BaseData:
    assert cs_count_per_cr <= cs_count

    cloud_resources = [f"cr_{cr}" for cr in range(cr_count)]
    cloud_services = [f"cs_{cs}" for cs in range(cs_count)]

    cr_to_cs_list = dict()

    for cr_num, cr in enumerate(cloud_resources):
        cs_list: set[CloudService] = set()

        for i in range(cs_count_per_cr):
            idx = (i * 119428 + 3 * cr_num + 83) % cs_count
            j = 0

            while len(cs_list) < i + 1:
                cs_list.add(cloud_services[(idx + j) % cs_count])
                j += 1

        cr_to_cs_list[cr] = list(cs_list)

    base_data = BaseData(
        cloud_resources=cloud_resources,
        cloud_services=cloud_services,
        cs_to_base_cost={
            f"cs_{cs}": cs % 100 + (cs % 20) * (cs % 5) + 10 for cs in range(cs_count)
        },
        cr_to_cs_list=cr_to_cs_list,
        cr_to_instance_demand={f"cr_{cr}": (cr % 4) * 250 + 1 for cr in range(cr_count)},
    )

    assert (
        len(base_data.cloud_resources) == cr_count
    ), f"cr_count {len(base_data.cloud_resources)} != {cr_count}"
    assert (
        len(base_data.cloud_services) == cs_count
    ), f"cs_count {len(base_data.cloud_services)} != {cs_count}"

    for cr in base_data.cloud_resources:
        count = len(base_data.cr_to_cs_list[cr])
        assert count == cs_count_per_cr, f"cs_count_per_cr({cr}) {count} != {cs_count_per_cr}"

    return base_data


def generate_network_data(
    cr_count: int,
    cs_count: int,
    loc_count: int,
    cr_to_loc_connections: int,
    cr_to_cr_connections: int,
) -> NetworkData:
    locations = set(f"loc_{loc}" for loc in range(loc_count))
    cr_and_loc_to_traffic: dict[tuple[CloudResource, Location], int] = dict()
    cr_and_cr_to_traffic: dict[tuple[CloudResource, Location], int] = dict()

    for i in range(cr_to_loc_connections):
        cr = (i * 1239 + i) % cr_count
        loc = (i * 912 + 32) % loc_count
        j = 0

        while len(cr_and_loc_to_traffic.keys()) < i + 1:
            cr = (cr + j) % cr_count
            loc = (loc + j + j % 2) % loc_count

            cr_and_loc_to_traffic[(f"cr_{cr}", f"loc_{loc}")] = abs(loc - cr)

            j += 1

    for i in range(cr_to_cr_connections):
        cr1 = (i * 2234 + i) % cr_count
        cr2 = (i * i + 5 * i + 992) % cr_count
        j = 0

        while len(cr_and_cr_to_traffic.keys()) < i + 1:
            cr1 = (cr1 + j) % cr_count
            cr2 = (cr2 + j + j % 2) % cr_count

            cr_and_cr_to_traffic[(f"cr_{cr1}", f"cr_{cr2}")] = (cr1 + cr2 + i) % 500

            j += 1

    network_data = NetworkData(
        locations=locations,
        cs_to_loc={f"cs_{cs}": f"loc_{cs % loc_count}" for cs in range(cs_count)},
        loc_and_loc_to_latency={
            (f"loc_{loc1}", f"loc_{loc2}"): abs(loc2 - loc1) % 40
            for loc1 in range(loc_count)
            for loc2 in range(loc_count)
        },
        loc_and_loc_to_cost={
            (f"loc_{loc1}", f"loc_{loc2}"): 0 if loc1 == loc2 else (loc1 + loc2 * 2) % 20 + 5
            for loc1 in range(loc_count)
            for loc2 in range(loc_count)
        },
        cr_and_loc_to_traffic=cr_and_loc_to_traffic,
        cr_and_cr_to_traffic=cr_and_cr_to_traffic,
        # Max latency only reduces the model size
        cr_and_loc_to_max_latency=dict(),
        cr_and_cr_to_max_latency=dict(),
    )

    assert len(locations) == loc_count, f"loc_count {len(locations)} != {loc_count}"
    assert (
        len(cr_and_loc_to_traffic.keys()) == cr_to_loc_connections
    ), f"cr_and_loc_to_traffic {len(cr_and_loc_to_traffic.keys())} != {cr_to_loc_connections}"
    assert (
        len(cr_and_cr_to_traffic.keys()) == cr_to_cr_connections
    ), f"cr_and_cr_to_traffic {len(cr_and_cr_to_traffic.keys())} != {cr_to_cr_connections}"

    return network_data
