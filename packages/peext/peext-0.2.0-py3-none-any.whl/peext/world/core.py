import asyncio
import os
import pickle

from pandapower.control.run_control import NetCalculationNotConverged
from pandapower.powerflow import LoadflowNotConverged
import pandapipes.multinet.control as ppmc
from peext.data.core import StaticPlottingController
import pandapipes

import peext.network as network


class MASWorld:

    def __init__(self, mas_coro_func, multinet, async_step_time=1/60, max_steps=None, name='MASWorld') -> None:
        self.__mas_coro_func = mas_coro_func
        self.__multinet = multinet
        self._me_network = None
        self._agents = None
        self._plotting_controller = None
        self._async_step_time = async_step_time
        self._max_steps = max_steps
        self._name = name
        
    @property
    def agents(self):
        return self._agents

    async def run(self):
        """start asyncio event loop
        """

        await self.prepare()
        await self.run_loop()

    async def prepare(self):
        self._me_network: network.MENetwork = network.from_panda_multinet(self.__multinet)

        mn_names = self._me_network.multinet['nets'].keys()
        self._plotting_controller = StaticPlottingController(self.__multinet, 
                                                              mn_names, 
                                                              self._me_network, 
                                                              self._max_steps-1,
                                                              only_collect=True)
        self.__multinet.controller.drop(self._plotting_controller.index, inplace=True)

        # initial single run for initial observation
        ppmc.run_control_multinet.run_control(self.__multinet, max_iter = 30, mode='all')
        
        # create learning agents and initialize models with network data
        _, self._agents = await self.__mas_coro_func(self._me_network)

    def write_results(self):
        if not os.path.isdir(self._name):
            os.mkdir(self._name)
        pandapipes.to_pickle(self._me_network.multinet, f"{self._name}/network.p")
        with open(f"{self._name}/network-result.p", "wb") as output_file:
            pickle.dump(self._plotting_controller.result, output_file)

    async def step(self):
        try:
            ppmc.run_control_multinet.run_control(self.__multinet, max_iter = 30, mode='all')
        except (NetCalculationNotConverged, LoadflowNotConverged) as ex:
            print("Multi-Net did not converge. This may be caused by invalid controller states: {0}".format(ex))

        # step time for mango
        await asyncio.sleep(self._async_step_time)

    async def run_loop(self):
        """Mainloop of the world simulation

        :param me_network: the MES network
        :type me_network: network.MENetwork
        :param panda_multinet: panda multinet
        :type panda_multinet: multinet
        :param plot_config: configuration of the plotting
        :type plot_config: Dict
        """
        step_num = 0
        while step_num < self._max_steps:
            # calculate new network results
            await self.step()
            print(step_num)
            self._plotting_controller.time_step(self.__multinet, step_num)
            step_num += 1
        
        self.write_results()