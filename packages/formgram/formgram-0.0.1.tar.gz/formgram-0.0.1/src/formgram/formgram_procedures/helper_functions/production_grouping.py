"""This module provides functions to sort the productions Collection of grammars





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

def group_right_hand_sides_by_left_hand_sides(productions: set) -> dict:
    """This function groups the productions by left hand side

    The output dictionary has the left hand sides of the productions as keys.
    Each key maps to a set of right hand sides corresponding to this left hand
    side.

    :examples:
    >>> grammar_string = '''<S> ::= <A> | <B>'''
    >>> grammar = parse(grammar_string)
    >>> grammar["productions"]
    {
        (("S", ), ("A", )),
        (("S", ), ("B", )),
    }
    >>> group_right_hand_sides_by_left_hand_sides(grammar["productions"])
    {
        ("S", ): {("A",) , ("B",)},
    }


    :param productions: A Collection of productions to group
    :return: A dictionary with left hand sides as keys and sets of all
             corresponding right hand sides as values
    """
    sorted_productions = {}
    for left_hand_side, right_hand_side in productions:
        if left_hand_side not in sorted_productions:
            sorted_productions[left_hand_side] = {right_hand_side}
        else:
            sorted_productions[left_hand_side].add(right_hand_side)
    return sorted_productions


def group_productions_by_producible_symbols(productions: set) -> dict:
    """This function creates a dictionary from productions by right hand symbols

    The keys are symbols found in right hand sides of productions,
    the values are sets of all productions including said symbol in right side

    :examples:
    >>> g_string = "<A> ::= 'b' <C> <D> | 'b'"
    >>> grammar = parse(g_string)
    >>> group_productions_by_producible_symbols(grammar["productions"])
     {"b": {(("A",), ("b", "C", "D")), (("A",),("b",))},
      "C": {(("A",), ("b", "C", "D"))},
      "D": {(("A",), ("b", "C", "D"))}}

    :param productions: A set of productions
    :return: a dictionary of productions grouped by symbols contained by them
    """
    structure = dict()
    for production in productions:
        _, right_hand_side = production
        for symbol in right_hand_side:
            if symbol in structure:
                structure[symbol].add(production)
            else:
                structure[symbol] = {production}
    return structure
