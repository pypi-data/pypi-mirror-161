# pandaenergy-extension

Library for converting pandapower/pandapipes networks to a graph representation and extending controller functionality.

## Installing

The peext-library is available as package on PyPi, therfore you can install it using `pip`.

```bash
pip install peext
```

However, as usual, it is recommended to install it in a virtual environment:

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install peext
```

## Quickstart

In peext you can execute a steady-state time series simulation coupled with mango-agents using pandapower/pandapipes.

To setup the simulation you need to construct a `MASWorld` object and start the asyncio based simulation.

```python
import asyncio
import peext.scenario.network as pn
from peext.world.core import MASWorld

# construct the world using a coroutine constructing the mango
# container + agents
world = MASWorld(create_mas, pn.create_small_test_multinet(), max_steps=10)

# Start the simulation using asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(future=world.run())
```

In this example a `MASWorld` is constructed using the mango setup routine `create_mas` and the small multi energy test network `pn.create_small_test_multinet()`. The mango setup routine could look like this.

```python
async def create_mas(me_network: MENetwork):
    """Create a multi agent system within a single container.

    :param me_network: the network
    :type me_network: network.MENetwork
    :return: container the agents live in
    :rtype: Container
    """
    container = await Container.factory(addr=('127.0.0.2', 5555))
    agents = []
    for node in me_network.nodes: 
        a = RoleAgent(container)
        # random actions
        a.add_role(RandomRegulatorRole(node)) 
        agents.append(a)
           
    return container, agents
```
This coroutine-function will setup a mango-agent `Container` on port 5555 with the internal adress '127.0.0.2'. Also it creates an agent for every node in the multi-energy network. The network is represented by an instance of the `MENetwork` class. For more information about defining roles, creating agents in mango, consult the mango documentation (https://mango-agents.readthedocs.io/en/latest/).


## Package documentation

In this section the important packages (and their important classes), their objective and capabilities are described. 

### MASWorld

A `MASWorld` (`peext.world.core`) is capable of coupling a mango-agents simulation with a multi-energy pandapipes controller simulation. It expects at least 2 object: 
* the multinet
* a coroutine-function, which setups mango-agents and containers.

Besides executing the simulation the World will collect data every step and persist the collected data and the network itself for later usage (f.e. with dcnv).

### MENetwork

The `MENetwork` is the central network model when using peext components and resides in the package `peext.network`. While pandapower/pipes uses pandas dataframes to store all informations about the components and the simulation results, the `MENetwork` represents every component by a node or an edge. Nodes are f.e. generators, loads, while edges f.e. are lines, pipes and trafos. In this representation buses and junctions are omitted. If the data is needed it can be accessed using the methods `get_bus_junc_res_data` and `get_bus_junc`. Exception: empty junctions and buses will be represented as own nodes.

### Pandapipes/Pandapower Controller

The peext-library implements a set of controller representing coupling points in the multi-energy network:

| Name  | Description  | Components | Modes |   
|---|---|---|---|
| CHPControlMultiEnergy  | Implements a regulatable (heat and power/gas) CHP coupling point with an optional heat storage  |  heat_exchanger, gen/sgen, sink, optional EnergyStorage | Power driven/Gas driven  |  
| RegulatedG2PControlMultiEnergy  | Implements a regulatable G2P coupling point. Essentially equivalent to CHPControllMultiEnergy with heat_regulation = 0  | gen/sgen, sink  | Power driven/Gas driven  |  
| RegulatedP2GControlMultiEnergy  | Implements a regulatable P2G coupling point.  |  source, load | Power driven  | 

Furthermore there are controllers to extend the capabilites of the MENetwork represenation and for collecting/plotting data:
* HistoryController
    * Collecting data for historical timesteps, providing a bridge to this data in the MENetwork instance
* PlottingController
    * Implements live plotting of a chosen set of components in matplotlib windows
* StaticPlottingController
    * Capable of collecting the network data every step. Used internally by the MASWorld for persisting the network results.
