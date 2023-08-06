"""This module provides functions for deterministic and nondeterministic finite automata

The helper_functions themself are stored as dictionary with keys
* nodes: A set
* starting_nodes: a subset of nodes set
* accepting_nodes: a subset of nodes set
* alphabet: a set
* edges: a set of tuples (source_node, transition_symbol, target_node)

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

from typing import Sequence

from formgram.formgram_machines.finite_automata.classifiers import find_epsilon_edges
from formgram.formgram_machines.helper_functions.nested_dictionaries import insert_to_nested_dict, create_nested_dict


def create_shortest_epsilon_route_map(epsilon_rules: set, nodes: set = None) -> dict:
    """Create a nested dictionary containing the shortest routes only using epsilon edges

    If more then one shortest route using only epsilon edges exists between two
    nodes, the first found is used in the dictionary.

    This is done using an variation on the Floyd-Warshall algorithm.

    :example:
    >>> epsilon_rules = {
    >>>     (1, None, 2),
    >>>     (2, None, 3),
    >>>     (3, None, 4),
    >>>     (4, None, 1),
    >>> }
    >>> create_shortest_epsilon_route_map(epsilon_rules)
    {
        1: {
            2: ((1, None, 2), ),
            3: ((1, None, 2), (2, None, 3)),
            4: ((1, None, 2), (2, None, 3), (3, None, 4))
        },
        2: {
            3: ((2, None, 3), ),
            4: ((2, None, 3), (3, None, 4)),
            1: ((2, None, 3), (3, None, 4), (4, None, 1))
        }
        3: {
            4: ((3, None, 4), ),
            1: ((3, None, 4), (4, None, 1)),
            2: ((3, None, 4), (4, None, 1), (1, None, 2))
        }
        4: {
            1: ((4, None, 1), ),
            2: ((4, None, 1), (1, None, 2)),
            3: ((4, None, 1), (1, None, 2), (2, None, 3))
        }
    }

    :param nodes:
    :param epsilon_rules: A set of epsilon rules
    :return: A nested dictionary of shortest epsilon routes
    """
    if nodes is None:
        nodes = set()
        for edge in epsilon_rules:
            source, _, target = edge
            nodes.add(source)
            nodes.add(target)

    shortest_paths = dict()

    distances = {source: {target: float("inf") for target in nodes} for source in nodes}
    next_step_on_path = {source: {target: None for target in nodes} for source in nodes}
    for source in nodes:
        distances[source][source] = 0
        next_step_on_path[source][source] = source
    for edge in epsilon_rules:
        source, _, target = edge
        distances[source][target] = 1
        next_step_on_path[source][target] = target

    nodes = list(nodes)
    for intermediate in nodes:
        for source in nodes:
            for target in nodes:
                if (
                    distances[source][target]
                    > distances[source][intermediate] + distances[intermediate][target]
                ):
                    distances[source][target] = (
                        distances[source][intermediate]
                        + distances[intermediate][target]
                    )
                    next_step_on_path[source][target] = next_step_on_path[source][
                        intermediate
                    ]

    for source in nodes:
        for target in nodes:
            if next_step_on_path[source][target] is None or source == target:
                continue
            path = []
            current_node = source
            while current_node != target:
                next_node = next_step_on_path[current_node][target]
                path.append((current_node, None, next_node))
                current_node = next_node
            shortest_paths = insert_to_nested_dict(
                shortest_paths, (source, target, tuple(path))
            )

    return shortest_paths


def create_epsilon_hull(state_set: set, epsilon_route_map: dict) -> set:
    """Return a set of all states reachable with epsilon routes from the input set

    This includes taking no epsilon routes, therefore the returned set is a
    superset of the input set.

    :param state_set: A set to create the hull of
    :param epsilon_route_map: A map created by create_shortest_epsilon_route_map
    :return: the epsilon hull of state_set
    """
    reachable_nodes = state_set.copy()
    for state in state_set:
        if state in epsilon_route_map:
            reachable_nodes.update(epsilon_route_map[state])
    return reachable_nodes


def simulate_single_step(
    nested_edge_dict: dict, read_symbol, epsilon_route_map: dict, state_set: set
) -> set:
    """Return a set of reached states from a set of sets using a read symbol

    :param nested_edge_dict: A nested dictionary of machine edges sorted by source node -> symbol -> set of target nodes
    :param read_symbol: The symbol to process
    :param epsilon_route_map: as created by create_shortest_epsilon_route_map
    :param state_set: The set of states to
    :return: dictionary with keys
    """
    epsilon_hull = create_epsilon_hull(
        state_set=state_set, epsilon_route_map=epsilon_route_map
    )
    stepable_states = [
        state for state in epsilon_hull if read_symbol in nested_edge_dict[state]
    ]
    post_step_states = set()
    for state in stepable_states:
        post_step_states.update(nested_edge_dict[state][read_symbol])
    return post_step_states


def does_accept(machine: dict, word: Sequence) -> bool:
    """Determine if the given machine accepts the given string

    :param machine:
    :param word:
    :return:
    """
    return not machine["accepting_nodes"].isdisjoint(
        determine_parsing_state_sequence(machine, word)[-1]
    )


def determine_parsing_state_sequence(machine: dict, string: Sequence) -> Sequence[set]:
    """Return the sequence of sets which are reached by each step of the parsing

    :param machine:
    :param string:
    :return:
    """

    nested_edges = create_nested_dict(edges=machine["edges"])
    epsilon_map = create_shortest_epsilon_route_map(
        epsilon_rules=find_epsilon_edges(machine["edges"]), nodes=machine["nodes"]
    )
    state_sequence = []
    current_states = machine["starting_nodes"]
    state_sequence.append(current_states)

    for symbol in string:
        current_states = simulate_single_step(
            epsilon_route_map=epsilon_map,
            read_symbol=symbol,
            state_set=current_states,
            nested_edge_dict=nested_edges,
        )
        state_sequence.append(current_states)
    last_epsilon_hull = create_epsilon_hull(
        state_set=current_states, epsilon_route_map=epsilon_map
    )
    if last_epsilon_hull != current_states:
        state_sequence[-1] = last_epsilon_hull
    return state_sequence


def infer_machine_variables_from_productions(
    incomplete_machine: dict, purge_unused: bool = False
) -> dict:
    """Fill nodes and alphabet set from production set

    :param purge_unused:
    :param incomplete_machine:
    :return:
    """
    productions = incomplete_machine["productions"]
    if purge_unused:
        nodes = set()
        alphabet = set()
    else:
        nodes = incomplete_machine.get("nodes", default=set())
        alphabet = incomplete_machine.get("alphabet", default=set())

    for (source, symbol, target) in productions:
        nodes.add(source)
        nodes.add(target)
        alphabet.add(symbol)

    return {
        "nodes": nodes,
        "alphabet": alphabet,
        "productions": productions,
        "accepting_nodes": incomplete_machine["accepting_nodes"].intersection(nodes),
        "starting_nodes": incomplete_machine["starting_nodes"].intersection(nodes),
    }
