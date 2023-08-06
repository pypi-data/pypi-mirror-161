"""
pda:
{
"transitions": ...,
"accepting_states": ...,
"initial_stack_symbol": ...,
"starting_state": ...,
"states": ...,
"alphabet": ....,
"stack_alphabet": ...
}

transitions:

{old_state:
    {read_symbol:
        {read_from_stack:
            {(next_state, insert_to_stack), ... }
        ,... }
    ,... }
,... }


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

from typing import Sequence, Tuple


def simulate_single_epsilon_step(
    transitions: dict, current_state: str, stack: Tuple[str]
) -> set:
    """

    :param transitions:
    :param current_state:
    :param stack:
    :return:
    """
    if not stack:
        return set()
    stack_head, *stack_tail = stack
    options = transitions.get(current_state, {}).get(None, {}).get(stack_head, set())
    return {
        (new_state, (insert_to_stack if insert_to_stack else ()) + tuple(stack_tail))
        for (new_state, insert_to_stack) in options
    }


def simulate_arbitrary_epsilon_steps(transitions: dict, combinations: set) -> set:
    """

    :param transitions:
    :param combinations:
    :return:
    """
    reached_combinations = combinations.copy()
    unexplored_combinations = combinations.copy()
    while unexplored_combinations:
        _state, _stack = unexplored_combinations.pop()
        new_combinations = simulate_single_epsilon_step(
            transitions, _state, _stack
        ).difference(reached_combinations)
        unexplored_combinations.update(new_combinations)
        reached_combinations.update(new_combinations)
    return reached_combinations


def simulate_single_symbol_step(
    transitions: dict, current_state: str, read_symbol: str, stack: Tuple[str]
) -> set:
    """

    :param transitions:
    :param current_state:
    :param read_symbol:
    :param stack:
    :return:
    """
    if not stack:
        return set()
    stack_head, *stack_tail = stack
    options = (
        transitions.get(current_state, {}).get(read_symbol, {}).get(stack_head, set())
    )
    return {
        (new_state, (insert_to_stack if insert_to_stack else ()) + tuple(stack_tail))
        for (new_state, insert_to_stack) in options
    }


def simulate_single_step(transitions: dict, combinations: set, read_symbol: str) -> set:
    """

    :param transitions:
    :param combinations:
    :param read_symbol:
    :return:
    """
    epsilon_hull = simulate_arbitrary_epsilon_steps(transitions, combinations)
    single_symbol_step = {
        combination
        for state, stack in epsilon_hull
        for combination in simulate_single_symbol_step(
            transitions, state, read_symbol, stack
        )
    }
    return simulate_arbitrary_epsilon_steps(transitions, single_symbol_step)


def run_full_simulation(
    machine: dict, input_tape: Sequence[str], variant: str = "stack accepting"
) -> bool:
    """

    :param machine:
    :param input_tape:
    :return:
    """

    options = simulate_arbitrary_epsilon_steps(
        machine["transitions"],
        {(machine["starting_state"], (machine["initial_stack_symbol"],))},
    )
    for symbol in input_tape:
        options = simulate_single_step(machine["transitions"], options, symbol)

        if not options:
            return False
    if variant == "state accepting":
        for (state, _) in options:
            if state in machine["accepting_states"]:
                return True
        return False
    else:
        for (_, stack) in options:
            if not stack:
                return True
        return False
