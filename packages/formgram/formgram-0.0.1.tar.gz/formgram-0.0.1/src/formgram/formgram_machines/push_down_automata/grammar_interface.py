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

from itertools import product

from formgram.formgram_procedures.helper_functions.decorators import call_by_value
from formgram.formgram_procedures.transformations.context_free import to_greibach_normal_form, to_clean_form


@call_by_value
def from_context_free_grammar(grammar: dict, only_state_name: str = "q") -> dict:
    """Create a PDA with only one state from a context free grammar

    :param only_state_name: The name of the one state the resulting PDA has
    :param grammar:
    :return:
    """
    grammar = to_greibach_normal_form(grammar)
    actions = set()
    for production in grammar["productions"]:
        (nonterminal,), right_hand_side = production
        if not len(right_hand_side):
            terminal, nonterminals = None, None
        else:
            terminal, *nonterminals = right_hand_side
        nonterminals = tuple(nonterminals) if nonterminals else None
        source_state = target_state = only_state_name

        actions.add((source_state, terminal, nonterminal, target_state, nonterminals))

    # the machine expects a nested dict to work,
    sub_dict = {}
    for original_state, read_symbol, stack_head, new_state, stack_push in actions:
        if read_symbol not in sub_dict:
            sub_dict[read_symbol] = {}
        if stack_head not in sub_dict[read_symbol]:
            sub_dict[read_symbol][stack_head] = set()
        sub_dict[read_symbol][stack_head].add((new_state, stack_push))

    transition_relation_dict = {only_state_name: sub_dict}

    return {
        "accepting_states": {only_state_name},
        "initial_stack_symbol": grammar["starting_symbol"],
        "transitions": transition_relation_dict,
        "starting_state": only_state_name,
        "states": {only_state_name},
        "alphabet": grammar["terminals"],
        "stack_alphabet": grammar["nonterminals"],
    }


def flatten(transitions) -> tuple:
    """

    :param transitions:
    :return:
    """
    for old_state in transitions:
        for read_symbol in transitions[old_state]:
            for stack_head in transitions[old_state][read_symbol]:
                for next_state, stack_push in transitions[old_state][read_symbol][
                    stack_head
                ]:
                    yield old_state, read_symbol, stack_head, next_state, stack_push


def create_possible_right_hand_side_tails(stack_push, states, first_state, last_state):
    """

    :param stack_push:
    :param states:
    :return:
    """
    if not stack_push:
        return

    if len(stack_push) == 1:
        yield (f"[{first_state}, {stack_push[0]}, {last_state}]",)
        return

    possible_state_sequences = product(states, repeat=len(stack_push) - 1)
    for sequence in possible_state_sequences:
        yield (f"[{first_state}, {stack_push[0]}, {sequence[0]}]",) + tuple(
            f"[{sequence[i]}, {stack_push[i+1]}, {sequence[i+1]}]"
            for i in range(0, len(sequence) - 1)
        ) + (f"[{sequence[-1]}, {stack_push[-1]}, {last_state}]",)


@call_by_value
def to_context_free_grammar(machine: dict) -> dict:
    """

    :param machine:
    :return:
    """
    nonterminals = {
        f"[{state}, {stack_head}, {other_state}]"
        for state in machine["states"]
        for other_state in machine["states"]
        for stack_head in machine["stack_alphabet"]
    }
    productions = set()
    starting_symbol = "S"
    for state in machine["states"]:
        productions.add(
            (
                (starting_symbol,),
                (
                    f"[{machine['starting_state']}, {machine['initial_stack_symbol']}, {state}]",
                ),
            )
        )

    for old_state, read_symbol, stack_head, next_state, stack_push in flatten(
        machine["transitions"]
    ):
        right_hand_root = (read_symbol,) if read_symbol is not None else ()
        left_hand_symbols = {
            target_state: f"[{old_state}, {stack_head}, {target_state}]"
            for target_state in machine["states"]
        }
        for target_state, left_hand_symbol in left_hand_symbols.items():
            if not stack_push:
                productions.add(((left_hand_symbol,), right_hand_root))
            else:
                # build possible right_hand_sides
                right_hand_sides = {
                    right_hand_root + right_hand_tail
                    for right_hand_tail in create_possible_right_hand_side_tails(
                        stack_push, machine["states"], next_state, target_state
                    )
                }
                for right_hand_side in right_hand_sides:
                    productions.add(((left_hand_symbol,), right_hand_side))

    new_grammar = {
        "nonterminals": nonterminals,
        "terminals": machine["alphabet"],
        "starting_symbol": starting_symbol,
        "productions": productions,
    }
    return to_clean_form(new_grammar)
