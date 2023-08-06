

import pandapipes as ppipes
import pandapower as ppower

from peext.controller import CHPControlMultiEnergy, RegulatedG2PControlMultiEnergy, RegulatedP2GControlMultiEnergy, create_chp, create_g2p, create_p2g, create_p2h
from peext.scenario.network import create_small_test_multinet


def test_g2p_controller():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    gas_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    g_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    controller_testee = RegulatedG2PControlMultiEnergy(mn, g_gen, gas_sink, 0.8, "TEST_G2P")
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928
    
def test_g2p_controller_convenience():
    # GIVEN
    mn = create_small_test_multinet()
    controller_testee = create_g2p(mn, 0, 0, 0.085)
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928

def test_g2p_controller_regulation():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    gas_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    g_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    controller_testee = RegulatedG2PControlMultiEnergy(mn, g_gen, gas_sink, 0.8, "TEST_G2P")
    controller_testee.regulation = 0.95
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons * controller_testee.regulation
    assert controller_testee.get_power_production(mn) == 2.7419079816000003

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons * controller_testee.regulation
    assert controller_testee.get_power_production(mn) == 2.7419079816000003

def test_chp():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    heat_net = mn['nets']['heat']
    chp_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    chp_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    chp_heat_feed_in = ppipes.create_heat_exchanger(heat_net, from_junction=0, to_junction=1, diameter_m=200e-3, qext_w=-10000)
    controller_testee = CHPControlMultiEnergy(mn, chp_gen, chp_sink, chp_heat_feed_in, 0.8, "TEST_CHP", ambient_temperature=282.5)
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928
    assert controller_testee.get_heat_production(mn) == -1936.4058895341723

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928 #mW
    assert controller_testee.get_heat_production(mn) == -1936.4058895341723 #W

def test_chp_convenience():
    # GIVEN
    mn = create_small_test_multinet()
    controller_testee = create_chp(mn, 0, 0, 0, 1, 0.085)
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928
    assert controller_testee.get_heat_production(mn) == -1936.4058895341723

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons
    assert controller_testee.get_power_production(mn) == 2.886218928 #mW
    assert controller_testee.get_heat_production(mn) == -1936.4058895341723 #W

def test_chp_regulated():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    heat_net = mn['nets']['heat']
    chp_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    chp_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    chp_heat_feed_in = ppipes.create_heat_exchanger(heat_net, from_junction=0, to_junction=1, diameter_m=200e-3, qext_w=-10000)
    controller_testee = CHPControlMultiEnergy(mn, chp_gen, chp_sink, chp_heat_feed_in, 0.8, "TEST_CHP", ambient_temperature=282.5)
    controller_testee.regulation = 0.5
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons * controller_testee.regulation
    assert controller_testee.get_power_production(mn) == 2.886218928 * controller_testee.regulation
    assert controller_testee.get_heat_production(mn) == -1443.2870697670862

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons * controller_testee.regulation
    assert controller_testee.get_power_production(mn) == 2.886218928 * controller_testee.regulation
    assert controller_testee.get_heat_production(mn) == -1443.2870697670862


def test_chp_heat_regulated():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    heat_net = mn['nets']['heat']
    chp_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    chp_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    chp_heat_feed_in = ppipes.create_heat_exchanger(heat_net, from_junction=0, to_junction=1, diameter_m=200e-3, qext_w=-10000)
    controller_testee = CHPControlMultiEnergy(mn, chp_gen, chp_sink, chp_heat_feed_in, 0.8, "TEST_CHP", ambient_temperature=282.5,
                                                initial_heat_regulation=0.001)
    controller_testee.regulation = 0.5
    base_gas_cons = controller_testee.get_gas_consume(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons * controller_testee.regulation
    assert controller_testee.get_power_production(mn) == 2.886218928 * controller_testee.regulation
    assert controller_testee.get_heat_production(mn) == -1.4432870697670863

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_gas_consume(mn) == base_gas_cons * controller_testee.regulation
    assert controller_testee.get_power_production(mn) == 2.886218928 * controller_testee.regulation
    assert controller_testee.get_heat_production(mn) == -1.4432870697670863

def test_p2g():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    p2g_id_el = ppower.create_load(power_net, bus = 0, p_mw = 1)
    p2g_id_gas = ppipes.create_source(gas_net, junction = 0, mdot_kg_per_s = 0.5)
    controller_testee = RegulatedP2GControlMultiEnergy(mn, p2g_id_el, p2g_id_gas, efficiency = 0.7, name="TEST_P2G")
    base_load = controller_testee.get_power_load(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_power_load(mn) == base_load
    assert controller_testee.get_source_production(mn) == 0.016492165420377285

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_power_load(mn) == base_load
    assert controller_testee.get_source_production(mn) == 0.016492165420377285

def test_p2g_convenience():
    # GIVEN
    mn = create_small_test_multinet()
    controller_testee = create_p2g(mn, 0, 0, 1, efficiency=0.7)
    base_load = controller_testee.get_power_load(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_power_load(mn) == base_load
    assert controller_testee.get_source_production(mn) == 0.016492165420377285

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_power_load(mn) == base_load
    assert controller_testee.get_source_production(mn) == 0.016492165420377285

def test_p2g_regulated():
    # GIVEN
    mn = create_small_test_multinet()
    gas_net = mn['nets']['gas']
    power_net = mn['nets']['power']
    p2g_id_el = ppower.create_load(power_net, bus = 0, p_mw = 1)
    p2g_id_gas = ppipes.create_source(gas_net, junction = 0, mdot_kg_per_s = 0.5)
    controller_testee = RegulatedP2GControlMultiEnergy(mn, p2g_id_el, p2g_id_gas, efficiency = 0.7, name="TEST_P2G")
    controller_testee.regulation = 0.75
    base_load = controller_testee.get_power_load(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_power_load(mn) == base_load * controller_testee.regulation
    assert controller_testee.get_source_production(mn) == 0.016492165420377285 * controller_testee.regulation

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_power_load(mn) == base_load * controller_testee.regulation
    assert controller_testee.get_source_production(mn) == 0.016492165420377285 * controller_testee.regulation


def test_p2h_convenience():
    # GIVEN
    mn = create_small_test_multinet()
    efficiency = 0.7
    controller_testee = create_p2h(mn, 0, 0, 0, efficiency=efficiency)
    base_power = controller_testee.get_power_load(mn)

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_heat_production(mn) == -base_power * efficiency

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_heat_production(mn) == -base_power * efficiency

def test_p2h_convenience_regulated():
    # GIVEN
    mn = create_small_test_multinet()
    efficiency = 0.7
    controller_testee = create_p2h(mn, 0, 0, 0, efficiency=efficiency)
    base_power = controller_testee.get_power_load(mn)    
    controller_testee.regulation = 0.75

    # WHEN
    controller_testee.time_step(mn, 0)

    # THEN
    assert controller_testee.get_heat_production(mn) == -base_power * efficiency * controller_testee.regulation

    # WHEN
    controller_testee.time_step(mn, 1)

    # THEN
    assert controller_testee.get_heat_production(mn) == -base_power * efficiency * controller_testee.regulation