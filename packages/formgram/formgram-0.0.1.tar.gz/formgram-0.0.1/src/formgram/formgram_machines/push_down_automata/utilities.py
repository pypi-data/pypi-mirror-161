"""This module provides functions to print push down automata
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

from formgram.formgram_machines.push_down_automata.grammar_interface import flatten


def to_jove(machine: dict) -> dict:
    """

    :param machine:
    :return:
    """
    jove_delta = {}

    for transition in flatten(machine["transitions"]):
        old_state, read_symbol, stack_head, next_state, stack_insert = transition
        key = (old_state, read_symbol, stack_head)
        value = (next_state, stack_insert)
        if key in jove_delta:
            jove_delta[key].append(value)
        else:
            jove_delta[key] = [value]

    return {
        "Q": machine["states"],
        "Sigma": machine["alphabet"],
        "Gamma": machine["stack_alphabet"],
        "Delta": jove_delta,
        "q0": machine["starting_state"],
        "z0": machine["initial_stack_symbol"],
        "F": machine["accepting_states"]
    }


def to_str(machine: dict) -> str:
    """

    :param machine:
    :return:
    """
    transitions = machine["transitions"]
    max_state_length = max(map(len, map(str, machine["states"])))
    max_stack_length = max(max(map(len, map(str, machine["stack_alphabet"]))), 4)
    max_symbol_length = max(max(map(len, map(str, machine["alphabet"]))), 4)
    length_tuple = (max_state_length, max_symbol_length, max_stack_length)
    starting_productions = [
        __to_str_single_line(*transition, length_tuple)
        for transition in flatten(transitions)
        if transition[0] == machine["starting_state"]
    ]
    other_productions = [
        __to_str_single_line(*transition, length_tuple)
        for transition in flatten(transitions)
        if transition[0] != machine["starting_state"]
    ]
    return "\n".join(starting_productions + other_productions)


def __to_str_single_line(
    state, read_symbol, stack_head, next_state, stack_push, length_tuple
) -> str:
    """
    
    :param state:
    :param read_symbol:
    :param stack_head:
    :param next_state:
    :param stack_push:
    :param length_tuple:
    :return:
    """
    return (
        f"{state:>{length_tuple[0]}}, {read_symbol!s:>{length_tuple[1]}}, {stack_head!s:>{length_tuple[2]}}"
        f"   |-->   {next_state:>{length_tuple[0]}}, {stack_push!s}"
    )
