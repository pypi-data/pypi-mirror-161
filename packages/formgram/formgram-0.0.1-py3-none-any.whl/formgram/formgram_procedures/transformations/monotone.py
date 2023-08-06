"""This module provides functions to determine certain forms of type 1 grammars
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

from formgram.formgram_procedures.classifiers.chomsky_classifiers import is_context_sensitive, is_monotone, \
    replaces_exactly_one_non_terminal
from formgram.formgram_procedures.helper_functions.decorators import call_by_value
from formgram.formgram_procedures.transformations.context_free import to_separated_terminals_form
from formgram.formgram_procedures.utility.unrestricted.helper import find_new_nonterminal


@call_by_value
def to_context_sensitive_form(grammar) -> dict:
    """This function creates a context sensitive from a monotone grammar

    This is done by 2 steps:
    1. factorize the grammar
    2. Introduce new interim nonterminals T_1 ... T_n and partition all multi-productions
        into single productions like so:
        <A><B><C> ::= <D><E><F><G><H>
        becomes
        <A><B><C> ::= <T_1><B><C>
        <T_1><B><C> ::= <T_1><T_2><C>
        <T_1><T_2><C> ::= <T_1><T_2><T_3>
        <T_1><T_2><T_3> ::= <D><T_2><T_3>
        <D><T_2><T_3> ::= <D><E><T_3>
        <D><E><T_3> ::= <D><E><F><G><H>

    :param grammar:
    :return:
    """
    if not is_monotone(grammar):
        raise ValueError(
            "The monotone -> context sensitive Grammar transformation needs a monotone Grammar"
        )
    if is_context_sensitive(grammar):
        return grammar
    grammar = to_separated_terminals_form(grammar)
    new_productions = set()
    new_non_terminals = set()

    for production in grammar["productions"]:
        (left_hand_side, right_hand_side) = production
        if len(left_hand_side) == 1 or replaces_exactly_one_non_terminal(
            production, grammar["nonterminals"]
        ):
            new_productions.add(production)
            continue
        temp_symbols = tuple(
            find_new_nonterminal(grammar, f"INTERIM_{symbol}")
            for symbol in left_hand_side
        )
        new_non_terminals.update(temp_symbols)
        for i in range(len(left_hand_side)):
            # fill the sides with placeholder symbols
            new_left_hand_side = temp_symbols[:i] + left_hand_side[i:]
            new_right_hand_side = temp_symbols[: i + 1] + left_hand_side[i + 1 :]
            new_productions.add((new_left_hand_side, new_right_hand_side))
            # transform the placeholder symbols to right hand side
            new_left_hand_side = right_hand_side[:i] + temp_symbols[i:]
            if i < len(left_hand_side) - 1:
                new_right_hand_side = right_hand_side[: i + 1] + temp_symbols[i + 1 :]
            else:
                new_right_hand_side = right_hand_side
            new_productions.add((new_left_hand_side, new_right_hand_side))
    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"].union(new_non_terminals),
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }
