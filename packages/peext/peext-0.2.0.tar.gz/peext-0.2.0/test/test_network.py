from peext.scenario.network import (
    create_small_test_multinet,
    create_super_district_coupled_network,
    generate_multi_network_based_on_power_net,
)
import peext.network as network

import random
import pandapipes
import simbench


def test_from_pandapipes():
    # GIVEN
    test_network = create_small_test_multinet()

    # WHEN
    me_network = network.from_panda_multinet(test_network)

    # THEN
    assert len(me_network.nodes) == 10
    assert len(me_network.edges) == 9
    assert len(me_network.nodes[8].edges) == 3  # 8 == CHPNode
    assert me_network.nodes[8].edges["power"][0][1] == "to"
    assert me_network.nodes[8].edges["power"][0][0]._id == 1
    assert me_network.nodes[8].edges["gas"][0][1] == "to"
    assert me_network.nodes[8].edges["gas"][0][0]._id == 1
    assert me_network.nodes[8].edges["heat"][0][1] == "from"
    assert me_network.nodes[8].edges["heat"][0][0]._id == 0


def test_generated_simbench_mn():
    # GIVEN
    random.seed(10)
    pp_net = simbench.get_simbench_net("1-MV-urban--1-no_sw")
    mn = generate_multi_network_based_on_power_net(pp_net, 1 / 2, 1 / 3)

    # WHEN
    me_network = network.from_panda_multinet(mn)

    # THEN
    assert len(me_network.nodes) == 599


def test_generated_district_mn():
    # GIVEN
    random.seed(10)
    test_network = create_super_district_coupled_network(0.8)

    # WHEN
    me_network = network.from_panda_multinet(test_network)

    # THEN
    assert len(me_network.nodes) == 162


def test_write_net():
    test_network = create_super_district_coupled_network(0.8)
    pandapipes.to_pickle(test_network, "coupled_district_network_with_p2h.p")


def test_load_net():
    mn = pandapipes.from_pickle("coupled_district_network_with_p2h.p")
    _ = network.from_panda_multinet(mn)
