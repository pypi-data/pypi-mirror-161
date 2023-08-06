""" This module contains the single top-level function validate_grammar_form

All other functions in this module are just there to be called by validate_grammar_form.
They are still considered "public" functions in case someone wants to only call specific
parts of this method.

To make sure that typing etc. is correct this module is a bit technical and in itself
does not necessarily help the understanding of formal grammars.

While reading the docstring of validate_grammar_form should suffice to learn the
basic idea of Chomsky-Grammar definition, the docstrings of the other functions
can grant some insight why the specific check is necessary.
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

def validate_grammar_form(grammar: dict) -> None:
    """Assert that all assumptions about the grammar are met

    If the correct grammar is not of the correct form Exceptions are raised.
    The correct form is defined as follows:

    -  :attr:`grammar` is of type :class:`dict`
    -  :attr:`grammar` has keys `"terminals"`, `"nonterminals"`, `"starting_symbol"`, `"productions"`
    -  :attr:`grammar["terminals"]` and :attr:`grammar["nonterminals"]` are of type :class:`set`
    -  :attr:`grammar["starting_symbol"]` is element of :attr:`grammar["nonterminals"]`
    -  :attr:`grammar["productions"]` is of type :class:`set[tuple[tuple, tuple]]`
    -  each element of :attr:`grammar["productions"]` has exactly two elements
    -  each side of each production is composed of elements of either
       :attr:`grammar["terminals"]` or :attr:`grammar["nonterminals"]`

    :param grammar: The input which is to be checked as weather it is a
        correctly defined grammar as stated in module description
    :raise:
        :TypeError: If the grammar is of wrong type
        :ValueError: If the grammar is not defined correctly the first error
            found is returned with a description why the validation failed
    """
    validate_grammar_type(grammar)
    validate_existence_of_necessary_keys(grammar)
    validate_types_of_grammar_keys(grammar)
    validate_terminal_non_terminal_disjointness(grammar)
    validate_starting_symbol_inclusion(grammar)
    validate_production_number_of_sides(grammar)
    validate_production_symbol_inclusion(grammar)


def validate_grammar_type(grammar: dict) -> None:
    """Assert that the grammar is a dict

    This is necessary to ensure that all methods which are needed by other parts
    of this project are supported by this grammar.

    :param grammar: object to check for grammar qualities
    :raises TypeError: If grammar is of wrong type
    """
    if not isinstance(grammar, dict):
        raise TypeError(
            f"The provided grammar {grammar} is not a dict,"
            f" consider creating a dict"
        )


def validate_existence_of_necessary_keys(grammar: dict) -> None:
    """Assert that all necessary keys are present in the dict

    These keys will be used as subscript every time a grammar is unpacked
    thus it is very important that they all exist.

    :param grammar: object to check for grammar qualities
    :raises ValueError: If a key misses
    """
    needed_keys = {"productions", "terminals", "nonterminals", "starting_symbol"}
    missing_keys = {key for key in needed_keys if key not in grammar.keys()}
    if missing_keys:
        raise ValueError(
            f"The provided grammar {grammar} misses following keys: {missing_keys}"
        )


def validate_types_of_grammar_keys(grammar: dict) -> None:
    """Assert that the grammar keys are of the correct type

    This means it is asserted that

    - :code:`grammar["terminals"]` and :code:`grammar["nonterminals"]` are :class:`set`
    - :code:`grammar["productions"]` is of type :class:`set[tuple[tuple, tuple]]`

    :param grammar: object to check for grammar qualities
    :raises TypeError: If a value of the object has wrong type
    """
    if not isinstance(grammar["terminals"], set):
        raise TypeError(
            f"The terminal set  of provided grammar {grammar} is not"
            f" of type Collection"
        )
    for symbol in grammar["terminals"]:
        if not isinstance(symbol, str):
            raise TypeError(
                f"There is a non-string terminal symbol {symbol}"
                f" in grammar {grammar}"
            )
    if not isinstance(grammar["nonterminals"], set):
        raise TypeError(
            f"The nonterminal set of provided grammar {grammar} is"
            f" not a set"
        )
    for symbol in grammar["nonterminals"]:
        if not isinstance(symbol, str):
            raise TypeError(
                f"There is a non-string nonterminal "
                f"symbol {symbol} in grammar {grammar}"
            )
    if not isinstance(grammar["productions"], set):
        raise TypeError(
            f"The production set of provided grammar {grammar} is"
            f" not of type set"
        )
    for production in grammar["productions"]:
        if not isinstance(production, tuple):
            raise TypeError(
                f"A production of provided grammar {grammar} is not"
                f" of type tuple. Offending production: {production}"
            )
        for side in production:
            if not isinstance(side, tuple):
                raise TypeError(
                    f"A side of a production of provided "
                    f"grammar {grammar} is not of type tuple. "
                    f"Offending side: {side} of production {production}"
                )


def validate_starting_symbol_inclusion(grammar: dict) -> None:
    """Assert that the starting_symbol is a nonterminal

    This is a core assumption of Chomsky Grammars

    :param grammar: object to check for grammar qualities
    :raises ValueError: If starting-symbol is not a nonterminal
    """
    if not grammar["starting_symbol"] in grammar["nonterminals"]:
        raise ValueError(
            f"The starting_symbol of provided grammar {grammar} is"
            f" not included in the set of nonterminals"
        )


def validate_terminal_non_terminal_disjointness(grammar: dict) -> None:
    """Assert that the terminal and nonterminal sets are disjoint

    nonterminals and terminals may not intersect. In fact nonterminals can be
    defined as anything used in the tuples of a side of a production from
    :code:`grammar["productions"]` which is not an element of the terminals set.

    This project however tracks the nonterminals independently so that they can
    be queried without iterating over productions and terminals. Allowing unused
    nonterminals to exist.

    Thus to ensure that the core principle of the alternative definition is not
    violated, disjunction of those two sets has to be checked.

    :param grammar: object to check for grammar qualities
    :raises ValueError: If terminals and nonterminals intersect
    """
    terminals = grammar["terminals"]
    non_terminals = grammar["nonterminals"]
    intersection = {symbol for symbol in terminals if symbol in non_terminals}
    if intersection:
        raise ValueError(
            f"The terminals and nonterminals of provided grammar"
            f" {grammar} are not disjoint. Offending intersection: "
            f"{intersection}"
        )


def validate_production_number_of_sides(grammar: dict) -> None:
    """Assert that each production has exactly two sides

    This is important as other functions of this project often unpack each
    production as

    :code:`left_hand_side, right_hand_side = production`

    This is only possible if there are exactly two members to unpack.

    :param grammar: object to check for grammar qualities
    :raises ValueError: If any the number of sides of any production is not two
    """
    for production in grammar["productions"]:
        if len(production) != 2:
            raise ValueError(
                f"A production of provided grammar {grammar} has "
                f"a wrong number of sides. Offending production "
                f"{production} has {len(production)} sides expected 2."
            )


def validate_production_symbol_inclusion(grammar: dict) -> None:
    """Assert that each symbol in any production is either a terminal or a nonterminal

    While one could define nonterminals as any symbol used in a production not
    element of terminals, this project tracks nonterminals separately.

    This means that if there are symbols in a side of any production which isn't
    either a terminal or a nonterminal, the separate tracking has failed.
    Meaning that functions of this project that query the set of
    nonterminals are not guaranteed to work correctly.

    :param grammar: object to check for grammar qualities
    :raises ValueError: If any side of any production has a symbol which is
        element of neither terminals nor nonterminals
    """
    # working with sets is a LOT faster than working with lists, as sets use hash-tables with a O(1) access time
    # while list containment checks are O(n)
    try:
        working_alphabet = set(grammar["terminals"]) | set(grammar["nonterminals"])
    except TypeError:
        working_alphabet = list(grammar["terminals"]) + list(grammar["nonterminals"])

    # now that the working alphabet is determined, do the actual work
    for production in grammar["productions"]:
        for side in production:
            offending_symbols = [
                symbol for symbol in side if symbol not in working_alphabet
            ]
            if offending_symbols:
                raise ValueError(
                    f"A side of a production in provided grammar "
                    f"{grammar} has symbols which are not in the "
                    f"working alphabet. Offending production "
                    f"{production} with offending symbols {offending_symbols}"
                )
