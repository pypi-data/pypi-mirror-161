"""Pandapipes/power controller used to couple different networks.
"""

import pandapipes as ppipes
import pandapower as ppower
from pandapipes.multinet.control.controller.multinet_control import (
    G2PControlMultiEnergy,
    P2GControlMultiEnergy,
)
from pandapower.control.basic_controller import Controller

from peext.storage import EnergyStorage
from overrides import overrides

import numpy as np

NETS_ACCESS = "nets"
P_MW = "p_mw"


def find_for_junction(net, key, junction_id, connect_point):
    """Searches for all objects connected to a junction. Return the obj id + the direction.

    :param net: the network
    :type net: pandapipes network
    :param junction_id: id of the junction
    :type junction_id: int
    :return: Dictionary will all obj (obj_id, direction in ['to', 'from'])
    :rtype: Dict
    """
    obj = {}
    for index, row in net[key].iterrows():
        if row["from_junction"] == junction_id:
            obj[index] = ("from", key, connect_point)
        if row["to_junction"] == junction_id:
            obj[index] = ("to", key, connect_point)
    return obj


def find_pipes_for_junction(net, junction_id, connect_point=""):
    """Searches for all pipes connected to a junction. Return the pipe id + the direction.

    :param net: the network
    :type net: pandapipes network
    :param junction_id: id of the junction
    :type junction_id: int
    :return: Dictionary will all pipes (pipe_id, direction in ['to', 'from'])
    :rtype: Dict
    """
    pipes = find_for_junction(net, "pipe", junction_id, connect_point)

    # if no pipe directly connected, look for connected pump and their pipes
    if len(pipes) == 0:
        for key in ["pump", "circ_pump_pressure", "circ_pump_mass"]:
            if key in net:
                pump = find_for_junction(net, key, junction_id, connect_point)
                pipes.update(pump)

    return pipes


def find_lines_for_bus(net, bus_id, connect_point=""):
    """Searches for all lines connected to a bus. Return the bus id + the direction.

    :param net: the network
    :type net: pandapower network
    :param bus_id: id of the junction
    :type bus_id: int
    :return: Dictionary will all lines (line_id, direction in ['to', 'from'])
    :rtype: Dict
    """
    lines = {}
    for index, row in net.line.iterrows():
        if row["from_bus"] == bus_id:
            lines[index] = ("from", "line", connect_point)
        if row["to_bus"] == bus_id:
            lines[index] = ("to", "line", connect_point)
    return lines


class RoleListController(Controller):
    """Interface to the pandapipes/power controller system to overcome the need to have
    a mango agent. Useful for time-series simulations without the need of communication
    between real agents.
    """

    def __init__(
        self,
        multinet,
        names,
        roles,
        in_service=True,
        order=0,
        level=0,
        drop_same_existing_ctrl=False,
        initial_run=True,
        **kwargs,
    ):
        super().__init__(
            multinet,
            in_service,
            order,
            level,
            drop_same_existing_ctrl=drop_same_existing_ctrl,
            initial_run=initial_run,
            **kwargs,
        )

        self._names = names
        self._roles = roles

    def initialize_control(self, _):
        self.applied = False

    def get_all_net_names(self):
        return self._names

    def time_step(self, _, time):
        if time > 0:
            self.applied = False

            for role in self._roles:
                if time % (role.time_pause() + 1) == 0:
                    role.control()

    def control_step(self, _):
        self.applied = True

    def is_converged(self, _):
        return self.applied


class CHPControlMultiEnergy(G2PControlMultiEnergy):
    """Coupling controller representing a CHP unit with/or without heat storage.
    The heat energy will directly be injected to the heat-network via heat-exchanger and
    its efficiency.

    As base for the controller you need to define a gas sink and a power generator (sgen/gen).
    In the default mode the generated power will be calculated based on the mass flow of the
    gas sink, so the values of the sink will be untouched - if not regulated. To change this behaviour
    you can set calc_gas_from_power = True.

    In the default mode the generated heating will get injected in the heat-network after
    multiplying it with the heat-regulation, so there is an energy loss, besided efficiencies, in the system.
    There is also the option to charge a heat storage instead of losing this energy with setting use_storage = True.
    In that case an internal storage unit will be charged with (heat * (1-heat_regulation)). To make use of the storage
    you can overwrite this controller or couple another controller. To regulate the unit you
    can use the property .regulation/.heat_regulation

    Example for constructing a CHP unit.
    ...
    chp_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    chp_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    chp_heat_feed_in = ppipes.create_heat_exchanger(heat_net, from_junction=0, to_junction=1, diameter_m=200e-3, qext_w=-10000)
    chp = CHPControlMultiEnergy(mn, chp_gen, chp_sink, chp_heat_feed_in, 0.8, "TEST_CHP", ambient_temperature=282.5,
                                                initial_heat_regulation=0.001)
    ...

    This creates a CHP unit using a gas flow of 0.085 kg/s. The conversion efficiency is 80% and it drops most the heat (99.9%) after
    converting. Note again that the power/heat capacity values of the heat_exchanger/s_generator are dropped in the default mode,
    so they don't matter at all.
    """

    def __init__(
        self,
        multinet,
        element_index_power,
        element_index_gas,
        heat_exchanger_id,
        efficiency,
        name,
        name_power_net="power",
        name_gas_net="gas",
        name_heat_net="heat",
        element_type_power="sgen",
        initial_heat_regulation=1,
        storage_cap=1000,
        storage_charge_eff=0.81,
        storage_discharge_eff=0.81,
        in_service=True,
        order=0,
        level=0,
        drop_same_existing_ctrl=False,
        initial_run=True,
        calc_gas_from_power=False,
        ambient_temperature=282.5,
        use_storage=False,
        **kwargs,
    ):

        super().__init__(
            multinet,
            element_index_power,
            element_index_gas,
            efficiency,
            name_power_net=name_power_net,
            name_gas_net=name_gas_net,
            element_type_power=element_type_power,
            in_service=in_service,
            order=order,
            level=level,
            drop_same_existing_ctrl=drop_same_existing_ctrl,
            initial_run=initial_run,
            calc_gas_from_power=calc_gas_from_power,
            **kwargs,
        )

        self.name = name
        self.__load_regulation_multiplier = 1
        self.__heat_regulation_multiplier = initial_heat_regulation
        self.__ambient_temperature_in_k = ambient_temperature
        self.__name_heat_net = name_heat_net
        self.__heat_exchanger_id = heat_exchanger_id
        self.__storage_builder = (
            EnergyStorage.builder()
            .step_size(1)
            .load(0)
            .capacity(storage_cap)
            .self_discharge(0)
            .charge_efficiency(storage_charge_eff)
            .discharge_efficiency(storage_discharge_eff)
        )
        self.storage = None
        self.heat_energy = 0
        self.power_gen = 0
        self._storage_active = use_storage

        heat_net = multinet[NETS_ACCESS][self.__name_heat_net]
        power_net = multinet[NETS_ACCESS][self.name_net_power]
        gas_net = multinet[NETS_ACCESS][self.name_net_gas]

        from_heat_junc = heat_net.heat_exchanger.loc[
            self.__heat_exchanger_id, "from_junction"
        ]
        to_heat_junc = heat_net.heat_exchanger.loc[
            self.__heat_exchanger_id, "to_junction"
        ]
        bus_gen = power_net[self.elm_type_power].loc[self.elm_idx_power, "bus"]
        junction_sink = gas_net.sink.loc[self.elm_idx_gas, "junction"]

        self._pipes_heat = dict(
            find_pipes_for_junction(heat_net, from_heat_junc, "from_junction")
        )
        self._pipes_heat.update(
            find_pipes_for_junction(heat_net, to_heat_junc, "to_junction")
        )
        self._line_power = find_lines_for_bus(power_net, bus_gen)
        self._pipes_gas = find_pipes_for_junction(gas_net, junction_sink)
        self.ref_gas_consume = self.get_gas_consume(multinet)
        self.ref_power_production = self.get_power_production(multinet)

    def get_gas_consume(self, multinet):
        try:
            gas_sink = multinet[NETS_ACCESS][self.name_net_gas].sink.at[
                self.elm_idx_gas, "mdot_kg_per_s"
            ]
        except (ValueError, TypeError):
            gas_sink = (
                multinet[NETS_ACCESS][self.name_net_gas]
                .sink.loc[self.elm_idx_gas, "mdot_kg_per_s"]
                .values[:]
            )
        return gas_sink

    def get_power_production(self, multinet):
        try:
            power_gen = multinet[NETS_ACCESS][self.name_net_power][
                self.elm_type_power
            ].at[self.elm_idx_power, "p_mw"]
        except (ValueError, TypeError):
            power_gen = (
                multinet[NETS_ACCESS][self.name_net_power][self.elm_type_power]
                .loc[self.elm_idx_power, "p_mw"]
                .values[:]
            )
        return power_gen

    def get_heat_production(self, multinet):
        try:
            return multinet[NETS_ACCESS][self.__name_heat_net].heat_exchanger.at[
                self.__heat_exchanger_id, "qext_w"
            ]
        except (ValueError, TypeError):
            return (
                multinet[NETS_ACCESS][self.__name_heat_net]
                .heat_exchanger.loc[self.__heat_exchanger_id, "qext_w"]
                .values[:]
            )

    def time_step(self, multinet, time):

        if self.el_power_led:
            self.power_gen = (
                self.ref_power_production * self.__load_regulation_multiplier
            )
            self.gas_cons = self.power_gen / (
                self.conversion_factor_kgps_to_mw() * self.efficiency
            )

        else:
            self.gas_cons = self.ref_gas_consume * self.__load_regulation_multiplier
            self.power_gen = (
                self.gas_cons * self.conversion_factor_kgps_to_mw() * self.efficiency
            )

        self.power_gen = (
            self.power_gen[0]
            if isinstance(self.power_gen, np.ndarray)
            else self.power_gen
        )
        self.gas_cons = (
            self.gas_cons[0] if isinstance(self.gas_cons, np.ndarray) else self.gas_cons
        )

        heat_energy_overall = self.calc_heat(self.gas_cons)
        heat_energy_overall = (
            heat_energy_overall[0]
            if isinstance(heat_energy_overall, np.ndarray)
            else heat_energy_overall
        )
        self.heat_energy = heat_energy_overall * self.heat_regulation
        self.heat_save_energy = heat_energy_overall * (1 - self.heat_regulation)
        if not self._storage_active:
            self.storage = self.__storage_builder.build()
            self.storage.charge(self.heat_save_energy)
        self.write_to_net(multinet)

    def calc_heat(self, gas_flow):
        return (
            gas_flow
            * self.conversion_factor_kgps_to_mw()
            * (0.000028 * self.__ambient_temperature_in_k + 273.3567)
            + 2.1609 * self.__ambient_temperature_in_k
            + 339.714
        )

    def control_step(self, mn):
        self.time_step(mn, 0)
        self.applied = True

    @overrides
    def get_all_net_names(self):
        return [self.name_net_gas, self.name_net_power, self.__name_heat_net]

    def write_to_net(self, multinet):
        try:
            multinet[NETS_ACCESS][self.name_net_gas].sink.at[
                self.elm_idx_gas, "mdot_kg_per_s"
            ] = self.gas_cons
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_gas].sink.loc[
                self.elm_idx_gas, "mdot_kg_per_s"
            ] = self.gas_cons
        try:
            multinet[NETS_ACCESS][self.name_net_power][self.elm_type_power].at[
                self.elm_idx_power, "p_mw"
            ] = self.power_gen
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_power][self.elm_type_power].loc[
                self.elm_idx_power, "p_mw"
            ] = self.power_gen

        try:
            multinet[NETS_ACCESS][self.__name_heat_net].heat_exchanger.at[
                self.__heat_exchanger_id, "qext_w"
            ] = -self.heat_energy
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.__name_heat_net].heat_exchanger.loc[
                self.__heat_exchanger_id, "qext_w"
            ].values[:] = -self.heat_energy

    @property
    def edges(self):
        """Return all edges connected to the CHP unit.

        :return: dict, energy-network-name -> edges
        :rtype: Dict
        """

        return {
            self.name_net_power: self._line_power,
            self.name_net_gas: self._pipes_gas,
            self.__name_heat_net: self._pipes_heat,
        }

    @property
    def nodes(self):
        return {
            self.name_net_power: (self.elm_type_power, self.elm_idx_power),
            self.name_net_gas: ("sink", self.elm_idx_gas),
            self.__name_heat_net: ("heat_exchanger", self.__heat_exchanger_id),
        }

    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @property
    def heat_regulation(self):
        return self.__heat_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value

    @heat_regulation.setter
    def heat_regulation(self, new_value):
        self.__heat_regulation_multiplier = new_value

    @property
    def storage_load(self):
        return self.storage.load

    @property
    def heat_cap(self):
        heat_cap = self.calc_heat(self.gas_cap)
        if isinstance(heat_cap, list):
            return heat_cap[0]
        return heat_cap

    @property
    def power_cap(self):
        if self.el_power_led:
            return self.ref_power_production
        else:
            return (
                self.ref_gas_consume
                * self.conversion_factor_kgps_to_mw()
                * self.efficiency
            )

    @property
    def gas_cap(self):
        if not self.el_power_led:
            return self.ref_gas_consume
        else:
            return (self.ref_power_production) / (
                self.conversion_factor_kgps_to_mw() * self.efficiency
            )

    def state_as_dict(self):
        return {
            "regulation": self.regulation,
            "heat_regulation": self.heat_regulation,
            "storage_load": self.storage_load,
        }


def create_chp(
    mn,
    bus_power,
    junction_gas,
    junction_heat_from,
    junction_heat_to,
    gas_consume,
    heat_diameter_m=200e-3,
    name="STD_CHP",
    efficiency=0.8,
    use_storage=False,
    storage_cap=1000,
    storage_charge_eff=0.81,
    storage_discharge_eff=0.81,
    ambient_temperature=282.5,
    heat_net_name="heat",
    power_net_name="power",
    gas_net_name="gas",
):
    """
    Create a CHPControlMultiEnergy and all necessary network elements for the given multinet.
    """

    gas_net = mn[NETS_ACCESS][gas_net_name]
    power_net = mn[NETS_ACCESS][power_net_name]
    heat_net = mn[NETS_ACCESS][heat_net_name]
    chp_gen = ppower.create_sgen(power_net, bus_power, p_mw=1)
    chp_sink = ppipes.create_sink(
        gas_net, junction=junction_gas, mdot_kg_per_s=gas_consume
    )
    chp_heat_feed_in = ppipes.create_heat_exchanger(
        heat_net,
        from_junction=junction_heat_from,
        to_junction=junction_heat_to,
        diameter_m=heat_diameter_m,
        qext_w=-10000,
    )
    return CHPControlMultiEnergy(
        mn,
        chp_gen,
        chp_sink,
        chp_heat_feed_in,
        efficiency,
        name,
        ambient_temperature=ambient_temperature,
        use_storage=use_storage,
        storage_cap=storage_cap,
        storage_charge_eff=storage_charge_eff,
        storage_discharge_eff=storage_discharge_eff,
    )


class RegulatedG2PControlMultiEnergy(G2PControlMultiEnergy):
    """Coupling controller representing a gas turbine (G2P) unit (without heat generation).

    As base for the controller you need to define a gas sink and a power generator (sgen/gen).
    In the default mode the generated power will be calculated based on the mass flow of the
    gas sink, so the values of the sink will be untouched - if not regulated. To change this behaviour
    you can set calc_gas_from_power = True. To regulate the unit you
    can use the property .regulation

    Example for constructing a G2P unit.
    ...
    g2p_gen = ppower.create_sgen(power_net, 0, p_mw = 1)
    g2p_sink = ppipes.create_sink(gas_net, junction=0, mdot_kg_per_s=0.085)
    g2p = RegulatedG2PControlMultiEnergy(mn, g2p_gen, g2p_sink, 0.8, "TEST_G2P")
    ...

    This creates a G2P unit using a gas flow of 0.085 kg/s. The conversion efficiency is 80%.
    Note again that the power value of the generator is dropped in default mode,
    so it doesn't matter at all. A G2P unit is equivalent to a CHP with heat_regulation=0
    """

    def __init__(
        self,
        multinet,
        element_index_power,
        element_index_gas,
        efficiency,
        name,
        name_power_net="power",
        name_gas_net="gas",
        element_type_power="sgen",
        desync_mode=False,
        in_service=True,
        order=0,
        level=0,
        drop_same_existing_ctrl=False,
        initial_run=True,
        **kwargs,
    ):
        super().__init__(
            multinet,
            element_index_power,
            element_index_gas,
            efficiency,
            name_power_net=name_power_net,
            element_type_power=element_type_power,
            name_gas_net=name_gas_net,
            in_service=in_service,
            order=order,
            level=level,
            drop_same_existing_ctrl=drop_same_existing_ctrl,
            initial_run=initial_run,
            **kwargs,
        )

        self.__load_regulation_multiplier = 1
        self.name = name
        self.power_gen = 0
        self._desync = desync_mode

        power_net = multinet[NETS_ACCESS][self.name_net_power]
        gas_net = multinet[NETS_ACCESS][self.name_net_gas]

        bus_gen = power_net[self.elm_type_power].loc[self.elm_idx_power, "bus"]
        junction_sink = gas_net.sink.loc[self.elm_idx_gas, "junction"]

        self._line_power = find_lines_for_bus(power_net, bus_gen)
        self._pipes_gas = find_pipes_for_junction(gas_net, junction_sink)

        self.ref_gas_consume = self.get_gas_consume(multinet)
        self.ref_power_production = self.get_power_production(multinet)

    def get_gas_consume(self, multinet):
        try:
            gas_sink = multinet[NETS_ACCESS][self.name_net_gas].sink.at[
                self.elm_idx_gas, "mdot_kg_per_s"
            ]
        except (ValueError, TypeError):
            gas_sink = (
                multinet[NETS_ACCESS][self.name_net_gas]
                .sink.loc[self.elm_idx_gas, "mdot_kg_per_s"]
                .values[:]
            )
        return gas_sink

    def get_power_production(self, multinet):
        try:
            power_gen = multinet[NETS_ACCESS][self.name_net_power][
                self.elm_type_power
            ].at[self.elm_idx_power, "p_mw"]
        except (ValueError, TypeError):
            power_gen = (
                multinet[NETS_ACCESS][self.name_net_power][self.elm_type_power]
                .loc[self.elm_idx_power, "p_mw"]
                .values[:]
            )
        return power_gen

    def time_step(self, multinet, _):

        if self.el_power_led:
            self.power_gen = (
                self.ref_power_production * self.__load_regulation_multiplier
            )
            self.gas_cons = (self.power_gen) / (
                self.conversion_factor_kgps_to_mw() * self.efficiency
            )
        else:
            self.gas_cons = self.ref_gas_consume * self.__load_regulation_multiplier
            self.power_gen = (
                self.gas_cons * self.conversion_factor_kgps_to_mw() * self.efficiency
            )

        self.write_to_net(multinet)

    def write_to_net(self, multinet):
        # we always have to write both values, as the regulation can change the static one.
        try:
            multinet[NETS_ACCESS][self.name_net_gas].sink.at[
                self.elm_idx_gas, "mdot_kg_per_s"
            ] = self.gas_cons
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_gas].sink.loc[
                self.elm_idx_gas, "mdot_kg_per_s"
            ] = self.gas_cons
        try:
            multinet[NETS_ACCESS][self.name_net_power][self.elm_type_power].at[
                self.elm_idx_power, "p_mw"
            ] = self.power_gen
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_power][self.elm_type_power].loc[
                self.elm_idx_power, "p_mw"
            ] = self.power_gen

    def control_step(self, multinet):
        self.time_step(multinet, 0)
        self.applied = True

    @property
    def nodes(self):
        return {
            self.name_net_power: (self.elm_type_power, self.elm_idx_power),
            self.name_net_gas: ("sink", self.elm_idx_gas),
        }

    @property
    def edges(self):
        return {
            self.name_net_power: self._line_power,
            self.name_net_gas: self._pipes_gas,
        }

    @property
    def power_cap(self):
        if self.el_power_led:
            return self.ref_power_production
        else:
            return (
                self.ref_gas_consume
                * self.conversion_factor_kgps_to_mw()
                * self.efficiency
            )

    @property
    def gas_cap(self):
        if not self.el_power_led:
            return self.ref_gas_consume
        else:
            return (self.ref_power_production) / (
                self.conversion_factor_kgps_to_mw() * self.efficiency
            )

    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value


def create_g2p(
    mn,
    bus_power,
    junction_gas,
    gas_consume,
    name="STD_G2P",
    efficiency=0.8,
    power_net_name="power",
    gas_net_name="gas",
):
    """
    Create a RegulatedG2PControlMultiEnergy and all necessary network elements for the given multinet.
    """

    gas_net = mn[NETS_ACCESS][gas_net_name]
    power_net = mn[NETS_ACCESS][power_net_name]
    g2p_gen = ppower.create_sgen(power_net, bus_power, p_mw=1)
    g2p_sink = ppipes.create_sink(
        gas_net, junction=junction_gas, mdot_kg_per_s=gas_consume
    )
    return RegulatedG2PControlMultiEnergy(mn, g2p_gen, g2p_sink, efficiency, name)


class RegulatedP2GControlMultiEnergy(P2GControlMultiEnergy):
    """Coupling controller representing a power2gas (P2G) unit.

    As base for the controller you need to define a gas source and a power load.
    The generated gas mass flow will be calculated based on the input energy represented by the power load,
    so the power load of the load element will be untouched - if not regulated. To regulate the unit you
    can use the property .regulation

    Example for constructing a P2G unit.
    ...
    p2g_id_el = ppower.create_load(power_net, bus = 0, p_mw = 1)
    p2g_id_gas = ppipes.create_source(gas_net, junction = 0, mdot_kg_per_s = 0.5)
    p2g = RegulatedP2GControlMultiEnergy(mn, p2g_id_el, p2g_id_gas, efficiency = 0.7, name="TEST_P2G")
    ...

    This creates a P2G unit using a power load of 1 mW. The conversion efficiency is 70%.
    Note again that the defined mass flow of the source is dropped, so it doesn't matter at all.
    """

    def __init__(
        self,
        multinet,
        element_index_power,
        element_index_gas,
        efficiency,
        name,
        desync_mode=False,
        name_power_net="power",
        name_gas_net="gas",
        in_service=True,
        order=0,
        level=0,
        drop_same_existing_ctrl=False,
        initial_run=True,
        **kwargs,
    ):

        super().__init__(
            multinet,
            element_index_power,
            element_index_gas,
            efficiency,
            name_power_net=name_power_net,
            name_gas_net=name_gas_net,
            in_service=in_service,
            order=order,
            level=level,
            drop_same_existing_ctrl=drop_same_existing_ctrl,
            initial_run=initial_run,
            **kwargs,
        )

        self.__load_regulation_multiplier = 1
        self.name = name
        self._desync = desync_mode
        power_net = multinet[NETS_ACCESS][self.name_net_power]
        gas_net = multinet[NETS_ACCESS][self.name_net_gas]

        bus_gen = power_net.load.loc[self.elm_idx_power, "bus"]
        junction_sink = gas_net.source.loc[self.elm_idx_gas, "junction"]

        self._line_power = find_lines_for_bus(power_net, bus_gen)
        self._pipes_gas = find_pipes_for_junction(gas_net, junction_sink)
        self.ref_power_load = self.get_power_load(multinet)

    def get_power_load(self, multinet):
        try:
            power_load = multinet[NETS_ACCESS][self.name_net_power].load.at[
                self.elm_idx_power, P_MW
            ]
        except (ValueError, TypeError):
            power_load = (
                multinet[NETS_ACCESS][self.name_net_power]
                .load.loc[self.elm_idx_power, P_MW]
                .values[:]
            )
        return power_load

    def get_source_production(self, multinet):
        try:
            prod = multinet[NETS_ACCESS][self.name_net_gas].source.at[
                self.elm_idx_gas, "mdot_kg_per_s"
            ]
        except (ValueError, TypeError):
            prod = (
                multinet[NETS_ACCESS][self.name_net_gas]
                .source.loc[self.elm_idx_gas, "mdot_kg_per_s"]
                .values[:]
            )
        return prod

    def control_step(self, multinet):
        self.time_step(multinet, 0)
        self.applied = True

    def time_step(self, multinet, _):
        self.power_load = self.ref_power_load * self.__load_regulation_multiplier
        self.mdot_kg_per_s = (
            self.power_load * self.conversion_factor_mw_to_kgps()[0] * self.efficiency
        )
        self.write_to_net(multinet)

    def write_to_net(self, multinet):
        try:
            multinet[NETS_ACCESS][self.name_net_gas].source.at[
                self.elm_idx_gas, "mdot_kg_per_s"
            ] = self.mdot_kg_per_s
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_gas].source.loc[
                self.elm_idx_gas, "mdot_kg_per_s"
            ].values[:] = self.mdot_kg_per_s
        try:
            multinet[NETS_ACCESS][self.name_net_power].load.at[
                self.elm_idx_power, P_MW
            ] = self.power_load
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_power].load.loc[
                self.elm_idx_power, P_MW
            ].values[:] = self.power_load

    @property
    def nodes(self):
        return {
            self.name_net_power: ("load", self.elm_idx_power),
            self.name_net_gas: ("source", self.elm_idx_gas),
        }

    @property
    def power_cap(self):
        return self.ref_power_load

    @property
    def gas_cap(self):
        return (
            self.ref_power_load
            * self.conversion_factor_mw_to_kgps()[0]
            * self.efficiency
        )

    @property
    def edges(self):

        return {
            self.name_net_power: self._line_power,
            self.name_net_gas: self._pipes_gas,
        }

    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value


def create_p2g(
    mn,
    bus_power,
    junction_gas,
    power_load,
    name="STD_P2G",
    efficiency=0.8,
    power_net_name="power",
    gas_net_name="gas",
):
    """
    Create a RegulatedP2GControlMultiEnergy and all necessary network elements for the given multinet.
    """

    gas_net = mn["nets"][gas_net_name]
    power_net = mn["nets"][power_net_name]
    p2g_id_el = ppower.create_load(power_net, bus=bus_power, p_mw=power_load)
    p2g_id_gas = ppipes.create_source(gas_net, junction=junction_gas, mdot_kg_per_s=0.5)
    return RegulatedP2GControlMultiEnergy(
        mn, p2g_id_el, p2g_id_gas, efficiency=efficiency, name=name
    )


class RegulatedP2HControlMultiEnergy(Controller):
    def __init__(
        self,
        multinet,
        element_index_power,
        heat_exchanger_id,
        efficiency,
        name,
        name_power_net="power",
        name_heat_net="heat",
        in_service=True,
        order=0,
        level=0,
        drop_same_existing_ctrl=False,
        initial_run=True,
        **kwargs,
    ):

        super().__init__(
            multinet,
            in_service,
            order,
            level,
            drop_same_existing_ctrl=drop_same_existing_ctrl,
            initial_run=initial_run,
            **kwargs,
        )

        self.name = name
        self.__load_regulation_multiplier = 1
        self.name_net_heat = name_heat_net
        self.name_net_power = name_power_net
        self.__heat_exchanger_id = heat_exchanger_id
        self.heat_energy = 0
        self.power_load = 0
        self.elm_idx_power = element_index_power
        self.efficiency = efficiency
        self.applied = False

        heat_net = multinet[NETS_ACCESS][self.name_net_heat]
        power_net = multinet[NETS_ACCESS][self.name_net_power]

        from_heat_junc = heat_net.heat_exchanger.loc[
            self.__heat_exchanger_id, "from_junction"
        ]
        to_heat_junc = heat_net.heat_exchanger.loc[
            self.__heat_exchanger_id, "to_junction"
        ]
        bus_gen = power_net.load.loc[self.elm_idx_power, "bus"]

        self._pipes_heat = dict(
            find_pipes_for_junction(heat_net, from_heat_junc, "from_junction")
        )
        self._pipes_heat.update(
            find_pipes_for_junction(heat_net, to_heat_junc, "to_junction")
        )
        self._line_power = find_lines_for_bus(power_net, bus_gen)
        self.ref_power_load = self.get_power_load(multinet)

    def initialize_control(self, _):
        self.applied = False

    def is_converged(self, _):
        return self.applied

    def get_power_load(self, multinet):
        try:
            power_load = multinet[NETS_ACCESS][self.name_net_power].load.at[
                self.elm_idx_power, "p_mw"
            ]
        except (ValueError, TypeError):
            power_load = (
                multinet[NETS_ACCESS][self.name_net_power]
                .load.loc[self.elm_idx_power, "p_mw"]
                .values[:]
            )
        return power_load

    def get_heat_production(self, multinet):
        try:
            return multinet[NETS_ACCESS][self.name_net_heat].heat_exchanger.at[
                self.__heat_exchanger_id, "qext_w"
            ]
        except (ValueError, TypeError):
            return (
                multinet[NETS_ACCESS][self.name_net_power]
                .heat_exchanger.loc[self.__heat_exchanger_id, "qext_w"]
                .values[:]
            )

    def time_step(self, multinet, _):

        self.power_load = self.ref_power_load * self.__load_regulation_multiplier

        self.heat_energy = self.calc_heat(self.power_load)
        self.write_to_net(multinet)

    def calc_heat(self, power_in_w):
        return power_in_w * self.efficiency

    def control_step(self, mn):
        self.time_step(mn, 0)
        self.applied = True

    def get_all_net_names(self):
        return [self.name_net_power, self.name_net_heat]

    def write_to_net(self, multinet):
        try:
            multinet[NETS_ACCESS][self.name_net_power].load.at[
                self.elm_idx_power, "p_mw"
            ] = self.power_load
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_power].load.loc[
                self.elm_idx_power, "p_mw"
            ] = self.power_load

        try:
            multinet[NETS_ACCESS][self.name_net_heat].heat_exchanger.at[
                self.__heat_exchanger_id, "qext_w"
            ] = -self.heat_energy
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_heat].heat_exchanger.loc[
                self.__heat_exchanger_id, "qext_w"
            ].values[:] = -self.heat_energy

    @property
    def edges(self):
        """Return all edges connected to the P2H unit.

        :return: dict, energy-network-name -> edges
        :rtype: Dict
        """

        return {
            self.name_net_power: self._line_power,
            self.name_net_heat: self._pipes_heat,
        }

    @property
    def nodes(self):
        return {
            self.name_net_power: ("load", self.elm_idx_power),
            self.name_net_heat: ("heat_exchanger", self.__heat_exchanger_id),
        }

    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value

    @property
    def heat_cap(self):
        return self.calc_heat(self.ref_power_load)

    @property
    def power_cap(self):
        return self.ref_power_load

    def state_as_dict(self):
        return {"regulation": self.regulation}


def create_p2h(
    mn,
    bus_power,
    junction_heat_from,
    junction_heat_to,
    heat_diameter_m=200e-3,
    name="STD_P2H",
    efficiency=0.8,
    p_mw=1,
    heat_net_name="heat",
    power_net_name="power",
):
    """
    Create a RegulatedP2HControlMultiEnergy and all necessary network elements for the given multinet.
    """

    power_net = mn[NETS_ACCESS][power_net_name]
    heat_net = mn[NETS_ACCESS][heat_net_name]
    p2h_gen = ppower.create_load(power_net, bus_power, p_mw=p_mw)
    p2h_heat_feed_in = ppipes.create_heat_exchanger(
        heat_net,
        from_junction=junction_heat_from,
        to_junction=junction_heat_to,
        diameter_m=heat_diameter_m,
        qext_w=-10000,
    )
    return RegulatedP2HControlMultiEnergy(
        mn, p2h_gen, p2h_heat_feed_in, efficiency, name
    )


class HistoryController(Controller):
    """Interface to the controller system of pandapower/pipes. Collect the data at each time step an shows
    live updating graphs.
    """

    def __init__(
        self,
        multinet,
        names,
        me_network,
        network_to_collect_types,
        in_service=True,
        order=0,
        level=0,
        drop_same_existing_ctrl=False,
        initial_run=True,
        **kwargs,
    ):
        super().__init__(
            multinet,
            in_service,
            order,
            level,
            drop_same_existing_ctrl=drop_same_existing_ctrl,
            initial_run=initial_run,
            **kwargs,
        )

        self._names = names
        self._me_network = me_network
        self._network_to_collect_types = network_to_collect_types

    def initialize_control(self, _):
        self.applied = False

    def get_all_net_names(self):
        return self._names

    def time_step(self, net, time):
        if time > 0:
            for net_name, types in self._network_to_collect_types.items():
                if net_name in net[NETS_ACCESS]:
                    for t in types:
                        self._me_network.add_history_table(
                            net_name, t, net[NETS_ACCESS][net_name][f"res_{t}"]
                        )

    def control_step(self, _):
        self.applied = True

    def is_converged(self, _):
        return self.applied
