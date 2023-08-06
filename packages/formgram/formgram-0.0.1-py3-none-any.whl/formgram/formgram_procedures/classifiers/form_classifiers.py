"""This module provides classifiers to determine the form of a grammar.

Some information on grammars can be deduced by looking at their form, also other
functions of this project need the input grammar to be of the correct form,
so these functions provide a method to check if they need to be transformed
first.

It is assumed in this module that grammars are as described in :ref:`the package description <grammar description>`.
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

from typing import Mapping

from formgram.formgram_procedures.classifiers.chomsky_classifiers import is_context_free


def has_separated_terminals(grammar: Mapping) -> bool:
    """Determine if the provided grammar has its terminals separated.

    A grammar has separated terminals, if and only if all terminals only exist
    in right hand sides of length one and none exist in left hand sides at all.

    :param grammar: The provided grammar to check
    :return: If the provided grammar has its terminals separated
    """
    for left_hand_side, right_hand_side in grammar["productions"]:
        if any(symbol not in grammar["nonterminals"] for symbol in left_hand_side):
            return False
        if len(right_hand_side) > 1:
            if any(
                symbol not in grammar["nonterminals"] for symbol in right_hand_side
            ):
                return False
    return True


def has_bifurcating_productions(grammar: Mapping) -> bool:
    """Determine if the provided grammar has only right hand sides of length two or less

    It iterates over all productions and rejects if any production has a right hand side
    which is too long.

    :param grammar: The grammar to check
    :return: True if all right hand sides are len 2 or less, else False
    """
    for _, right_hand_side in grammar["productions"]:
        if len(right_hand_side) > 2:
            return False
    return True


def has_no_epsilon_productions(
    grammar: Mapping, starting_exception: bool = False
) -> bool:
    """Determine if there are epsilon productions in the grammar

    It iterates over all productions and checks for empty right hand sides

    :param grammar: Grammar to check
    :param starting_exception: If true, ignore starting symbol to epsilon productions
    :return: True if all right hand sides are non empty
    """
    for left_hand_side, right_hand_side in grammar["productions"]:
        if len(right_hand_side) == 0:
            if not (
                len(left_hand_side) == 1
                and left_hand_side[0] == grammar["starting_symbol"]
                and starting_exception
            ):
                return False
    return True


def has_no_unit_productions(grammar: Mapping) -> bool:
    """Determine if there are unit productions in the grammar

    Checks each production individually

    :param grammar: The grammar to check
    :return: True if there are no unit productions
    """
    for left_hand_side, right_hand_side in grammar["productions"]:
        if len(right_hand_side) == 1 and len(left_hand_side) == 1:
            left_symbol = left_hand_side[0]
            right_symbol = right_hand_side[0]
            nonterminals = grammar["nonterminals"]
            if right_symbol in nonterminals and left_symbol in nonterminals:
                return False
    return True


def has_chomsky_normal_form(grammar: Mapping, starting_exception: bool = True) -> bool:
    """Determine if grammar is of Chomsky normal form

    This is done by calling
    has_separated_terminals : Make sure terminals and nonterminals aren't mixing on right hand sides
    has_bifurcating_productions: Make sure all right hand sides are of length <= 2
    has_no_unit_productions: Make sure all right hand sides with length 1 are not nonterminals

    :param starting_exception: Boolean flag, if the starting symbol may be allowed to produce the empty string
    :param grammar: The grammar to check
    :return: True if grammar is of chomsky normal form else False
    """
    tests = [
        is_context_free(grammar),
        has_no_unit_productions(grammar),
        has_no_epsilon_productions(grammar, starting_exception=starting_exception),
        has_bifurcating_productions(grammar),
        has_separated_terminals(grammar),
    ]
    return all(tests)


def has_greibach_normal_form(grammar: Mapping) -> bool:
    """Determine if the provided grammar is of greibach normal form

    :param grammar:
    :return:
    """
    if not is_context_free(grammar):
        return False
    for production in grammar["productions"]:
        left_hand_side, right_hand_side = production
        if not right_hand_side:
            if left_hand_side[0] == grammar["starting_symbol"]:
                continue  # right hand side is empty
            else:
                return False  # only starting symbol may produce empty word
        head, *tail = right_hand_side
        if head in grammar["nonterminals"]:
            return False  # the first symbol of all right hand sides must be a terminal
        if len(tail) > 0 and grammar["terminals"].intersection(tail):
            return False  # all other right hand symbols must be nonterminals
    return True


