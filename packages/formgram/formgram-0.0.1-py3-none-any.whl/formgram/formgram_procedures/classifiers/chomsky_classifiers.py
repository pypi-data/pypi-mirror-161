"""This module provides functions for chomsky classification of grammars

It is assumed in this module that grammars are as described in :ref:`the package description <grammar description>`.

:examples:

.. container:: thebe

    .. code-block:: python3

        from formgram_procedures.classifiers.chomsky_classifiers import get_chomsky_type
        alphabet = {"a", }
        variables = {"A", "S"}
        starting_symbol = "S"
        productions = [
            (("S",), ("A",)),
            (("A",), ("a", "A")),
            (("A",), ("a",))
        ]
        grammar = {
            "terminals": alphabet,
            "nonterminals": variables,
            "starting_symbol": starting_symbol,
            "productions": productions
        }
        get_chomsky_type(grammar)

    .. container:: output

        <ChomskyType.REGULAR: 3>
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

from enum import IntEnum
from typing import Tuple

from formgram.formgram_procedures.helper_functions.input_validator import validate_grammar_form
from formgram.formgram_procedures.helper_functions.sequence_functions import get_common_prefix, get_common_suffix


class ChomskyType(IntEnum):
    """Provide a nice printable way to express Chomsky type

    The IntEnum Class makes sure that ChomskyType.MONOTONE == 1 evaluates true.
    However print(ChomskyType.MONOTONE) wont print 1 but "ChomskyType.MONOTONE"
    which is easier to read.
    """

    REGULAR = 3
    CONTEXT_FREE = 2
    MONOTONE = 1
    UNRESTRICTED = 0


def get_chomsky_type(grammar: dict) -> int:
    """Determine the chomsky type of given grammar

    This function calls the specific determining functions for all chomsky types
    in descending order.

    :param grammar: A Mapping as described in module description
    :return ChomskyType: An IntEnum between 0 and 3 named appropriately
    :raise:
        :TypeError: If the provided object does not provide the necessary methods
            needed by other functions of this project
        :ValueError: If the provided object is otherwise not of correct form for
            a Chomsky-Grammar
    """
    validate_grammar_form(grammar)
    if is_single_side_linear(grammar):
        return ChomskyType.REGULAR
    if is_context_free(grammar):
        return ChomskyType.CONTEXT_FREE
    if is_monotone(grammar):
        return ChomskyType.MONOTONE
    return ChomskyType.UNRESTRICTED


def is_grammar(grammar: dict) -> bool:
    """Check if given dict conforms meets package requirements for grammars

    The correct form is defined in the module description. As the checks are
    somewhat technical in nature the actual checking is done in another module
    called input_validator.

    :param grammar: The object to check for grammar form
    :return bool: True if grammar is of correct form else False
    """
    try:
        validate_grammar_form(grammar)
    except (TypeError, ValueError):
        return False
    return True


def is_monotone(grammar: dict, allow_starting_epsilon_productions: bool = True) -> bool:
    """Determine if production right hand sides are longer then left hand ones

    This is done by comparing the left and right hand sides of every single
    production individually.

    If the :attr:`allow_starting_epsilon_productions` flag is set, the special case of
    epsilon productions is handled by :func:`check_for_epsilon_special_case`

    :param grammar: The grammar to determine monotonicity of
    :param allow_starting_epsilon_productions: If this flag is set, monotonicity
        is allowed to be violated by productions with only the starting-symbol
        as their left hand side, under the condition, that the starting-symbol
        may not occur on any right hand side
    :return: True if no left hand side is longer than the corresponding right
        hand one
    """
    for left_hand_side, right_hand_side in grammar["productions"]:
        if len(right_hand_side) == 0 and allow_starting_epsilon_productions:
            continue  # skip if starting symbols may produce the emtpy word
        if len(left_hand_side) > len(right_hand_side):
            return False

    if allow_starting_epsilon_productions:
        return check_for_epsilon_special_case(grammar)
    else:
        return True


def replaces_exactly_one_non_terminal(
    production: Tuple[tuple], non_terminals: set
) -> bool:
    """Check if the left hand side is present on the right hand side sans exactly one nonterminal

    This is done by looking for each nonterminal in the left hand side:
    Are all the previous symbols a prefix of the right hand side
    and all following symbols a suffix of the right hand side?

    :param production: The production to be checked
    :param non_terminals: The Collection of non-terminal symbols
    :return: True if one can describe the left hand side though
        (common_prefix + one_non_terminal + common_suffix) else False
    """
    left_hand_side, right_hand_side = production
    left_non_terminals_enumerated = (
        (index, symbol)
        for index, symbol in enumerate(left_hand_side)
        if symbol in non_terminals
    )
    common_prefix = get_common_prefix(left_hand_side, right_hand_side)
    common_suffix = get_common_suffix(left_hand_side, right_hand_side)
    left_hand_length = len(left_hand_side)
    common_prefix_len, common_suffix_len = map(len, [common_prefix, common_suffix])
    for index, symbol in left_non_terminals_enumerated:
        # can deconstruct the left hand side into
        # prefix symbol suffix
        # now check if prefix in common prefix and suffix in common suffix.
        if (
            common_prefix_len >= index
            and common_suffix_len >= left_hand_length - index - 1
        ):  # - 1 as the non terminal itself must be considered
            return True
    return False


def is_context_free(grammar: dict) -> bool:
    """Determine if grammar is context free

    This means that the left hand side must be exactly one non-terminal

    :param grammar: The grammar to determine context-freedom of
    :return: True if grammar is context free else False
    """
    for left_hand_side, _ in grammar["productions"]:
        if len(left_hand_side) != 1 or left_hand_side[0] not in grammar["nonterminals"]:
            return False
    return True


def is_single_side_linear(grammar: dict) -> bool:
    """Determine if grammar is left or right linear

    For a grammar to be type 3 it first must be context free.
    Secondly it must be left linear or right linear, meaning that every
    right hand side of every production must have at most one non-terminal symbol
    which all must be either the left most or right most symbol.

    It is not allowed to mix left and right linear productions, which would make
    the grammar more expressive then type 3. Thus making it only linear which is
    a strict subset of context free languages but a strict superset of regular
    ones.

    :param grammar: The grammar to determine linearity of
    :return: True if the grammar is any kind of linear else False
    """
    if not is_context_free(grammar):
        return False
    return is_left_linear(grammar) or is_right_linear(grammar)


def is_left_linear(grammar: dict) -> bool:
    """Determine if grammar is left linear

    For a grammar to be left linear it must be context-free.
    Additionally every production must have at most one non-terminal symbol in
    each right hand side. In these right hand sides the nonterminals must be
    the leftmost symbol.

    :param grammar: The grammar to determine left linearity of
    :return: True if grammar is left linear else False
    """
    if not is_context_free(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if not right_hand_side:
            continue  # the empty word has at most one terminal!
        leftmost_symbol, *symbols = right_hand_side
        if any(symbol in grammar["nonterminals"] for symbol in symbols):
            return False  # only the leftmost symbol is allowed to be non-terminal
        if not symbols and leftmost_symbol not in grammar["terminals"]:
            return False  # there must be terminals

    return True


def is_right_linear(grammar: dict) -> bool:
    """Determine if grammar is right linear

    For a grammar to be right linear, it must be context free.
    Additionally every production must have at most one non-terminal symbol in
    each right hand side. In these right hand sides the nonterminals must be
    the rightmost symbol.

    :param grammar: The grammar to determine right linearity of
    :return: True if grammar is right linear else False
    """
    if not is_context_free(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if not right_hand_side:
            continue  # the empty word has at most one terminal!
        *symbols, rightmost_symbol = right_hand_side
        if any(symbol in grammar["nonterminals"] for symbol in symbols):
            return False  # only the rightmost symbol is allowed to be non-terminal
        if not symbols and rightmost_symbol not in grammar["terminals"]:
            return False  # there must be terminals
    return True


def is_regular(grammar: dict) -> bool:
    """Determine if grammar is right or left regular

    For a grammar to be regular it must be left- or right linear and every
    right hand side must be of length smaller then two.

    :param grammar: The grammar to determine regularity of
    :return: True if the grammar is regular else False
    """
    return is_left_regular(grammar) or is_right_regular(grammar)


def is_right_regular(grammar: dict) -> bool:
    """Determine if grammar is right regular

    For a grammar to be right regular it must be right linear with a maximal
    right hand side length of two.

    :param grammar: A context-free grammar to determine right regularity of
    :return: True if right linear with max right hand side of two else False
    """
    if not is_right_linear(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if len(right_hand_side) > 2:
            return False
    return True


def is_left_regular(grammar: dict) -> bool:
    """Determine if grammar is left regular

    For a grammar to be left regular it must be left linear with a maximal
    right hand side length of two.

    :param grammar: A context-free grammar to determine left regularity of
    :return: True if left linear with max right hand side of two else False
    """
    if not is_left_linear(grammar):
        return False
    for _, right_hand_side in grammar["productions"]:
        if len(right_hand_side) > 2:
            return False
    return True


def check_for_epsilon_special_case(grammar: dict) -> bool:
    """Check if only the starting symbol can (in-)directly produce the emtpy word

    If one is strict, context free grammars may not be monotone even though
    they are higher in the Chomsky-Hierarchy. This is due to the allowance of
    epsilon rules.

    If one does not allow any epsilon rules for monotone grammars, the Hierarchy
    breaks even for the language classes, as monotone grammars can not produce
    the language only containing the empty word.

    To add this special case one may allow productions of the form
    :math:`S \rightarrow \varepsilon`
    if and only if S is the starting symbol and does not occur in any right hand
    side.

    It can be shown that allowing S to still occur in right hand sides, would
    enable type-1 grammars to be as expressive as unrestricted ones.

    :param grammar: The grammar to check the epsilon production special case on
    :return: True if only the starting symbol produces the empty word and said
        symbol only ever occurs on the left hand side of productions
    """

    def is_epsilon_production(production):
        left_hand_side, right_hand_side = production
        return len(right_hand_side) == 0

    def is_starting_symbol_production(production):
        left_hand_side, right_hand_side = production
        return (
            len(left_hand_side) == 1 and left_hand_side[0] == grammar["starting_symbol"]
        )

    def has_starting_symbol_in_right_hand_side(production):
        left_hand_side, right_hand_side = production
        return grammar["starting_symbol"] in right_hand_side

    epsilon_productions = {
        production
        for production in grammar["productions"]
        if is_epsilon_production(production)
    }
    if any(
        not is_starting_symbol_production(epsilon_production)
        for epsilon_production in epsilon_productions
    ):
        return False

    if epsilon_productions and any(
        has_starting_symbol_in_right_hand_side(production)
        for production in grammar["productions"]
    ):
        return False

    return True


def is_context_sensitive(grammar: dict) -> bool:
    """Determine if grammar is of context sensitive form

    This means that the grammar must be monotone and for every production exactly
    one non-terminal of the left hand side must be replaced by a Sequence composed
    of terminals and/or nonterminals

    :param grammar: The grammar to determine context-sensitivity of
    :return: True if each production is context-sensitive
    """
    if not is_monotone(grammar):
        return False
    for production in grammar["productions"]:
        non_terminals = grammar["nonterminals"]
        if not replaces_exactly_one_non_terminal(production, non_terminals):
            return False
    return True
