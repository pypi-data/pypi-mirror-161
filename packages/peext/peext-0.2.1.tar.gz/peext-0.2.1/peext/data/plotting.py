"""Plotting for creating, in "real" time, updating plots of the state of the multinetwork. 
"""
from typing import Dict, List, Tuple
import numpy as np

import matplotlib.pyplot as plt

from peext.core import MESModel, RegulatableMESModel
from peext.node import EmptyBusNode, EmptyJunctionNode, RegulatableController
import peext.network as network
from peext.network import NETS_ACCESS, get_bus_junc

plt.style.use('ggplot')

def check_to_plot(graph_model: MESModel, plot_config_comp_list: List):
    """Checks if the component is listed in the to_plot area of the plotting config.
    There are two ways to list it there:
    1. by name (compare .name() with string in config)
    2. by id (as the id is only unique per table, we compare network_name, component_type and the id itself)

    :param graph_model: the model
    :type graph_model: MESModel
    :param plot_config_comp_list: entries in the to_plot area 
    :type plot_config_comp_list: List
    :return: True if the model should be plotted, False otherwise
    :rtype: bool
    """
    for comp in plot_config_comp_list:
        if graph_model.name() == comp:
            return True
        if isinstance(comp, Tuple) and graph_model.network.name == comp[0] and graph_model.component_type() == comp[1] and graph_model.id == comp[2]:
            return True
    return False

def gen_id(node):
    return f'{node.network.name}:{node.component_type()}:{node.id}'

def update_plots(plot_data_dict: Dict, me_network: network.MENetwork, plot_config=None, only_update=False, block=False, time_steps=100):
    """Update all plots configured in plot_config. 

    :param plot_data_dict: Persistent plot data (can be empty first time)
    :type plot_data_dict: Dict
    :param me_network: Network representing the MES
    :type me_network: network.MENetwork
    :param plot_config: configuration for the plot
    :type plot_config: Dict
    """
    if plot_config is not None:
        nodes_to_plot = list(filter(lambda node: check_to_plot(node, plot_config['to_plot']['nodes']), me_network.nodes))
        edges_to_plot = list(filter(lambda edge: check_to_plot(edge, plot_config['to_plot']['edges']), me_network.edges))
    else:
        nodes_to_plot = me_network.nodes
        edges_to_plot = me_network.edges

    # for controller: add all edges to plotting.
    for node in nodes_to_plot:
        if isinstance(node, RegulatableController):
            for _,edge_list in node.edges.items():
                edges_to_plot += [edge_tupel[0] for edge_tupel in edge_list]
    
    visited = []
    if len(nodes_to_plot) > 0:
        update_regulation_plot(plot_data_dict, nodes_to_plot, only_update, time_steps=time_steps)
    for i in range(len(nodes_to_plot)):
        node = nodes_to_plot[i]
        # bus/junction are not part of the graph data structure, but we need to collect their data
        if not isinstance(node, EmptyJunctionNode) and not isinstance(node, EmptyBusNode):
            bus_juncs = get_bus_junc(node)
            for el in bus_juncs:
                if el not in visited:
                    network = node.network[NETS_ACCESS][el[0]] if isinstance(node, RegulatableController) else node.network
                    junc_bus_node = EmptyBusNode(el[2], network) if el[1] == 'bus' else EmptyJunctionNode(el[2], network)
                    update_model_state_plot(gen_id(junc_bus_node), plot_data_dict, junc_bus_node, only_update, time_steps=time_steps)
                    visited.append(el)
        update_model_state_plot(gen_id(node), plot_data_dict, node, only_update, time_steps=time_steps)
    for i in range(len(edges_to_plot)):
        edge = edges_to_plot[i]
        if edge not in visited:
            update_model_state_plot(gen_id(edge), plot_data_dict, edge, only_update, time_steps=time_steps)
            visited.append(edge)

    update_grid_plot(plot_data_dict, me_network, only_update, time_steps=time_steps)

    if not only_update:
        if not block:    
            plt.pause(1/60)
        else:
            plt.show(block=True)

def update_grid_plot(plot_data_dict, me_network: network.MENetwork, only_update=False, time_steps=100):
    """Update grid wide plots (currently: energy balance).

    :param plot_data_dict: plot container
    :type plot_data_dict: Dict
    :param me_network: Network representing the MES
    :type me_network: network.MENetwork
    """
    if not 'grid' in plot_data_dict:
        plot_data_dict['grid'] = ([], [], None)

    x_data_list, y_data_list, axes = plot_data_dict['grid']

    if len(x_data_list) == 0:
        x_data_list.append(list(range(-time_steps,0,1)))
        y_data_list.append(np.zeros(time_steps))

    y_data_list[0] = np.append(y_data_list[0][1:], 0.0)
    y_data_list[0][-1] = me_network.power_balance()

    x_data_list[0] = np.append(x_data_list[0][1:], x_data_list[0][-1] + 1)

    axes = None
    if not only_update:
        axes = live_plotter_scaling(axes,
            y_data_list=y_data_list,
            x_data_list=x_data_list,
            label=['power balance'],
            title=['Generator/Load Balance'])

    plot_data_dict['grid'] = (x_data_list, y_data_list, axes)


def update_regulation_plot(plot_data_dict, nodes: List, only_update=False, time_steps=100):
    """Update the regulation plots, showing the current controller state of the node

    :param plot_data_dict: plot container
    :type plot_data_dict: Dict
    :param nodes: Nodes to update
    :type nodes: List
    """
    if not 'regulation' in plot_data_dict:
        plot_data_dict['regulation'] = ([], [], None)
        
    x_data_list, y_data_list, axes = plot_data_dict['regulation']

    for i in range(len(nodes)):
        node = nodes[i]
        if len(x_data_list) <= i:
            x_data_list.append(list(range(-time_steps,0,1)))
            y_data_list.append(np.zeros(time_steps))

        y_data_list[i] = np.append(y_data_list[i][1:], 0.0)
        y_data_list[i][-1] = node.regulation_factor()

        x_data_list[i] = np.append(x_data_list[i][1:], x_data_list[i][-1] + 1)

    axes = None
    if not only_update:
        axes = live_plotter_scaling(axes,
            y_data_list=y_data_list,
            x_data_list=x_data_list,
            label=['scaling' for _ in range(len(x_data_list))],
            title=[f'Agent {i} ({nodes[i].name()})' for i in range(len(nodes))])

    plot_data_dict['regulation'] = (x_data_list, y_data_list, axes)

def update_model_state_plot(name: str, plot_data_dict, model: MESModel, only_update=False, time_steps=100):
    """Update plot using the given model state

    :param name: name of the node/edge
    :type name: str
    :param plot_data_dict: plot container
    :type plot_data_dict: [type]
    :param model: Model representing the node/edge
    :type model: MESModel
    """
    if not name in plot_data_dict:
        plot_data_dict[name] = ([], [], None)
    
    x_data_list, y_data_list, axes = plot_data_dict[name]
    
    label_list = []
    i = 0
    for key in model.values_as_dict().keys():
        if len(x_data_list) <= i:
            x_data_list.append(list(range(time_steps)))
            y_data_list.append(np.zeros(time_steps))
        y_data_list[i] = np.append(y_data_list[i][1:], 0.0)
        y_data_list[i][-1] = model.values_as_dict()[key]
        i += 1
        label_list.append(key)

    if isinstance(model, RegulatableMESModel):   
        try:
            state_as_dict = model.state_as_dict()
            for key in state_as_dict.keys(): 
                if len(x_data_list) <= i:
                    x_data_list.append(list(range(time_steps)))
                    y_data_list.append(np.zeros(time_steps))
                y_data_list[i] = np.append(y_data_list[i][1:], 0.0)
                y_data_list[i][-1] = state_as_dict[key]
                i += 1
                label_list.append(key)
        except AttributeError:
            if len(x_data_list) <= i:
                x_data_list.append(list(range(-time_steps,0,1)))
                y_data_list.append(np.zeros(time_steps))

            y_data_list[i] = np.append(y_data_list[i][1:], 0.0)
            y_data_list[i][-1] = model.regulation_factor()

            x_data_list[i] = np.append(x_data_list[i][1:], x_data_list[i][-1] + 1)
            label_list.append('regulation')

    axes = None
    if not only_update:
        axes = live_plotter_scaling(axes, y_data_list=y_data_list, x_data_list=x_data_list, label=label_list, suptitle=model.name() if model.name() is not None else f"{model.network.name}:{model.component_type()}:{model.id}")
    else:
        axes = label_list
    plot_data_dict[name] = (x_data_list, y_data_list, axes)

def live_plotter_scaling(axes = None, y_data_list: List = None, x_data_list: List = None, step: float = 0.1, label: List[str] = None, title: List[str] = None, suptitle: str = ''):
    """Doing the actual drawing of the real time plots (one window)


    :param axes: shared axes defaults to None
    :type axes: matplotlib axe, optional
    :param y_data_list: y data list, defaults to None
    :type y_data_list: List, optional
    :param x_data_list: x data list, defaults to None
    :type x_data_list: List, optional
    :param step: time step, defaults to 0.1
    :type step: float, optional
    :param label: list of labels, defaults to None
    :type label: List[str], optional
    :param title: list of titles (per graph), defaults to None
    :type title: List[str], optional
    :param suptitle: suptitle (per window), defaults to ''
    :type suptitle: str, optional
    :return: axes
    :rtype: matplotlib axes
    """
    if axes == None:
        plt.ion()
        fig = plt.figure()
        fig.suptitle(suptitle)
        rows = int(np.ceil(np.sqrt(len(x_data_list))))
        cols = int(np.ceil(np.sqrt(len(y_data_list))))
        axes = []
        for i in range(len(y_data_list)):
            axes.append(fig.add_subplot(rows, cols, i+1))
        plt.show()

    for i in range(len(x_data_list)):
        y_data = y_data_list[i]
        x_data = x_data_list[i]
        axes[i].clear()
        if label is not None:
            axes[i].set_ylabel(label[i])
        if title is not None:
            axes[i].set_title(title[i])
        _, = axes[i].plot(np.array(x_data), np.array(y_data), color='r')

    return axes
