"""
Package for converting pandapipes/pandapower multinets to a graph network based datastructure (MENetwork)

mn = my_multinet
me_network = from_panda_multinet(mn)
"""

from peext.controller import (
    CHPControlMultiEnergy,
    RegulatedG2PControlMultiEnergy,
    RegulatedP2GControlMultiEnergy,
    RegulatedP2HControlMultiEnergy,
)
from peext.node import (
    CHPNode,
    EmptyBusNode,
    EmptyJunctionNode,
    ExtGasGrid,
    ExtPowerGrid,
    G2PNode,
    P2GNode,
    P2HNode,
    PowerLoadNode,
    GeneratorNode,
    SGeneratorNode,
    SinkNode,
    SourceNode,
    RegulatableController,
    HeatExchangerNode,
    SwitchNode,
)
from peext.edge import (
    CircPumpMassEdge,
    CircPumpPressureEdge,
    LineEdge,
    PipeEdge,
    SwitchEdge,
    TrafoEdge,
)

import pandapower as ppower

POWER_NET = "power"
GAS_NET = "gas"
HEAT_NET = "heat"
MULTI = "multi"
NETS_ACCESS = "nets"


class MENetwork:
    """
    Network representation of a pandapipes multinet. You nearly never want to create this manually. Instead use 'from_panda_multinet'
    """

    def __init__(
        self, nodes=None, edges=None, multinet=None, history_container=None
    ) -> None:
        self.__nodes = nodes
        self.__edges = edges
        self.__multinet = multinet
        self.__history_container = history_container
        pass

    def add_history_table(self, network_name, table_name, table):
        if network_name not in self.__history_container:
            self.__history_container[network_name] = {}
        if table_name not in self.__history_container[network_name]:
            self.__history_container[network_name][table_name] = []

        self.__history_container[network_name][table_name].insert(0, table)

    @property
    def multinet(self):
        """Return the underlying multinet.

        Returns:
            _type_: multinet pandapipes
        """
        return self.__multinet

    @property
    def names(self):
        """Return the names of the different energy networks in this MENetwork instance.

        Returns:
            _type_: set of strings
        """
        return self.__nodes.keys()

    @property
    def edges(self):
        """Return all edges.

        Returns:
            _type_: list of edges (EdgeModel)
        """
        all_edges = []
        for key in self.__edges.keys():
            all_edges += self.__edges[key]
        return all_edges

    @property
    def edges_as_dict(self):
        """Return all edges in a dictionary mapped from their energy network name.
        F.e. {'power', [PowerEdge...], 'gas', [GasEdge...], ...}

        Returns:
            _type_: dict
        """
        return self.__edges

    @property
    def nodes(self):
        """Return all nodes as list

        Returns:
            _type_: list (MESModel)
        """
        all_nodes = []
        for key in self.__nodes.keys():
            all_nodes += self.__nodes[key]
        return all_nodes

    def power_nodes(self):
        """Return all nodes in the power network

        Returns:
            _type_: list of MESModel
        """
        return self.__nodes[POWER_NET]

    def power_balance(self):
        """Calculates the generation/load balance of the network. SGeneratorNodes, GeneratorNodes and PowerLoadNodes will
        be considered for the calculaion. Note, losses are not considered in any way, so this can only work
        as educated guess.

        Returns:
            _type_: float
        """
        amount_gen = sum(
            [
                node.active_power() * node.regulation_factor()
                for node in list(
                    filter(
                        lambda node: isinstance(node, SGeneratorNode)
                        or isinstance(node, GeneratorNode),
                        self.__nodes[POWER_NET],
                    )
                )
            ]
        )
        amount_load = sum(
            [
                node.active_power() * node.regulation_factor()
                for node in list(
                    filter(
                        lambda node: isinstance(node, PowerLoadNode),
                        self.__nodes[POWER_NET],
                    )
                )
            ]
        )
        return amount_gen - amount_load


def find_bus_junc_for_table(node_table, node_id, network_name):
    """Find and return the bus/junction data for a specific node table + node id in a specified network.
       For example it can be used when you need to generically find the bus/junction id(s) for a specific element:

       # return the bus the generator with id = 0 in the network 'power' is connected to.
       find_bus_junc_for_table('gen', '0', 'power')

    Args:
        node_table (_type_): table name of the node
        node_id (_type_): id of the node
        network_name (_type_): name of the network

    Returns:
        _type_: list of tuple(network_name, 'bus' or 'junction', id of the cross, direction if any)
    """
    result = []
    for cross in ["bus", "junction", "to_junction", "from_junction"]:
        if cross in node_table:
            cross_id = node_table[cross][node_id]
            result.append(
                (
                    network_name,
                    cross.replace("to_", "").replace("from_", ""),
                    cross_id,
                    cross.split("_")[0],
                )
            )
    return result


def get_bus_junc(node):
    """Return the bus/junction data for a specified node. Works with controller nodes and regular nodes.

    Args:
        node (_type_): the node u want the bus data of

    Returns:
        _type_: list of tuple(network_name, 'bus' or 'junction', id of the cross, direction if any)

    """
    result = []
    if isinstance(node, RegulatableController):
        inner_nodes = node.controller.nodes
        for network_name, inner_node in inner_nodes.items():
            target_table = node.network[NETS_ACCESS][network_name][inner_node[0]]
            result += find_bus_junc_for_table(target_table, inner_node[1], network_name)
    elif isinstance(node, EmptyBusNode):
        result.append((node.network.name, "bus", node.id, ""))
    elif isinstance(node, EmptyJunctionNode):
        result.append((node.network.name, "junction", node.id, ""))
    else:
        node_table = node.network[node.component_type()]
        result += find_bus_junc_for_table(node_table, node.id, node.network.name)
    return result


def get_bus_junc_res_data(node):
    """Return the bus/junction RESULT data for a specified node. Works with controller nodes and regular nodes.

    Args:
        node (_type_): the node u want the data of

    Returns:
        _type_: dict {network_name -> list[result_row...]}
    """

    metadata_set = get_bus_junc(node)
    data_set = {}
    for network_name, cross, cross_id, _ in metadata_set:
        if network_name not in data_set:
            data_set[network_name] = []
        network = node.network
        if "nets" in node.network:
            network = node.network["nets"][network_name]
        data_set[network_name] += [network["res_" + cross].iloc[cross_id]]
    return data_set


def find_edges_controller(edges, controller):
    """Finds all edges connecting to a controller.

    Args:
        edges (_type_): all edges
        controller (_type_): the controller object

    Returns:
        _type_: dict{network_name -> list[edge_data...]}
    """
    all_edges = {}
    for key, value in controller.edges.items():
        edge_with_key = [
            (edge, value[edge.id][0], value[edge.id][2])
            for edge in edges[key]
            if edge.id in value.keys() and value[edge.id][1] == edge.component_type()
        ]
        all_edges[key] = edge_with_key
    return all_edges


def create_me_edge_tuple(edges, edge_type, key_to_from, point_name, net_name, id):
    me_edge = edges[net_name][edge_type][id]
    if me_edge is None:
        raise Exception(f"{edge_type}:{key_to_from}:{point_name}:{net_name}:{id}")
    return (
        me_edge,
        key_to_from,
        point_name,
    )


def index_edge_by_cid(
    current_cache, edges, net_name, to_junc, from_junc, edge_type, point_name, id
):
    for key in [("to", to_junc), ("from", from_junc)]:
        index = key[1]
        if index not in current_cache:
            current_cache[index] = {}
        if net_name not in current_cache[index]:
            current_cache[index][net_name] = []
        current_cache[index][net_name].append(
            create_me_edge_tuple(edges, edge_type, key[0], point_name, net_name, id)
        )


def cache_empty_cross(cross_empty_cache, net, net_name, table, point_name, index):
    if net_name not in cross_empty_cache:
        cross_empty_cache[net_name] = {}
    cross_empty_cache[net_name][net[table][point_name][index]] = True


def find_edges(
    edges, index, net, net_name, table, point_name, edge_cache, cross_empty_cache
):

    if table in ["bus", "junction"]:
        converted_index = index
    else:
        converted_index = net[table][point_name][index]

        # mark cross as not empty
        if net_name not in cross_empty_cache:
            cross_empty_cache[net_name] = {}
        cross_empty_cache[net_name][converted_index] = True

    # fast lane, will be filled when the combination of net_name, table and point_name
    # has ever been searched for
    if f"{net_name}:{table}:{point_name}" in edge_cache:
        static_entry_dict = edge_cache[f"{net_name}:{table}:{point_name}"]
        if converted_index in static_entry_dict:
            return static_entry_dict[converted_index]
        else:
            # when nodes doesn't have any edges
            return {}

    edge_cache[f"{net_name}:{table}:{point_name}"] = current_cache = {}

    if "junction" in point_name:
        for edge_type in ["pipe", "pump", "circ_pump_pressure", "circ_pump_mass"]:
            if edge_type not in net:
                continue
            for id, to_junc, from_junc in zip(
                net[edge_type].index,
                net[edge_type]["to_junction"],
                net[edge_type]["from_junction"],
            ):

                index_edge_by_cid(
                    current_cache,
                    edges,
                    net_name,
                    to_junc,
                    from_junc,
                    edge_type,
                    point_name,
                    id,
                )
    elif point_name == "bus" or point_name == "element":
        for edge_type in [
            ("line", "to_bus", "from_bus"),
            ("trafo", "lv_bus", "hv_bus"),
        ]:
            for id, to_bus, from_bus in zip(
                net[edge_type[0]].index,
                net[edge_type[0]][edge_type[1]],
                net[edge_type[0]][edge_type[2]],
            ):

                index_edge_by_cid(
                    current_cache,
                    edges,
                    net_name,
                    to_bus,
                    from_bus,
                    edge_type[0],
                    point_name,
                    id,
                )
        edge_type = ("switch", "bus", "element")
        switch_sub_df = net[edge_type[0]][net[edge_type[0]]["et"] == "b"]
        for id, to_bus, from_bus in zip(
            switch_sub_df.index,
            switch_sub_df[edge_type[1]],
            switch_sub_df[edge_type[2]],
        ):

            index_edge_by_cid(
                current_cache,
                edges,
                net_name,
                to_bus,
                from_bus,
                edge_type[0],
                point_name,
                id,
            )
    return current_cache[converted_index] if converted_index in current_cache else {}


def post(node):
    for _, edges in node.edges.items():
        for edge in edges:
            edge[0].add_node(node, edge[1], edge[2])
    return node


def check_part_of_controller(multinet, comp_index, comp_type, network_name):
    found = False
    for controller in multinet.controller["object"]:
        if (
            network_name in controller.nodes
            and comp_index == controller.nodes[network_name][1]
            and controller.nodes[network_name][0] == comp_type
        ):
            found = True
            break
    return found


def is_empty_bus(multinet, bus_id, network_name):
    connected_elements = ppower.get_connected_elements_dict(
        multinet[NETS_ACCESS][network_name], bus_id
    )
    # its about being connected to an existing node
    for type in ["bus", "line", "trafo"]:
        if type in connected_elements:
            del connected_elements[type]
    return len(connected_elements) == 0


def is_empty_cross_fastlane(cross_to_bool, cross_index, net_name):
    return cross_index not in cross_to_bool[net_name]


def is_empty_junction(multinet, junction_id, network_name):
    for type in ["sink", "source", "ext_grid"]:
        if type in multinet[NETS_ACCESS][network_name]:
            for _, row in multinet[NETS_ACCESS][network_name][type].iterrows():
                if row["junction"] == junction_id:
                    return False
    for type in ["heat_exchanger"]:
        if type in multinet[NETS_ACCESS][network_name]:
            for _, row in multinet[NETS_ACCESS][network_name][type].iterrows():
                if (
                    row["from_junction"] == junction_id
                    or row["to_junction"] == junction_id
                ):
                    return False
    return True


def merge_dict_with_lists(first, second):
    result = {**first, **second}
    for key, value in result.items():
        if key in first and key in second:
            result[key] = value + first[key]
    return result


def index_edge_by_eid(me_edge, index, net_name):
    comp_type = me_edge.component_type()
    if comp_type not in index[net_name]:
        index[net_name][comp_type] = {}
    index[net_name][comp_type][me_edge.id] = me_edge
    return me_edge


def from_panda_multinet(multinet):
    """Converting a multinet to a MENetwork. A MENetwork is a facade for a multinet, which saves the
    multinet as a graph network considering the topology of the multinet. Buses and junctions are mostly
    invisible in the MENetwork except for empty buses and junctions.

    Every component is considered a node, every line or pipe as an edge. Furthermore there are some special
    edges, for example heat_exchanger and trafos. Every node knows all its edges and the edges know their connected nodes.
    In opposite to the pandapipes/pandapower structure, controllers are considered as regular nodes. The MENetwork abstracts from
    the underlying component of a controller, therfor components which are part of the controller construction (f.e. P2G, gas source and
    power load) are not included as individual nodes but part of the controller node.

    Args:
        multinet (_type_): pandapipes multinet

    Returns:
        _type_: MENetwork
    """
    if POWER_NET in multinet[NETS_ACCESS]:
        power_net = multinet[NETS_ACCESS][POWER_NET]

    if GAS_NET in multinet[NETS_ACCESS]:
        gas_net = multinet[NETS_ACCESS][GAS_NET]

    if HEAT_NET in multinet[NETS_ACCESS]:
        heat_net = multinet[NETS_ACCESS][HEAT_NET]

    nodes = {GAS_NET: [], POWER_NET: [], HEAT_NET: [], MULTI: []}
    edges = {GAS_NET: [], POWER_NET: [], HEAT_NET: [], MULTI: []}
    history_container = {}

    me_edges_index = {GAS_NET: {}, POWER_NET: {}, HEAT_NET: {}, MULTI: {}}
    # edges
    if POWER_NET in multinet[NETS_ACCESS]:
        for i in power_net.line.index:
            edges[POWER_NET].append(
                index_edge_by_eid(
                    LineEdge(i, power_net, history_container=history_container),
                    me_edges_index,
                    POWER_NET,
                )
            )
        if "trafo" in power_net:
            for i in power_net.trafo.index:
                edges[POWER_NET].append(
                    index_edge_by_eid(
                        TrafoEdge(i, power_net, history_container=history_container),
                        me_edges_index,
                        POWER_NET,
                    )
                )
        for i in power_net.switch.index:
            if power_net.switch["et"][i] == "b":
                edges[POWER_NET].append(
                    index_edge_by_eid(
                        SwitchEdge(i, power_net, history_container=history_container),
                        me_edges_index,
                        POWER_NET,
                    )
                )

    if GAS_NET in multinet[NETS_ACCESS]:
        for i in gas_net.pipe.index:
            edges[GAS_NET].append(
                index_edge_by_eid(
                    PipeEdge(i, gas_net, history_container=history_container),
                    me_edges_index,
                    GAS_NET,
                )
            )

    if HEAT_NET in multinet[NETS_ACCESS]:
        for i in heat_net.pipe.index:
            edges[HEAT_NET].append(
                index_edge_by_eid(
                    PipeEdge(i, heat_net, history_container=history_container),
                    me_edges_index,
                    HEAT_NET,
                )
            )
        if "circ_pump_pressure" in heat_net:
            for i in heat_net.circ_pump_pressure.index:
                edges[HEAT_NET].append(
                    index_edge_by_eid(
                        CircPumpPressureEdge(
                            i, heat_net, history_container=history_container
                        ),
                        me_edges_index,
                        HEAT_NET,
                    )
                )
        if "circ_pump_mass" in heat_net:
            for i in heat_net.circ_pump_mass.index:
                edges[HEAT_NET].append(
                    index_edge_by_eid(
                        CircPumpMassEdge(
                            i, heat_net, history_container=history_container
                        ),
                        me_edges_index,
                        HEAT_NET,
                    ),
                )

    # controller
    for i, row in multinet.controller.iterrows():
        controller = row.object

        if isinstance(controller, RegulatedP2GControlMultiEnergy):
            nodes[MULTI].append(
                post(P2GNode(i, multinet, find_edges_controller(edges, controller)))
            )
        if isinstance(controller, RegulatedG2PControlMultiEnergy):
            nodes[MULTI].append(
                post(G2PNode(i, multinet, find_edges_controller(edges, controller)))
            )
        if isinstance(controller, CHPControlMultiEnergy):
            nodes[MULTI].append(
                post(CHPNode(i, multinet, find_edges_controller(edges, controller)))
            )
        if isinstance(controller, RegulatedP2HControlMultiEnergy):
            nodes[MULTI].append(
                post(P2HNode(i, multinet, find_edges_controller(edges, controller)))
            )

    edge_cache = {}
    cross_empty_cache = {GAS_NET: {}, POWER_NET: {}, HEAT_NET: {}, MULTI: {}}
    # power
    if POWER_NET in multinet[NETS_ACCESS]:
        if "load" in power_net:
            for i in power_net.load.index:
                if not check_part_of_controller(multinet, i, "load", POWER_NET):
                    nodes[POWER_NET].append(
                        post(
                            PowerLoadNode(
                                i,
                                power_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    power_net,
                                    POWER_NET,
                                    "load",
                                    "bus",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, power_net, POWER_NET, "load", "bus", i
                    )

        if "switch" in power_net:
            for i in power_net.switch.index:
                if power_net.switch["et"][i] != "b":
                    nodes[POWER_NET].append(
                        post(
                            SwitchNode(
                                i,
                                power_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    power_net,
                                    POWER_NET,
                                    "switch",
                                    "bus",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, power_net, POWER_NET, "switch", "bus", i
                    )

        if "gen" in power_net:
            for i in power_net.gen.index:
                if not check_part_of_controller(multinet, i, "gen", POWER_NET):
                    nodes[POWER_NET].append(
                        post(
                            GeneratorNode(
                                i,
                                power_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    power_net,
                                    POWER_NET,
                                    "gen",
                                    "bus",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, power_net, POWER_NET, "gen", "bus", i
                    )

        if "sgen" in power_net:
            for i in power_net.sgen.index:
                if not check_part_of_controller(multinet, i, "sgen", POWER_NET):
                    nodes[POWER_NET].append(
                        post(
                            SGeneratorNode(
                                i,
                                power_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    power_net,
                                    POWER_NET,
                                    "sgen",
                                    "bus",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, power_net, POWER_NET, "sgen", "bus", i
                    )

        if "ext_grid" in power_net:
            for i in power_net.ext_grid.index:
                if not check_part_of_controller(multinet, i, "ext_grid", POWER_NET):
                    nodes[POWER_NET].append(
                        post(
                            ExtPowerGrid(
                                i,
                                power_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    power_net,
                                    POWER_NET,
                                    "ext_grid",
                                    "bus",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, power_net, POWER_NET, "ext_grid", "bus", i
                    )

        for i in power_net.bus.index:
            if is_empty_cross_fastlane(cross_empty_cache, i, POWER_NET):
                nodes[POWER_NET].append(
                    post(
                        EmptyBusNode(
                            i,
                            power_net,
                            find_edges(
                                me_edges_index,
                                i,
                                power_net,
                                POWER_NET,
                                "bus",
                                "bus",
                                edge_cache,
                                cross_empty_cache,
                            ),
                        )
                    )
                )

    # gas

    if GAS_NET in multinet[NETS_ACCESS]:
        if "sink" in gas_net:
            for i in gas_net.sink.index:
                if not check_part_of_controller(multinet, i, "sink", GAS_NET):
                    nodes[GAS_NET].append(
                        post(
                            SinkNode(
                                i,
                                gas_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    gas_net,
                                    GAS_NET,
                                    "sink",
                                    "junction",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, gas_net, GAS_NET, "sink", "junction", i
                    )

        if "source" in gas_net:
            for i in gas_net.source.index:
                if not check_part_of_controller(multinet, i, "source", GAS_NET):
                    nodes[GAS_NET].append(
                        post(
                            SourceNode(
                                i,
                                gas_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    gas_net,
                                    GAS_NET,
                                    "source",
                                    "junction",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, gas_net, GAS_NET, "source", "junction", i
                    )

        if "ext_grid" in gas_net:
            for i in gas_net.ext_grid.index:
                if not check_part_of_controller(multinet, i, "ext_grid", GAS_NET):
                    nodes[GAS_NET].append(
                        post(
                            ExtGasGrid(
                                i,
                                gas_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    gas_net,
                                    GAS_NET,
                                    "ext_grid",
                                    "junction",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, gas_net, GAS_NET, "ext_grid", "junction", i
                    )

        for i in gas_net.junction.index:
            if is_empty_cross_fastlane(cross_empty_cache, i, GAS_NET):
                nodes[GAS_NET].append(
                    post(
                        EmptyJunctionNode(
                            i,
                            gas_net,
                            find_edges(
                                me_edges_index,
                                i,
                                gas_net,
                                GAS_NET,
                                "junction",
                                "junction",
                                edge_cache,
                                cross_empty_cache,
                            ),
                        )
                    )
                )

    # heat
    if HEAT_NET in multinet[NETS_ACCESS]:
        if "sink" in heat_net:
            for i in heat_net.sink.index:
                if not check_part_of_controller(multinet, i, "source", HEAT_NET):
                    nodes[HEAT_NET].append(
                        post(
                            SinkNode(
                                i,
                                heat_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    heat_net,
                                    HEAT_NET,
                                    "sink",
                                    "junction",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, heat_net, HEAT_NET, "sink", "junction", i
                    )

        # in heat networks you model a source as heat exchanger, therefore there is not necessarily a source
        if "source" in heat_net:
            for i in heat_net.source.index:
                if not check_part_of_controller(multinet, i, "source", HEAT_NET):
                    nodes[HEAT_NET].append(
                        post(
                            SourceNode(
                                i,
                                heat_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    heat_net,
                                    HEAT_NET,
                                    "source",
                                    "junction",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, heat_net, HEAT_NET, "source", "junction", i
                    )

        if "heat_exchanger" in heat_net:
            for i in heat_net.heat_exchanger.index:
                if not check_part_of_controller(
                    multinet, i, "heat_exchanger", HEAT_NET
                ):
                    nodes[HEAT_NET].append(
                        post(
                            HeatExchangerNode(
                                i,
                                heat_net,
                                merge_dict_with_lists(
                                    find_edges(
                                        me_edges_index,
                                        i,
                                        heat_net,
                                        HEAT_NET,
                                        "heat_exchanger",
                                        "to_junction",
                                        edge_cache,
                                        cross_empty_cache,
                                    ),
                                    find_edges(
                                        me_edges_index,
                                        i,
                                        heat_net,
                                        HEAT_NET,
                                        "heat_exchanger",
                                        "from_junction",
                                        edge_cache,
                                        cross_empty_cache,
                                    ),
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache,
                        heat_net,
                        HEAT_NET,
                        "heat_exchanger",
                        "from_junction",
                        i,
                    )
                    cache_empty_cross(
                        cross_empty_cache,
                        heat_net,
                        HEAT_NET,
                        "heat_exchanger",
                        "to_junction",
                        i,
                    )

        if "ext_grid" in heat_net:
            for i in heat_net.ext_grid.index:
                if not check_part_of_controller(multinet, i, "ext_grid", HEAT_NET):
                    nodes[HEAT_NET].append(
                        post(
                            ExtGasGrid(
                                i,
                                heat_net,
                                find_edges(
                                    me_edges_index,
                                    i,
                                    heat_net,
                                    HEAT_NET,
                                    "ext_grid",
                                    "junction",
                                    edge_cache,
                                    cross_empty_cache,
                                ),
                            )
                        )
                    )
                else:
                    cache_empty_cross(
                        cross_empty_cache, heat_net, HEAT_NET, "ext_grid", "junction", i
                    )

        for i in heat_net.junction.index:
            if is_empty_cross_fastlane(cross_empty_cache, i, HEAT_NET):
                nodes[HEAT_NET].append(
                    post(
                        EmptyJunctionNode(
                            i,
                            heat_net,
                            find_edges(
                                me_edges_index,
                                i,
                                heat_net,
                                HEAT_NET,
                                "junction",
                                "junction",
                                edge_cache,
                                cross_empty_cache,
                            ),
                        )
                    )
                )

    return MENetwork(
        nodes=nodes, edges=edges, multinet=multinet, history_container=history_container
    )
