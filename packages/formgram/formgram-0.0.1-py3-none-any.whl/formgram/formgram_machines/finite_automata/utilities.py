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

import graphviz

from formgram.formgram_procedures.helper_functions.decorators import call_by_value
from formgram.formgram_procedures.helper_functions.set_functions import find_new_unique_string


@call_by_value
def to_jove(machine: dict) -> dict:
    """

    :param machine:
    :return:
    """
    epsilon = ""
    if epsilon in machine["alphabet"]:
        raise ValueError("The empty string is needed by jove as epsilon, and can not be in the alphabet")

    jove_delta = {}
    for node, symbol, target_node in machine["transitions"]:
        if symbol is None:
            symbol = epsilon  # jove handles epsilon in a different way than formgram_procedures
        key = (node, symbol)
        if key in jove_delta:
            jove_delta[key].add(target_node)
        else:
            jove_delta[key] = {target_node}

    return {
        "Q": machine["states"],
        "Sigma": machine["alphabet"],
        "Q0": machine["starting_states"],
        "Delta": jove_delta,
        "F": machine["accepting_states"]
    }


@call_by_value
def to_dot(machine: dict, as_object: bool = False) -> dict:
    """

    :param as_object:
    :param machine:
    :return:
    """
    graph = graphviz.Digraph()
    pre_start_node_name = find_new_unique_string(previous_symbols=machine["alphabet"] | machine["control_symbols"], string_base="pre_start")
    graph.node(pre_start_node_name, shape="point")

    for accepting_node in machine["accepting_states"]:
        graph.node(accepting_node, shape="double_circle")
    for normal_node in machine["states"] - machine["accepting_states"]:
        graph.node(normal_node, shape="circle")
    for source, symbol, target in machine["transitions"]:
        graph.edge(source, target, label="symbol")

    if as_object:
        return graph
    else:
        return graph.source
