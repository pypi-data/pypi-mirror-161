"""This module provides functions to determine certain forms of type 0 grammars

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

from formgram.formgram_procedures.helper_functions.production_grouping import group_right_hand_sides_by_left_hand_sides
from formgram.formgram_procedures.helper_functions.set_functions import find_new_unique_string


def find_new_nonterminal(grammar: Mapping, base_symbol) -> str:
    """This function finds a name for a new non-terminal using a base symbol

    This function uses a base symbol for finding a new non-terminal.
    The base symbol will be cast to type `str` to form `base`
    The new name will be `<base>_<number>` where number will be the smallest
    possible. If the base string is not in the grammar it will be used instead

    :param grammar:
    :param base_symbol:
    :return:

    :example:
    >>> non_terminals = ["Start"]
    >>> grammar = {"nonterminals": non_terminals}
    >>> find_new_nonterminal(grammar, "new")
    "new"
    >>> a = find_new_nonterminal(grammar, "Start")
    >>> a
    "Start_2"
    >>> grammar["nonterminals"].append(a)
    >>> grammar["nonterminals"]
    ["Start", "Start_2"]
    >>> find_new_nonterminal(grammar, "Start")
    "Start_3"
    """
    return find_new_unique_string(grammar["nonterminals"] | grammar["terminals"], base_symbol)


def to_backus_naur_form(grammar: Mapping) -> str:
    """This function creates a string representation of the grammar

    The string representation is a variation on the backus naur form.
    It uses the same backus naur form variation which is used to parse grammars
    from string in the txt_interface subpackage.

    Note that the string representation casts all the symbols to string, if the
    symbol objects of the grammar do not support this an exception will be raised.

    Also as the txt_interface subpackage assumes that the first production uses
    the starting symbol as left hand side, this function will not work if there
    is no such production.
    The assumption is made that a grammar of only unreachable productions will
    occur seldomly enough that this special case can be safely ignored.

    :param grammar:
    :return:
    """

    def escape_character(character):
        protected_symbols = ["'", '"', "<", ">", "\\"]
        if character not in protected_symbols:
            return character
        else:
            return "\\" + character

    def escape_string(string):
        return "".join(map(lambda s: escape_character(s), string))

    def wrap_each_symbol_in_correct_delimiters(side):
        symbol_strings = []
        for symbol in side:
            if symbol in grammar["terminals"]:
                symbol_strings.append(f"'{escape_string(str(symbol))}'")
            else:
                symbol_strings.append(f"<{escape_string(str(symbol))}>")
        return " ".join(symbol_strings)

    grouped_productions = group_right_hand_sides_by_left_hand_sides(
        grammar["productions"]
    )
    output_dictionary = {}
    starting_left_hand_side = None
    for left_hand_side in grouped_productions.keys():
        if len(left_hand_side) == 1 and left_hand_side[0] == grammar["starting_symbol"]:
            starting_left_hand_side = left_hand_side
        output_dictionary[
            left_hand_side
        ] = f"{wrap_each_symbol_in_correct_delimiters(left_hand_side)} ::= {' | '.join((wrap_each_symbol_in_correct_delimiters(side) for side in sorted(grouped_productions[left_hand_side])))}"
    if starting_left_hand_side is None:
        raise ValueError(
            f"The provided grammar {grammar} has no production with a single starting-symbol "
            f"as left hand side"
        )
    starting_string = output_dictionary[starting_left_hand_side]
    output_string = "\n".join(
        {
            value
            for key, value in sorted(output_dictionary.items())
            if key != starting_left_hand_side
        }
    )
    return "\n".join([starting_string, output_string])
