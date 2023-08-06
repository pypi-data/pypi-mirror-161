"""

"""

#  Copyright (c) 2022-2022 Theodor Möser
#  .
#  Licensed under the EUPL-1.2-or-later (the "Licence");
#  .
#  You may not use this work except in compliance with the Licence.
#  You may obtain a copy of the Licence at:
#  .
#  https://joinup.ec.europa.eu/software/page/eupl
#  .
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the Licence is distributed on an "AS IS" basis,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  .
#  See the Licence for the specific language governing
#  permissions and limitations under the Licence.

from formgram.formgram_machines.finite_automata.classifiers import is_deterministic, find_epsilon_edges
from formgram.formgram_machines.finite_automata.simulation_functions import create_shortest_epsilon_route_map, \
    create_epsilon_hull
from formgram.formgram_machines.helper_functions.nested_dictionaries import create_nested_dict
from formgram.formgram_procedures.helper_functions.decorators import call_by_value
from formgram.formgram_procedures.helper_functions.set_functions import powerset


@call_by_value
def to_deterministic(machine: dict) -> dict:
    """Transform to a deterministic finite automaton

    :param machine: Any finite automaton
    :return:
    """
    if is_deterministic(machine):
        return machine
    edge_dict = create_nested_dict(machine["edges"])
    node_powerset = powerset(machine["nodes"])
    accepting_powerset = {
        subset
        for subset in node_powerset
        if subset.intersection(machine["accepting_nodes"])
    }

    def to_node_string(subset):
        return "{" + ", ".join({str(x) for x in sorted(subset)}) + "}"

    epsilon_map = create_shortest_epsilon_route_map(
        find_epsilon_edges(machine["edges"])
    )
    new_edges = {}
    for source_set in node_powerset:
        epsilon_hull = create_epsilon_hull(
            epsilon_route_map=epsilon_map, state_set=source_set
        )
        for symbol in machine["alphabet"]:
            reached = {
                target
                for node in epsilon_hull
                for target in edge_dict[node].get(symbol, default={})
            }
            target_set = create_epsilon_hull(
                epsilon_route_map=epsilon_map, state_set=reached
            )
            new_edges.add(
                (to_node_string(source_set), symbol, to_node_string(target_set))
            )

    return {
        "nodes": {to_node_string(subset) for subset in node_powerset},
        "alphabet": machine["alphabet"],
        "edges": new_edges,
        "accepting_nodes": {to_node_string(subset) for subset in accepting_powerset},
        "starting_nodes": {to_node_string(machine["starting_nodes"])},
    }


@call_by_value
def to_unreachable_state_free_form(machine: dict) -> dict:
    """remove all nodes from machine, which are not reachable from a starting node

    :param machine:
    :return:
    """
    reachables = {node for node in machine["starting_nodes"]}
    new_reached = reachables
    symbol_agnostic_edge_dict = create_nested_dict(
        {(source, target) for (source, _, target) in machine["edges"]}
    )
    while new_reached:
        last_reached = new_reached
        new_reached = set()
        for node in last_reached:
            new_reached.update(symbol_agnostic_edge_dict[node].difference(reachables))
            reachables.update(symbol_agnostic_edge_dict[node])
    machine["nodes"] = reachables
    machine["accepting_nodes"] = machine["accepting_nodes"].intersection(reachables)
    return machine
