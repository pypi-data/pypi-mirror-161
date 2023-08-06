"""Contains a number of multi energy network definitions.
"""
from numpy import random
from pandapower.timeseries.data_sources.frame_data import DFData

import simbench
import pandapower as ppower
import pandapipes as ppipes
import pandapipes.multinet as ppm
import pandapower.networks as pandapowernetworks
import pandapipes.networks as pipesnetworks
import pandapower.control as powercontrol

import pandas as pd
import numpy as np
import math
import random

from peext.controller import (
    CHPControlMultiEnergy,
    RegulatedG2PControlMultiEnergy,
    RegulatedP2GControlMultiEnergy,
    RegulatedP2HControlMultiEnergy,
)

REF_BAR = 60
REF_TEMP = 290


def create_small_test_multinet():
    """Factory for the panda-multinet.

    :return: multinet
    :rtype: pandapower/pipes multinet
    """

    # Setup power network
    net_power = ppower.create_empty_network("power")
    bus_id = ppower.create_bus(net_power, vn_kv=1, name="bus_el")
    bus_id2 = ppower.create_bus(net_power, vn_kv=1, name="bus_el2")
    bus_id3 = ppower.create_bus(net_power, vn_kv=1, name="bus_el3")
    bus_id4 = ppower.create_bus(net_power, vn_kv=1, name="bus_el4")
    ppower.create_line_from_parameters(
        net_power,
        from_bus=bus_id,
        to_bus=bus_id2,
        length_km=10,
        r_ohm_per_km=1,
        x_ohm_per_km=1,
        c_nf_per_km=20,
        max_i_ka=20,
        name="PHLine",
    )
    ppower.create_line_from_parameters(
        net_power,
        from_bus=bus_id,
        to_bus=bus_id3,
        length_km=10,
        r_ohm_per_km=1,
        x_ohm_per_km=1,
        c_nf_per_km=20,
        max_i_ka=20,
        name="TWLine",
    )
    ppower.create_line_from_parameters(
        net_power,
        from_bus=bus_id2,
        to_bus=bus_id4,
        length_km=1,
        r_ohm_per_km=1,
        x_ohm_per_km=1,
        c_nf_per_km=20,
        max_i_ka=20,
        name="ASLine",
    )
    ppower.create_ext_grid(net_power, bus=bus_id, vm_pu=10)
    ppower.create_gen(net_power, bus_id3, p_mw=1, vm_pu=10, name="Torgenerator")
    ppower.create_load(net_power, bus=bus_id4, p_mw=0.1, name="ALoad")

    # Setup L-Gas network
    net_gas = ppipes.create_empty_network("gas", fluid="lgas")
    jun_id = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k=290)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k=290)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k=290)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k=290)
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id,
        to_junction=jun_id2,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe 1",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id2,
        to_junction=jun_id3,
        length_km=1.1,
        diameter_m=0.15,
        name="Pipe 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id3,
        to_junction=jun_id4,
        length_km=1.1,
        diameter_m=0.15,
        name="Pipe 3",
    )
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.085, name="Sink 2")
    ppipes.create_ext_grid(
        net_gas, junction=jun_id, p_bar=5.2, t_k=293.15, name="Grid Connection"
    )

    # Setup Heat network
    net_heat = ppipes.create_empty_network("heat", fluid="water")
    jun_id_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k=308)
    jun_id2_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k=293)
    jun_id3_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k=293)
    jun_id4_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k=293)
    ppipes.create_circ_pump_const_mass_flow(
        net_heat,
        from_junction=jun_id3_heat,
        to_junction=jun_id4_heat,
        p_bar=5,
        mdot_kg_per_s=20,
        t_k=273.15 + 35,
    )
    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id2_heat,
        to_junction=jun_id3_heat,
        length_km=1,
        diameter_m=200e-3,
        k_mm=0.1,
        alpha_w_per_m2k=10,
        sections=5,
        text_k=283,
        name="Heat Pipe 1",
    )
    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id4_heat,
        to_junction=jun_id_heat,
        length_km=1,
        diameter_m=200e-3,
        k_mm=0.1,
        alpha_w_per_m2k=10,
        sections=5,
        text_k=283,
        name="Heat Pipe 2",
    )

    # Multinet for coupling of those networks
    mn = ppm.create_empty_multinet("multi")
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")
    ppm.add_net_to_multinet(mn, net_heat, net_name="heat")

    # Create coupling point chp
    chp_gen = ppower.create_sgen(net_power, bus_id3, p_mw=1, name="CHPTorgenerator")
    chp_sink = ppipes.create_sink(
        net_gas, junction=jun_id3, mdot_kg_per_s=0.085, name="CHP Sink"
    )
    chp_heat_feed_in = ppipes.create_heat_exchanger(
        net_heat,
        from_junction=jun_id_heat,
        to_junction=jun_id2_heat,
        diameter_m=200e-3,
        qext_w=-10000,
    )
    CHPControlMultiEnergy(
        mn, chp_gen, chp_sink, chp_heat_feed_in, 0.8, "CHP1", ambient_temperature=282.5
    )

    # Create coupling point power2gas
    p2g_id_el = ppower.create_load(net_power, bus=bus_id2, p_mw=1, name="ALoad")
    p2g_id_gas = ppipes.create_source(
        net_gas, junction=jun_id2, mdot_kg_per_s=0.5, name="ASource"
    )
    ppipes.create_source(net_gas, junction=jun_id4, mdot_kg_per_s=0.2, name="A2Source")
    RegulatedP2GControlMultiEnergy(
        mn, p2g_id_el, p2g_id_gas, efficiency=0.8, name="ANp2g"
    )

    return mn


def create_big_multinet_gas_power():
    """Evaluation NET for big example with several controllers, which might act conflicting.
    Most of the components will use static data (load-data, schedules).
    """
    schutterwald_gas_net = pipesnetworks.schutterwald()
    mv_rhein_power_net = pandapowernetworks.mv_oberrhein()
    mn = ppm.create_empty_multinet("multi")
    ppm.add_net_to_multinet(mn, schutterwald_gas_net, net_name="gas")
    ppm.add_net_to_multinet(mn, mv_rhein_power_net, net_name="power")
    return mn


def generate_load_profiles(
    net_gas, net_power, net_heat, time_steps, with_heat, load_type, load_mul
):
    # power loads
    TS_LEN = time_steps
    random_load_matr = np.random.normal(
        0.03 * load_mul, 0.01, (TS_LEN, len(net_power.load.index))
    )
    sink_matr = np.full((TS_LEN, len(net_gas.sink.index)), 0.8)
    heat_matr = None

    if with_heat:
        heat_matr = np.full((TS_LEN, len(net_heat.heat_exchanger.index)), 0.5)

    # sin curves for load/sinks in range 30 to 80
    if load_type == "sin":
        for i in range(TS_LEN):
            random_load_matr[i, :] = (
                np.sin(i / 10 + np.array([i for i in range(len(net_power.load.index))]))
                + 1
            ) * load_mul + 20
            sink_matr[i, :] = (math.sin(i / 10 + math.pi) + 1) * load_mul
            if with_heat:
                heat_matr[i, :] = (math.sin(i / 10 + math.pi / 2) + 1) * load_mul
    elif load_type == "ssin":
        # load peaks in range 30 to 80
        for i in range(TS_LEN):
            sink_matr[i, :] = (math.sin(i / 10 + math.pi) + 1) * load_mul
    elif load_type == "ssin2":
        # load peaks in range 30 to 80
        for i in range(TS_LEN):
            random_load_matr[i, :] = (math.sin(i / 10) + 1) * load_mul
    elif load_type == "ext":
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN - 10):
            random_load_matr[i, :] *= random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * random.randint(2, 4) * load_mul
    elif load_type == "aext":
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN - 10):
            random_load_matr[i, :] *= -random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * random.randint(2, 4) * load_mul
    elif load_type == "aext2":
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN - 10):
            random_load_matr[i, :] *= random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * -random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * -random.randint(2, 4) * load_mul
    elif load_type == "sext":
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN - 10):
            random_load_matr[i, :] *= random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * load_mul
    elif load_type == "sext2":
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN - 10):
            random_load_matr[i, :] *= load_mul
            sink_matr[i, :] = sink_matr[0, 0] * random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * random.randint(2, 4) * load_mul

    return random_load_matr, heat_matr, sink_matr


def create_medium_multinet_gas_power(
    load_type=None, load_mul=1, time_steps=101, with_heat=False
):
    """Evaluation NET for medium examples only consisting of generators and sinks."""
    # Setup power network
    net_power = pandapowernetworks.create_synthetic_voltage_control_lv_network(
        "rural_1"
    )
    net_power.name = "power"

    # Setup L-Gas network
    REF_BAR = 60
    REF_TEMP = 290
    net_gas = ppipes.create_empty_network(name="gas", fluid="lgas")
    jun_id_ext = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id5 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id6 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id7 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id8 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id9 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id10 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)

    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id2,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id5,
        length_km=2.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 5",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id4,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 4",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id5,
        to_junction=jun_id3,
        length_km=0.5,
        diameter_m=0.05,
        name="Pipe SI 5 SI 3",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id2,
        to_junction=jun_id,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 2 SI 1",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id7,
        to_junction=jun_id6,
        length_km=3.1,
        diameter_m=0.05,
        name="Pipe SI 7 SI 6",
    )

    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id_ext,
        to_junction=jun_id9,
        length_km=1.1,
        diameter_m=0.08,
        name="Pipe EXT SO 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id8,
        to_junction=jun_id6,
        length_km=3.1,
        diameter_m=0.05,
        name="Pipe SO 1 SI 7",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id9,
        to_junction=jun_id6,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SO 2 SI 6",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id10,
        to_junction=jun_id6,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SO 2 SI 6",
    )

    g_si_1 = ppipes.create_sink(
        net_gas, junction=jun_id, mdot_kg_per_s=0.02, name="BSink 1"
    )
    g_si_2 = ppipes.create_sink(
        net_gas, junction=jun_id2, mdot_kg_per_s=0.045, name="SSink 2"
    )
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.0085, name="SSink 3")
    ppipes.create_sink(net_gas, junction=jun_id4, mdot_kg_per_s=0.008, name="MSink 4")
    ppipes.create_sink(net_gas, junction=jun_id5, mdot_kg_per_s=0.0085, name="SSink 5")
    ppipes.create_sink(net_gas, junction=jun_id6, mdot_kg_per_s=0.00085, name="SSink 6")
    ppipes.create_sink(net_gas, junction=jun_id7, mdot_kg_per_s=0.008, name="MSink 7")

    g_s_1 = ppipes.create_source(
        net_gas, junction=jun_id8, mdot_kg_per_s=0.0285, name="BSource 1"
    )
    g_s_2 = ppipes.create_source(
        net_gas, junction=jun_id9, mdot_kg_per_s=0.0285, name="BSource 2"
    )
    ppipes.create_source(
        net_gas, junction=jun_id10, mdot_kg_per_s=0.01885, name="BSource 3"
    )
    ppipes.create_ext_grid(
        net_gas,
        junction=jun_id_ext,
        p_bar=REF_BAR,
        t_k=REF_TEMP,
        name="Grid Connection Gas",
    )

    # COUPLINGS
    mn = ppm.create_empty_multinet()
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")

    # Setup Heat network
    net_heat = None
    if with_heat:
        HEAT_BAR = 5
        HEAT_TEMP = 363.15
        net_heat = ppipes.create_empty_network("heat", fluid="water")
        jun_id_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id2_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id3_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id4_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id5_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id6_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        chp_heat_feed_in = ppipes.create_heat_exchanger(
            net_heat,
            from_junction=jun_id_heat,
            to_junction=jun_id2_heat,
            diameter_m=0.075,
            qext_w=-0.1,
        )
        ppipes.create_heat_exchanger(
            net_heat,
            from_junction=jun_id4_heat,
            to_junction=jun_id5_heat,
            diameter_m=0.075,
            qext_w=0.1,
        )
        ppipes.create_heat_exchanger(
            net_heat,
            from_junction=jun_id5_heat,
            to_junction=jun_id6_heat,
            diameter_m=0.075,
            qext_w=0.1,
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=jun_id3_heat,
            to_junction=jun_id4_heat,
            length_km=0.1,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
            text_k=HEAT_TEMP,
            name="Heat Pipe 1",
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=jun_id2_heat,
            to_junction=jun_id3_heat,
            length_km=0.1,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
            text_k=HEAT_TEMP,
            name="Heat Pipe 1",
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=jun_id6_heat,
            to_junction=jun_id_heat,
            length_km=0.1,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
            text_k=HEAT_TEMP,
            name="Heat Pipe 2",
        )
        ppipes.create_ext_grid(
            net_heat,
            junction=jun_id6_heat,
            p_bar=HEAT_BAR,
            t_k=HEAT_TEMP,
            name="Grid Connection Heat",
        )
        ppm.add_net_to_multinet(mn, net_heat, net_name="heat")

    random_load_matr, heat_matr, sink_matr = generate_load_profiles(
        net_gas, net_power, net_heat, time_steps, with_heat, load_type, load_mul
    )

    # P2G load exception
    random_load_matr[:, 2] = 0.18
    random_load_matr[:, 3] = 0.18
    sink_matr[:, g_si_1] = 0.8
    sink_matr[:, g_si_2] = 0.8

    if with_heat:
        heat_matr[:, chp_heat_feed_in] = -0.5

    df = (
        pd.DataFrame(
            random_load_matr,
            index=list(range(time_steps)),
            columns=net_power.load.index,
        )
        * net_power.load.p_mw.values
    )
    ds = DFData(df)
    powercontrol.ConstControl(
        net_power,
        element="load",
        element_index=net_power.load.index,
        variable="p_mw",
        data_source=ds,
        profile_name=net_power.load.index,
    )

    # gas loads
    df = (
        pd.DataFrame(
            sink_matr, index=list(range(time_steps)), columns=net_gas.sink.index
        )
        * net_gas.sink.mdot_kg_per_s.values
    )
    ds = DFData(df)
    powercontrol.ConstControl(
        net_gas,
        element="sink",
        element_index=net_gas.sink.index,
        variable="mdot_kg_per_s",
        data_source=ds,
        profile_name=net_gas.sink.index,
    )

    if with_heat:
        # gas loads
        df = (
            pd.DataFrame(
                heat_matr,
                index=list(range(time_steps)),
                columns=net_heat.heat_exchanger.index,
            )
            * net_heat.heat_exchanger.qext_w.values
        )
        ds = DFData(df)
        powercontrol.ConstControl(
            net_heat,
            element="heat_exchanger",
            element_index=net_heat.heat_exchanger.index,
            variable="qext_w",
            data_source=ds,
            profile_name=net_heat.heat_exchanger.index,
        )

        CHPControlMultiEnergy(
            mn,
            0,
            g_si_1,
            chp_heat_feed_in,
            0.8,
            "CHP1",
            ambient_temperature=282.5,
            element_type_power="sgen",
        )
        CHPControlMultiEnergy(
            mn,
            1,
            g_si_2,
            chp_heat_feed_in,
            0.8,
            "CHP2",
            ambient_temperature=282.5,
            element_type_power="sgen",
        )
    else:
        RegulatedG2PControlMultiEnergy(
            mn, 0, g_si_1, efficiency=0.9, name="ANg2p2 0 0", element_type_power="sgen"
        )
        RegulatedG2PControlMultiEnergy(
            mn, 1, g_si_2, efficiency=0.85, name="ANg2p3 1 1", element_type_power="sgen"
        )

    # partially overwrite constcontrol
    RegulatedP2GControlMultiEnergy(
        mn, 2, g_s_1, efficiency=0.78, name="ANp2g1 1 0", element_type_power="gen"
    )
    RegulatedP2GControlMultiEnergy(
        mn, 3, g_s_2, efficiency=0.94, name="ANp2g2 2 1", element_type_power="gen"
    )

    return mn


def create_big_multinet_gas_power(
    load_type=None, load_mul=1, time_steps=101, with_heat=False
):
    """Evaluation NET for medium examples only consisting of generators and sinks."""
    # Setup power network
    net_power = pandapowernetworks.create_synthetic_voltage_control_lv_network(
        "rural_1"
    )
    net_power.name = "power"

    # Setup L-Gas network
    REF_BAR = 60
    REF_TEMP = 290
    net_gas = ppipes.create_empty_network(name="gas", fluid="lgas")
    jun_id_ext = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id5 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id6 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id7 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id8 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id9 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id10 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)

    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id2,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id5,
        length_km=2.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 5",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id4,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 4",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id5,
        to_junction=jun_id3,
        length_km=0.5,
        diameter_m=0.05,
        name="Pipe SI 5 SI 3",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id2,
        to_junction=jun_id,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 2 SI 1",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id7,
        to_junction=jun_id6,
        length_km=3.1,
        diameter_m=0.05,
        name="Pipe SI 7 SI 6",
    )

    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id_ext,
        to_junction=jun_id9,
        length_km=1.1,
        diameter_m=0.08,
        name="Pipe EXT SO 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id8,
        to_junction=jun_id6,
        length_km=3.1,
        diameter_m=0.05,
        name="Pipe SO 1 SI 7",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id9,
        to_junction=jun_id6,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SO 2 SI 6",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id10,
        to_junction=jun_id6,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SO 2 SI 6",
    )

    g_si_1 = ppipes.create_sink(
        net_gas, junction=jun_id, mdot_kg_per_s=0.02, name="BSink 1"
    )
    g_si_2 = ppipes.create_sink(
        net_gas, junction=jun_id2, mdot_kg_per_s=0.045, name="SSink 2"
    )
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.0085, name="SSink 3")
    ppipes.create_sink(net_gas, junction=jun_id4, mdot_kg_per_s=0.008, name="MSink 4")
    ppipes.create_sink(net_gas, junction=jun_id5, mdot_kg_per_s=0.0085, name="SSink 5")
    ppipes.create_sink(net_gas, junction=jun_id6, mdot_kg_per_s=0.00085, name="SSink 6")
    ppipes.create_sink(net_gas, junction=jun_id7, mdot_kg_per_s=0.008, name="MSink 7")

    g_s_1 = ppipes.create_source(
        net_gas, junction=jun_id8, mdot_kg_per_s=0.0285, name="BSource 1"
    )
    g_s_2 = ppipes.create_source(
        net_gas, junction=jun_id9, mdot_kg_per_s=0.0285, name="BSource 2"
    )
    ppipes.create_source(
        net_gas, junction=jun_id10, mdot_kg_per_s=0.01885, name="BSource 3"
    )
    ppipes.create_ext_grid(
        net_gas,
        junction=jun_id_ext,
        p_bar=REF_BAR,
        t_k=REF_TEMP,
        name="Grid Connection Gas",
    )

    # COUPLINGS
    mn = ppm.create_empty_multinet()
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")

    # EXT
    jun_id11 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id12 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id13 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id14 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id3,
        to_junction=jun_id11,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id5,
        to_junction=jun_id12,
        length_km=2.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 5",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id10,
        to_junction=jun_id13,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 4",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id4,
        to_junction=jun_id14,
        length_km=0.5,
        diameter_m=0.05,
        name="Pipe SI 5 SI 3",
    )
    g_si_3 = ppipes.create_sink(
        net_gas, junction=jun_id11, mdot_kg_per_s=0.008, name="MSink 4"
    )
    g_si_4 = ppipes.create_sink(
        net_gas, junction=jun_id12, mdot_kg_per_s=0.0085, name="SSink 5"
    )
    g_si_5 = ppipes.create_sink(
        net_gas, junction=jun_id13, mdot_kg_per_s=0.00085, name="SSink 6"
    )
    g_si_6 = ppipes.create_sink(
        net_gas, junction=jun_id14, mdot_kg_per_s=0.008, name="MSink 7"
    )

    ext_gen = ppower.create_sgen(net_power, 20, p_mw=0.1, name="Torgenerator2")
    ext_gen2 = ppower.create_sgen(net_power, 13, p_mw=0.105, name="Torgenerator3")
    ext_gen3 = ppower.create_sgen(net_power, 16, p_mw=0.1, name="Torgenerator4")
    ext_gen4 = ppower.create_sgen(net_power, 17, p_mw=0.52, name="Torgenerator5")

    RegulatedG2PControlMultiEnergy(
        mn,
        ext_gen,
        g_si_3,
        efficiency=0.88,
        name="ANp2g1 1 0",
        element_type_power="sgen",
    )
    RegulatedG2PControlMultiEnergy(
        mn,
        ext_gen2,
        g_si_4,
        efficiency=0.90,
        name="ANp2g2 2 1",
        element_type_power="sgen",
    )
    RegulatedG2PControlMultiEnergy(
        mn,
        ext_gen3,
        g_si_5,
        efficiency=0.85,
        name="ANp2g1 1 0",
        element_type_power="sgen",
    )
    RegulatedG2PControlMultiEnergy(
        mn,
        ext_gen4,
        g_si_6,
        efficiency=0.91,
        name="ANp2g2 2 1",
        element_type_power="sgen",
    )

    # Setup Heat network
    net_heat = None
    if with_heat:
        HEAT_BAR = 5
        HEAT_TEMP = 363.15
        net_heat = ppipes.create_empty_network("heat", fluid="water")
        jun_id_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id2_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id3_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id4_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id5_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        jun_id6_heat = ppipes.create_junction(
            net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
        )
        chp_heat_feed_in = ppipes.create_heat_exchanger(
            net_heat,
            from_junction=jun_id_heat,
            to_junction=jun_id2_heat,
            diameter_m=0.075,
            qext_w=-0.1,
        )
        ppipes.create_heat_exchanger(
            net_heat,
            from_junction=jun_id4_heat,
            to_junction=jun_id5_heat,
            diameter_m=0.075,
            qext_w=0.1,
        )
        ppipes.create_heat_exchanger(
            net_heat,
            from_junction=jun_id5_heat,
            to_junction=jun_id6_heat,
            diameter_m=0.075,
            qext_w=0.1,
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=jun_id3_heat,
            to_junction=jun_id4_heat,
            length_km=0.1,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
            text_k=HEAT_TEMP,
            name="Heat Pipe 1",
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=jun_id2_heat,
            to_junction=jun_id3_heat,
            length_km=0.1,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
            text_k=HEAT_TEMP,
            name="Heat Pipe 1",
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=jun_id6_heat,
            to_junction=jun_id_heat,
            length_km=0.1,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
            text_k=HEAT_TEMP,
            name="Heat Pipe 2",
        )
        ppipes.create_ext_grid(
            net_heat,
            junction=jun_id6_heat,
            p_bar=HEAT_BAR,
            t_k=HEAT_TEMP,
            name="Grid Connection Heat",
        )
        ppm.add_net_to_multinet(mn, net_heat, net_name="heat")

    # power loads
    random_load_matr, heat_matr, sink_matr = generate_load_profiles(
        net_gas, net_power, net_heat, time_steps, with_heat, load_type, load_mul
    )

    # P2G load exception
    random_load_matr[:, 2] = 0.18
    random_load_matr[:, 3] = 0.18
    sink_matr[:, g_si_3] = 0.8
    sink_matr[:, g_si_4] = 0.8
    sink_matr[:, g_si_5] = 0.8
    sink_matr[:, g_si_6] = 0.8

    if with_heat:
        heat_matr[:, chp_heat_feed_in] = -0.5

    df = (
        pd.DataFrame(
            random_load_matr,
            index=list(range(time_steps)),
            columns=net_power.load.index,
        )
        * net_power.load.p_mw.values
    )
    ds = DFData(df)
    powercontrol.ConstControl(
        net_power,
        element="load",
        element_index=net_power.load.index,
        variable="p_mw",
        data_source=ds,
        profile_name=net_power.load.index,
    )

    # gas loads
    df = (
        pd.DataFrame(
            sink_matr, index=list(range(time_steps)), columns=net_gas.sink.index
        )
        * net_gas.sink.mdot_kg_per_s.values
    )
    ds = DFData(df)
    powercontrol.ConstControl(
        net_gas,
        element="sink",
        element_index=net_gas.sink.index,
        variable="mdot_kg_per_s",
        data_source=ds,
        profile_name=net_gas.sink.index,
    )

    if with_heat:
        # gas loads
        df = (
            pd.DataFrame(
                heat_matr,
                index=list(range(time_steps)),
                columns=net_heat.heat_exchanger.index,
            )
            * net_heat.heat_exchanger.qext_w.values
        )
        ds = DFData(df)
        powercontrol.ConstControl(
            net_heat,
            element="heat_exchanger",
            element_index=net_heat.heat_exchanger.index,
            variable="qext_w",
            data_source=ds,
            profile_name=net_heat.heat_exchanger.index,
        )

        CHPControlMultiEnergy(
            mn,
            0,
            g_si_1,
            chp_heat_feed_in,
            0.8,
            300,
            "CHP1",
            ambient_temperature=282.5,
            element_type_power="sgen",
        )
        CHPControlMultiEnergy(
            mn,
            1,
            g_si_2,
            chp_heat_feed_in,
            0.8,
            300,
            "CHP1",
            ambient_temperature=282.5,
            element_type_power="sgen",
        )
    else:
        RegulatedG2PControlMultiEnergy(
            mn, 0, g_si_1, efficiency=0.9, name="ANg2p2 0 0", element_type_power="sgen"
        )
        RegulatedG2PControlMultiEnergy(
            mn, 1, g_si_2, efficiency=0.85, name="ANg2p3 1 1", element_type_power="sgen"
        )

    # partially overwrite constcontrol
    RegulatedP2GControlMultiEnergy(
        mn, 2, g_s_1, efficiency=0.78, name="ANp2g1 1 0", element_type_power="gen"
    )
    RegulatedP2GControlMultiEnergy(
        mn, 3, g_s_2, efficiency=0.94, name="ANp2g2 2 1", element_type_power="gen"
    )

    return mn


def create_district_gas_network():
    # Setup L-Gas network
    REF_BAR = 60
    REF_TEMP = 290
    net_gas = ppipes.create_empty_network(name="gas", fluid="lgas")
    jun_id_ext = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id5 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id6 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id7 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id8 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id9 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)
    jun_id10 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP)

    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id2,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id5,
        length_km=2.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 5",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id6,
        to_junction=jun_id4,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 6 SI 4",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id5,
        to_junction=jun_id3,
        length_km=0.5,
        diameter_m=0.05,
        name="Pipe SI 5 SI 3",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id2,
        to_junction=jun_id,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SI 2 SI 1",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id7,
        to_junction=jun_id6,
        length_km=3.1,
        diameter_m=0.05,
        name="Pipe SI 7 SI 6",
    )

    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id_ext,
        to_junction=jun_id9,
        length_km=1.1,
        diameter_m=0.08,
        name="Pipe EXT SO 2",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id8,
        to_junction=jun_id6,
        length_km=3.1,
        diameter_m=0.05,
        name="Pipe SO 1 SI 7",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id9,
        to_junction=jun_id6,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SO 2 SI 6",
    )
    ppipes.create_pipe_from_parameters(
        net_gas,
        from_junction=jun_id10,
        to_junction=jun_id6,
        length_km=1.1,
        diameter_m=0.05,
        name="Pipe SO 2 SI 6",
    )

    ppipes.create_sink(net_gas, junction=jun_id, mdot_kg_per_s=0.02, name="BSink 1")
    ppipes.create_sink(net_gas, junction=jun_id2, mdot_kg_per_s=0.045, name="SSink 2")
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.0085, name="SSink 3")
    ppipes.create_sink(net_gas, junction=jun_id4, mdot_kg_per_s=0.008, name="MSink 4")
    ppipes.create_sink(net_gas, junction=jun_id5, mdot_kg_per_s=0.0085, name="SSink 5")
    ppipes.create_sink(net_gas, junction=jun_id6, mdot_kg_per_s=0.00085, name="SSink 6")
    ppipes.create_sink(net_gas, junction=jun_id7, mdot_kg_per_s=0.008, name="MSink 7")

    ppipes.create_source(
        net_gas, junction=jun_id8, mdot_kg_per_s=0.0285, name="BSource 1"
    )
    ppipes.create_source(
        net_gas, junction=jun_id9, mdot_kg_per_s=0.0285, name="BSource 2"
    )
    ppipes.create_source(
        net_gas, junction=jun_id10, mdot_kg_per_s=0.01885, name="BSource 3"
    )
    ppipes.create_ext_grid(
        net_gas,
        junction=jun_id_ext,
        p_bar=REF_BAR,
        t_k=REF_TEMP,
        name="Grid Connection Gas",
    )

    return net_gas


def create_district_heat_network(number_of_hh_in_sidelanes=20):
    HEAT_BAR = 5
    HEAT_TEMP = 363.15
    net_heat = ppipes.create_empty_network("heat", fluid="water")

    jun_id_heat_main_start = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    jun_id_heat_main_start_2 = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    ppipes.create_heat_exchanger(
        net_heat,
        from_junction=jun_id_heat_main_start_2,
        to_junction=jun_id_heat_main_start,
        diameter_m=0.075,
        qext_w=-0.1,
    )

    jun_id_heat_main_mid1 = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    jun_id_heat_main_mid1_2 = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    ppipes.create_heat_exchanger(
        net_heat,
        from_junction=jun_id_heat_main_mid1,
        to_junction=jun_id_heat_main_mid1_2,
        diameter_m=0.075,
        qext_w=-0.1,
    )

    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id_heat_main_start,
        to_junction=jun_id_heat_main_mid1,
        length_km=4,
        diameter_m=0.105,
        k_mm=0.025,
        alpha_w_per_m2k=100,
        sections=5,
        text_k=HEAT_TEMP,
    )
    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id_heat_main_mid1_2,
        to_junction=jun_id_heat_main_start_2,
        length_km=4,
        diameter_m=0.105,
        k_mm=0.025,
        alpha_w_per_m2k=100,
        sections=5,
        text_k=HEAT_TEMP,
    )

    jun_id_heat_main_mid2 = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    jun_id_heat_main_mid2_2 = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    ppipes.create_heat_exchanger(
        net_heat,
        from_junction=jun_id_heat_main_mid2_2,
        to_junction=jun_id_heat_main_mid2,
        diameter_m=0.075,
        qext_w=-0.1,
    )

    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id_heat_main_mid1,
        to_junction=jun_id_heat_main_mid2,
        length_km=3,
        diameter_m=0.105,
        k_mm=0.025,
        alpha_w_per_m2k=100,
        sections=5,
        text_k=HEAT_TEMP,
    )
    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id_heat_main_mid2_2,
        to_junction=jun_id_heat_main_mid1_2,
        length_km=3,
        diameter_m=0.105,
        k_mm=0.025,
        alpha_w_per_m2k=100,
        sections=5,
        text_k=HEAT_TEMP,
    )

    jun_id_heat_main_end = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    jun_id_heat_main_end_2 = ppipes.create_junction(
        net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
    )
    ppipes.create_heat_exchanger(
        net_heat,
        from_junction=jun_id_heat_main_end_2,
        to_junction=jun_id_heat_main_end,
        diameter_m=0.075,
        qext_w=-0.1,
    )

    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id_heat_main_mid2,
        to_junction=jun_id_heat_main_end,
        length_km=3,
        diameter_m=0.105,
        k_mm=0.025,
        alpha_w_per_m2k=100,
        sections=5,
        text_k=HEAT_TEMP,
    )
    ppipes.create_pipe_from_parameters(
        net_heat,
        from_junction=jun_id_heat_main_end_2,
        to_junction=jun_id_heat_main_mid2_2,
        length_km=3,
        diameter_m=0.105,
        k_mm=0.025,
        alpha_w_per_m2k=100,
        sections=5,
        text_k=HEAT_TEMP,
    )

    for junc_start_point in [
        (jun_id_heat_main_start, jun_id_heat_main_start_2),
        (jun_id_heat_main_mid1, jun_id_heat_main_mid1_2),
        (jun_id_heat_main_mid2, jun_id_heat_main_mid2_2),
        (jun_id_heat_main_end, jun_id_heat_main_end_2),
    ]:
        connect_1 = junc_start_point[0]
        connect_2 = junc_start_point[1]
        for _ in range(number_of_hh_in_sidelanes):
            next_jun_1 = ppipes.create_junction(
                net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
            )
            next_jun_2 = ppipes.create_junction(
                net_heat, pn_bar=HEAT_BAR, tfluid_k=HEAT_TEMP
            )
            ppipes.create_pipe_from_parameters(
                net_heat,
                from_junction=connect_1,
                to_junction=next_jun_1,
                length_km=3,
                diameter_m=0.105,
                k_mm=0.025,
                alpha_w_per_m2k=100,
                sections=5,
                text_k=HEAT_TEMP,
            )
            ppipes.create_pipe_from_parameters(
                net_heat,
                from_junction=next_jun_2,
                to_junction=connect_2,
                length_km=3,
                diameter_m=0.105,
                k_mm=0.025,
                alpha_w_per_m2k=100,
                sections=5,
                text_k=HEAT_TEMP,
            )
            ppipes.create_heat_exchanger(
                net_heat,
                from_junction=next_jun_1,
                to_junction=next_jun_2,
                diameter_m=0.075,
                qext_w=-0.1,
            )
            connect_1 = next_jun_1
            connect_2 = next_jun_2

    ppipes.create_ext_grid(
        net_heat, junction=jun_id_heat_main_end, p_bar=HEAT_BAR, t_k=HEAT_TEMP
    )

    return net_heat


def create_super_district_coupled_network(coupling_density, heat_sidelane_size=20):
    net_power = pandapowernetworks.create_synthetic_voltage_control_lv_network(
        "village_2"
    )
    net_power.name = "power"
    net_gas = create_district_gas_network()
    net_heat = create_district_heat_network(heat_sidelane_size)

    # COUPLINGS
    mn = ppm.create_empty_multinet()
    ppm.add_net_to_multinet(mn, net_heat, net_name="heat")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")

    # Add coupling points
    # P2G
    for i in range(min(len(net_power.load), len(net_gas.source))):
        if random.random() < coupling_density:
            RegulatedP2GControlMultiEnergy(
                mn,
                int(random.random() * len(net_power.load)),
                int(random.random() * len(net_gas.source)),
                efficiency=0.94,
                name=f"P2G-{i}",
            )
    # CHP
    for i in range(
        min(len(net_power.sgen), len(net_gas.sink), len(net_heat.heat_exchanger))
    ):
        if random.random() < coupling_density:
            CHPControlMultiEnergy(
                mn,
                int(random.random() * len(net_power.sgen)),
                int(random.random() * len(net_gas.sink)),
                int(random.random() * len(net_heat.heat_exchanger)),
                0.7 + random.random() * 0.3,
                "CHP-{i}",
                ambient_temperature=282.5,
                element_type_power="sgen",
            )

    # P2H
    for i in range(min(len(net_power.load), len(net_heat.heat_exchanger))):
        if random.random() < coupling_density:
            RegulatedP2HControlMultiEnergy(
                mn,
                int(random.random() * len(net_power.load)),
                int(random.random() * len(net_heat.heat_exchanger)),
                0.4 + random.random() * 0.5,
                name=f"P2H-{i}",
            )

    return mn


def generate_multi_network_based_on_simbench(
    simbench_id, heat_deployment_rate, gas_deployment_rate, coupling_density=0.3
):
    return generate_multi_network_based_on_power_net(
        simbench.get_simbench_net(simbench_id)
    )


def create_gas_net_for_power(power_net, gas_deployment_rate, source_sink_ratio=0.05):
    net_gas = ppipes.create_empty_network(name="gas", fluid="lgas")

    for i in power_net.bus.index:
        ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k=REF_TEMP, index=i)

    for i, from_bus, to_bus in zip(
        power_net.trafo.index,
        power_net.trafo["lv_bus"],
        power_net.trafo["hv_bus"],
    ):
        ppipes.create_pipe_from_parameters(
            net_gas,
            from_junction=from_bus,
            to_junction=to_bus,
            length_km=0.01,
            diameter_m=0.05,
        )

    for i, length, from_bus, to_bus in zip(
        power_net.line.index,
        power_net.line["length_km"],
        power_net.line["from_bus"],
        power_net.line["to_bus"],
    ):
        ppipes.create_pipe_from_parameters(
            net_gas,
            from_junction=from_bus,
            to_junction=to_bus,
            length_km=length * (random.random() / 4 + (7 / 8)),
            diameter_m=0.05,
        )

    for i in power_net.bus.index:
        ratio_c_value = random.random()
        deployment_c_value = random.random()
        if deployment_c_value < gas_deployment_rate:
            if ratio_c_value > source_sink_ratio:

                ppipes.create_sink(net_gas, junction=i, mdot_kg_per_s=0.1)
            else:
                ppipes.create_source(
                    net_gas,
                    junction=i,
                    mdot_kg_per_s=(1 / source_sink_ratio) * 0.1,
                )

    ppipes.create_ext_grid(
        net_gas,
        junction=0,
        p_bar=REF_BAR,
        t_k=REF_TEMP,
        name="Grid Connection Gas",
    )
    return net_gas


def create_heat_net_for_power(power_net, heat_deployment_rate):
    net_heat = ppipes.create_empty_network(name="heat", fluid="water")
    start_return_net_id_junctions = max(power_net.bus.index) + 1

    for i in power_net.bus.index:
        ppipes.create_junction(net_heat, pn_bar=REF_BAR, tfluid_k=REF_TEMP, index=i)
        ppipes.create_junction(
            net_heat,
            pn_bar=REF_BAR,
            tfluid_k=REF_TEMP,
            index=i + start_return_net_id_junctions,
        )

    for i, from_bus, to_bus in zip(
        power_net.trafo.index,
        power_net.trafo["lv_bus"],
        power_net.trafo["hv_bus"],
    ):
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=from_bus,
            to_junction=to_bus,
            length_km=0.01,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=1,
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=from_bus + start_return_net_id_junctions,
            to_junction=to_bus + start_return_net_id_junctions,
            length_km=0.01,
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=1,
        )

    for i, length, from_bus, to_bus in zip(
        power_net.line.index,
        power_net.line["length_km"],
        power_net.line["from_bus"],
        power_net.line["to_bus"],
    ):
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=from_bus,
            to_junction=to_bus,
            length_km=length * (random.random() / 4 + (7 / 8)),
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
        )
        ppipes.create_pipe_from_parameters(
            net_heat,
            from_junction=from_bus + start_return_net_id_junctions,
            to_junction=to_bus + start_return_net_id_junctions,
            length_km=length * (random.random() / 4 + (7 / 8)),
            diameter_m=0.075,
            k_mm=0.025,
            alpha_w_per_m2k=100,
            sections=5,
        )

    for i in power_net.bus.index:
        deployment_c_value = random.random()
        if deployment_c_value < heat_deployment_rate:
            ppipes.create_heat_exchanger(
                net_heat,
                from_junction=i,
                to_junction=i + start_return_net_id_junctions,
                diameter_m=0.075,
                qext_w=-0.1,
            )

    ppipes.create_ext_grid(
        net_heat,
        junction=0,
        p_bar=REF_BAR,
        t_k=REF_TEMP,
        name="Grid Connection Heat",
    )
    return net_heat


def create_p2h_in_combined_generated_network(mn, net_power, net_heat, p2h_density):
    for i in net_heat.heat_exchanger.index:
        if random.random() < p2h_density:
            cross_index = net_heat.heat_exchanger["from_junction"][i]
            load = net_power.load[net_power.load["bus"] == cross_index]
            if len(load.index) > 0:
                RegulatedP2HControlMultiEnergy(
                    mn,
                    load.index[0],
                    i,
                    0.4 + random.random() * 0.5,
                    name=f"P2H-{i}",
                )


def create_chp_in_combined_generated_network(
    mn, net_power, net_heat, net_gas, chp_density
):
    for i in net_gas.sink.index:
        if random.random() < chp_density:
            cross_index = net_gas.sink["junction"][i]
            sgen = net_power.sgen[net_power.sgen["bus"] == cross_index]
            heat_ex = net_heat.heat_exchanger[
                net_heat.heat_exchanger["from_junction"] == cross_index
            ]
            if len(sgen.index) > 0 and len(heat_ex.index) > 0:
                CHPControlMultiEnergy(
                    mn,
                    sgen.index[0],
                    i,
                    heat_ex.index[0],
                    0.7 + random.random() * 0.3,
                    "CHP-{i}",
                    ambient_temperature=282.5,
                    element_type_power="sgen",
                )


def create_p2g_in_combined_generated_network(mn, net_power, net_gas, p2g_density):
    for i in net_gas.source.index:
        if random.random() < p2g_density:
            cross_index = net_gas.source["junction"][i]
            load = net_power.load[net_power.load["bus"] == cross_index]
            if len(load.index) > 0:
                RegulatedP2GControlMultiEnergy(
                    mn,
                    load.index[0],
                    i,
                    efficiency=0.85,
                    name=f"P2G-{i}",
                )


def generate_multi_network_based_on_power_net(
    net_power,
    heat_deployment_rate,
    gas_deployment_rate,
    chp_density=0.3,
    p2g_density=0.1,
    p2h_density=0.1,
):
    net_power.name = "power"
    net_heat = create_heat_net_for_power(net_power, heat_deployment_rate)
    net_gas = create_gas_net_for_power(net_power, gas_deployment_rate)

    mn = ppm.create_empty_multinet()
    ppm.add_net_to_multinet(mn, net_heat, net_name="heat")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")

    create_p2h_in_combined_generated_network(mn, net_power, net_heat, p2h_density)
    create_chp_in_combined_generated_network(
        mn, net_power, net_heat, net_gas, chp_density
    )
    create_p2g_in_combined_generated_network(mn, net_power, net_gas, p2g_density)

    return mn
