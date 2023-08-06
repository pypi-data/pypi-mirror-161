
from pandapower.control.basic_controller import Controller
from abc import abstractmethod

from peext.data.plotting import update_plots


class DataSink:

    @abstractmethod
    def start_write_to(me_network):
        pass

    @abstractmethod
    def write_to(me_network, step):
        pass

    @abstractmethod
    def end_write_to(me_network):
        pass

class PlottingController(Controller):
    """Interface to the controller system of pandapower/pipes. Collect the data at each time step an shows 
    live updating graphs.
    """
    def __init__(self, multinet, names, me_network, plot_config, in_service=True, order=0,
                 level=0, drop_same_existing_ctrl=False, initial_run=True, **kwargs):
        super().__init__(multinet, in_service, order, level,
                        drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run,
                        **kwargs)

        self._names = names
        self._me_network = me_network
        self._plot_data_list = {}
        self._plot_config = plot_config

    def initialize_control(self, _):
        self.applied = False

    def get_all_net_names(self):
        return self._names

    def time_step(self, net, time):
        if time > 0:
            update_plots(self._plot_data_list, self._me_network, self._plot_config)

    def control_step(self, _):
        self.applied = True

    def is_converged(self, _):
        return self.applied

class StaticPlottingController(PlottingController):
    """A non-live version of the PlottingController. Collects the data at each time-step and shows at the end of the time-series
    all plots.
    """
    def __init__(self, multinet, names, me_network, last_timestep, plot_config=None, only_collect=False, in_service=True, order=0,
                 level=0, drop_same_existing_ctrl=False, initial_run=True, **kwargs):
        super().__init__(multinet, names, me_network, plot_config, in_service, order, level,
                        drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run,
                        **kwargs)

        self._last_timestep = last_timestep
        self._only_collect = only_collect

    def time_step(self, _, time):
        if time == self._last_timestep and not self._only_collect:
            update_plots(self._plot_data_list, self._me_network, self._plot_config, only_update=False, block=True, time_steps=self._last_timestep)
            self._me_network = None
        elif time > 0:
            update_plots(self._plot_data_list, self._me_network, self._plot_config, True, time_steps=self._last_timestep)

    @property
    def result(self):
        return self._plot_data_list