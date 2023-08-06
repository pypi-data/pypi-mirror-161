"""This module provides functions to determine certain forms of type 1 grammars

It is assumed in this module that grammars are as described in :ref:`the package description <grammar description>`.

It is not checked if the grammars used as input are actually of type 1.
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

from formgram.formgram_procedures.classifiers.form_classifiers import has_separated_terminals, has_chomsky_normal_form
from formgram.formgram_procedures.helper_functions.decorators import call_by_value
from formgram.formgram_procedures.helper_functions.production_grouping import group_productions_by_producible_symbols, \
    group_right_hand_sides_by_left_hand_sides
from formgram.formgram_procedures.helper_functions.set_functions import powerset
from formgram.formgram_procedures.utility.context_free.helper import collect_nullable_symbols
from formgram.formgram_procedures.utility.unrestricted.helper import find_new_nonterminal


@call_by_value
def to_separated_terminals_form(grammar: dict) -> dict:
    """Transform context-free grammar by separating terminals from variables.

    If the grammar is already of the correct form a deepcopy is returned.
    Otherwise it is provided that terminals only appear as singletons and only
    on right hand sides, and only produced by single variables which produce
    nothing else.

    :param grammar: The grammar to be transformed
    :return: An equivalent grammar with its terminals seperated from its variables
    """
    if has_separated_terminals(grammar):
        return dict(grammar)  # grammar is of correct form, return a copy of it
    new_productions = set()

    # Create new nonterminals N_<symbol> for each terminal <symbol>
    # and a corresponding production N_<symbol> ::= <symbol>
    # Keep track of them in a dictionary with dict[<symbol>] = N_<symbol>.
    # For easier dict also do dict[non_terminal] = non_terminal.

    non_terminal_dictionary = {symbol: symbol for symbol in grammar["nonterminals"]}
    for terminal in grammar["terminals"]:
        new_terminal_non_terminal = find_new_nonterminal(grammar, f"N_{terminal}")
        non_terminal_dictionary[terminal] = new_terminal_non_terminal
        new_productions.add(((new_terminal_non_terminal,), (terminal,)))

    # Use said dictionary to replace all symbols with their dictionary stored
    # counterparts.
    # Skip this for productions with right hand length of 1, as either this is
    # already a production nonterminal ::= terminal, or nothing would be changed.

    for old_left_hand_side, old_right_hand_side in grammar["productions"]:
        new_left_hand_side = tuple(non_terminal_dictionary[symbol] for symbol in old_left_hand_side)
        new_right_hand_side = tuple(non_terminal_dictionary[symbol] for symbol in old_right_hand_side)
        if len(old_right_hand_side) == 1:
            new_productions.add((new_left_hand_side, old_right_hand_side))
        else:
            new_productions.add((new_left_hand_side, new_right_hand_side))

    # Finally: Return new grammar

    return {
        "terminals": grammar["terminals"],
        "nonterminals": set(non_terminal_dictionary.values()) - grammar["terminals"],
        "starting_symbol": grammar["starting_symbol"],
        "productions": new_productions,
    }


@call_by_value
def to_epsilon_free_form(grammar: dict) -> dict:
    """Remove all epsilon rules from the grammar by transformation

    An exception to this is if the left hand side is the starting symbol.
    This is done by adding new productions for all productions which include
    nonterminals in right hand side which have epsilon rules, by leaving those
    out of said right hand side.

    :examples:
    >>> grammar_string = '''
    >>> <S> ::= <A> <A> <A> | <A> <B> <A> |
    >>> <A> ::=
    >>> <B> ::= 'b'
    >>> '''
    >>> from formgram.formgram_procedures.txt_interface import parse
    >>> grammar = parse(grammar_string)
    >>> to_epsilon_free_form(grammar)
    {
        "terminals": {'b'},
        "nonterminals": {'S', 'A', 'B'}
        "productions": {
            (('S', ), ('A', 'B', 'A')),
            (('S', ), ('A', 'B')),
            (('S', ), ('B', 'A')),
            (('S', ), ('B')),
            (('S', ), ('A', 'A', 'A')),
            (('S', ), ('A', 'A')),
            (('S', ), ('A', )),
            (('S', ), ()),
            (('B', ), ('b', )),
        }
    }

    note that there a lot of unproductive productions in that form

    :param grammar: The grammar to be transformed
    :return: An equivalent grammar transformed to lack epsilon rules
    """

    # collect all symbols which can derive epsilon in any amount of steps
    nullable_symbols = collect_nullable_symbols(grammar)

    # remove direct epsilon productions
    # then for each production containing nullable symbols remove every combination
    # of them
    new_productions = set()
    for (non_terminal,), right_hand_side in grammar["productions"]:
        if not right_hand_side and non_terminal != grammar["starting_symbol"]:
            continue  # We remove all nullable productions, except for S -> []
        if not right_hand_side and non_terminal == grammar["starting_symbol"]:
            new_productions.add(((non_terminal,), right_hand_side))
            continue
        nullable_indices = {
            index
            for index, symbol in enumerate(right_hand_side)
            if symbol in nullable_symbols
        }
        index_powerset = powerset(nullable_indices)
        for index_set in index_powerset:
            if (
                len(index_set) == len(right_hand_side)
                and non_terminal != grammar["starting_symbol"]
            ):
                continue  # dont add new epsilon productions! EXCEPT FOR THE STARTING SYMBOL
            new_right_hand_side = tuple(
                symbol for i, symbol in enumerate(right_hand_side) if i not in index_set
            )
            new_productions.add(((non_terminal,), new_right_hand_side))

    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"],
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@call_by_value
def to_bifurcated_form(grammar: dict) -> dict:
    """Make sure the right hand sides of the grammar have at most two symbols

    This Function trims all productions with long right hand sides to length two.
    This is done by creating new interim nonterminals and using them to "glue"
    them together.

    For example
    :example:
    >>> grammar_string = '''<A> ::= <B> 'c' <D> 'e' <F>'''
    >>> grammar = parse(grammar_string)
    >>> new_grammar = to_bifurcated_form(grammar)
    >>> to_backus_naur_form(new_grammar)
    '''<A>   ::= <B> <A_1>
    <A_1> ::= 'c' <A_2>
    <A_2> ::= <D> <A_3>
    <A_3> ::= 'e' <F>'''


    :param grammar: The grammar to transform
    :return: The transformed grammar
    """
    new_productions = {
        production for production in grammar["productions"] if len(production[1]) <= 2
    }
    too_long_productions = {
        production for production in grammar["productions"] if len(production[1]) >= 3
    }
    additional_non_terminals = set()
    for (non_terminal,), right_hand_side in too_long_productions:
        current_symbol = non_terminal
        for i, symbol in enumerate(right_hand_side[:-2]):
            new_interim_non_terminal = find_new_nonterminal(
                grammar, f"{non_terminal}_{i + 1}"
            )
            additional_non_terminals.add(new_interim_non_terminal)
            new_right_hand_side = (right_hand_side[i], new_interim_non_terminal)
            new_productions.add(((current_symbol,), new_right_hand_side))
            current_symbol = new_interim_non_terminal
        new_productions.add(
            ((current_symbol,), (right_hand_side[-2], right_hand_side[-1]))
        )
    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"] | additional_non_terminals,
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@call_by_value
def to_unit_free_form(grammar: dict) -> dict:
    """Remove all unit rules from the production set of the grammar

    That is accomplished by adding all right hand sides of the target of a unit
    rule to the image of the source.

    :example:
    >>> grammar_string = '''
    >>> <A> ::= <B> <C> | <D>
    >>> <D> ::= <E> <F>'''
    >>> grammar = parse(grammar_string)
    >>> new_grammar = to_unit_free_form(grammar)
    >>> to_backus_naur_form(new_grammar)
    '''
    <A> ::= <B> <C> | <E> <F>
    <D> ::= <E> <F>
    '''

    :param grammar: The grammar to transform
    :return: A new unit production free grammar
    """
    # STEP 1: Determine Unit rules
    # Build a dictionary which remembers which nonterminal can replace which directly
    # Meanwhile collect all non-unit rules as new production rules

    unit_rules = {}
    new_productions = set()
    for left_hand_side, right_hand_side in grammar["productions"]:
        (left_hand_symbol,) = left_hand_side
        if len(right_hand_side) == 1 \
                and grammar["nonterminals"].issuperset(right_hand_side):
            (right_hand_symbol,) = right_hand_side
            if right_hand_symbol in unit_rules:
                unit_rules[right_hand_symbol].add(left_hand_symbol)
            else:
                unit_rules[right_hand_symbol] = {left_hand_symbol}
        else:
            new_productions.add((left_hand_side, right_hand_side))

    # STEP 2: Determine Chained Unit rules
    # <A> ::= <B>
    # <B> ::= <C>
    # would mean, we can replace <C> by either <B> or <A> in any production
    # adjust the dictionary accordingly.

    added_new_unit_rule = True
    while added_new_unit_rule:
        added_new_unit_rule = False
        for current_right_hand_symbol in unit_rules.keys():
            for other_right_hand_symbol, left_hand_symbols in unit_rules.items():
                if current_right_hand_symbol in left_hand_symbols:
                    current_left_symbols = unit_rules[current_right_hand_symbol]
                    if not left_hand_symbols.issuperset(current_left_symbols):
                        added_new_unit_rule = True
                        left_hand_symbols.update(current_left_symbols)

    # STEP 3: Add variations of all productions with unit producable left hand side
    # by "applying" the unit productions beforehand
    # <A> ::= <B>
    # <B> ::= 'b'
    # Would become
    # <B> ::= 'b'
    # <A> ::= 'b'
    # Note that the unit productions were skipped when collecting new_productions
    for (left_hand_symbol,), right_hand_side in new_productions.copy():
        if left_hand_symbol not in unit_rules:
            continue
        for symbol in unit_rules[left_hand_symbol]:
            new_productions.add(((symbol,), right_hand_side))

    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"],
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@call_by_value
def to_new_start_symbol_form(grammar: dict) -> dict:
    """Replace the old starting symbol with a new one only occurring on left hand sides

    This function takes a grammar and replaces its starting symbol with a new one.
    The new starting symbol will only be used in the Production
    <Start_1> ::= <Start>
    It is useful to make sure the starting symbol does not occur on right hand sides.

    :param grammar: The grammar to transform
    :return: A new grammar with a new starting symbol
    """
    original_starting_symbol = grammar["starting_symbol"]
    new_starting_symbol = find_new_nonterminal(grammar, original_starting_symbol)
    new_productions = grammar["productions"]
    new_productions.add(((new_starting_symbol,), (original_starting_symbol,)))
    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"].union({new_starting_symbol}),
        "starting_symbol": new_starting_symbol,
        "productions": new_productions,
    }


@call_by_value
def to_leftbound_start_form(grammar: dict) -> dict:
    """Assure that the starting symbol exists only on left hand sides.

    If the grammars starting symbol is already left bound, a copy of the input
    is returned.
    Else :py:func:`to_new_start_symbol_form` is called

    :param grammar: The grammar to transform
    :return: A new grammar with starting symol only occuring on left hand sides
    """
    productions = grammar["productions"]
    start_symbol = grammar["starting_symbol"]
    if not any(start_symbol in right_hand_side for _, right_hand_side in productions):
        # did not find any start symbol in right hand sides
        return grammar
    else:
        return to_new_start_symbol_form(grammar)


@call_by_value
def to_monotone_start_form(grammar: dict) -> dict:
    """Assure that the starting symbol can not be used to break monotonicity directly

    If there is a starting symbol production which breaks monotonicity the grammar
    is transformed into the left bound start form.

    The starting symbol can be used to break monotonicity if following statements are true:
    * The starting symbol exists on right hand sides
    * The starting symbol can produce the empty word

    If only the second statement is true, the monotonicity is only violated in the
    allowed special case needed for the grammar to produce the empty word.
    If only the first statement is true, monotonicity is not in danger due to the
    context free nature of the grammar.

    Note that monotonicity can still be broken indirectly using other nullable
    nonterminals. This function is only concerned with the special case of the
    starting symbol, to complement the to_epsilon_free_form function.

    :param grammar: The grammar to assure monotonicity of the staring symbol of
    :return: A grammar which starting symbol can not be used to break monotonicity
    """
    # check if starting-symbol is in right hand sides
    start_symbol = grammar["starting_symbol"]

    nullable_symbols = collect_nullable_symbols(grammar)
    if start_symbol not in nullable_symbols:
        # the starting symbol is not nullable
        return grammar

    return to_leftbound_start_form(grammar)


@call_by_value
def to_chomsky_normal_form(
    grammar: dict,
    order=("CHECK", "CLEAN", "START", "TERM", "BIN", "DEL", "UNIT", "CLEAN"),
) -> dict:
    """Transform context free grammar into chomsky normal form

    This is done by calling other functions in a specific order.
    The order of those other functions can be changed with the order parameter.

    :param grammar: The grammar to be transformed
    :param order: One can alter the order of subroutines this way. It may result
    in the returned grammar not being of chomsky normal form.

    Options:
    * CHECK     calls has_Chomsky_normal_form. Checks if given grammar is already
                a CNF, if so, returns given grammar without changes
    * CLEAN     calls to_clean_form. Removes all unreachable productions, and
                any production which can't ultimately produce a word.
    * START     calls to_monotone_start_form. Adds a new starting symbol if
                the start symbol was able to break monotonicity
    * START!    calls to_leftbound_start_form. Adds a new starting symbol regardless
    * TERM      calls to_seperated_terminals_form. Assures that right hand sides
                are either only terminals or only nonterminals
    * BIN       calls to_bifurcated_form. Assures that right hand sides are of
                length <= 2
    * DEL       calls to_epsilon_free_form. Assures that there are no epsilon
                productions in the grammar. An exception exists for the
                starting symbol
    * UNIT      calls to_unit_free_form. Assures that there are no productions
                which substitute a nonterminal symbol with exactly one other

    :return: An equivalent grammar in chomsky normal form
    """
    output_grammar = grammar
    for step in order:
        if step == "CHECK":
            if has_chomsky_normal_form(output_grammar):
                return output_grammar
        if step == "START":
            output_grammar = to_monotone_start_form(output_grammar)
        if step == "START!":
            output_grammar = to_new_start_symbol_form(output_grammar)
        if step == "TERM":
            output_grammar = to_separated_terminals_form(output_grammar)
        if step == "BIN":
            output_grammar = to_bifurcated_form(output_grammar)
        if step == "DEL":
            output_grammar = to_epsilon_free_form(output_grammar)
        if step == "UNIT":
            output_grammar = to_unit_free_form(output_grammar)
        if step == "CLEAN":
            output_grammar = to_clean_form(output_grammar)
    return output_grammar


@call_by_value
def to_clean_form(grammar: dict) -> dict:
    """Cleans the grammar from unusable symbols and productions

    This is done by first removing all productions which right hand sides can
    never exist.
    Then all productions which ultimately cant produce a word of only terminals
    are removed.
    Lastly all productions are scanned for used symbols and all symbols not in
    any production are removed from the grammar

    :param grammar: A context-free Grammar
    :return: the cleaned Grammar
    """
    return to_unused_symbol_free_form(
        to_unproductive_production_free_form(
            to_unreachable_production_free_form(grammar)
        )
    )


@call_by_value
def to_unproductive_production_free_form(grammar: dict) -> dict:
    """This function removes all productions which ultimately cant create a word

    This works by searching the production set for new productions which can
    be used to produce a word of terminals.
    All Symbols which can in that way produce a word of terminals are saved
    between iterations.
    When no new ones can be found, a last iteration over all productions is
    done removing all productions whose right hand side does contain other
    nonterminals

    :param grammar:
    :return:
    """
    new_terminable = {symbol for symbol in grammar["terminals"]}
    symbol_to_producing_productions_map = group_productions_by_producible_symbols(
        grammar["productions"]
    )

    for (nonterminal,), right_hand_side in grammar["productions"]:
        if not right_hand_side:
            new_terminable.add(nonterminal)

    terminable_symbols = new_terminable.copy()
    while new_terminable:
        old_terminable, new_terminable = new_terminable, set()
        for symbol in old_terminable:
            productions = symbol_to_producing_productions_map.get(symbol, set())
            for production in productions:
                (non_terminal,), right_hand_side = production
                if non_terminal not in terminable_symbols and all(
                    symbol in terminable_symbols for symbol in right_hand_side
                ):
                    new_terminable.add(non_terminal)
        terminable_symbols.update(new_terminable)

    new_productions = {
        ((left_hand_symbol,), right_hand_side)
        for ((left_hand_symbol,), right_hand_side) in grammar["productions"]
        if left_hand_symbol in terminable_symbols
        and terminable_symbols.issuperset(right_hand_side)
    }

    return {
        "productions": new_productions,
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"],
        "starting_symbol": grammar["starting_symbol"],
    }


@call_by_value
def to_unreachable_production_free_form(grammar: dict) -> dict:
    """This function removes all productions which cant be reached from start

    This is done by saving a set of all nonterminals reachable from start.
    (This starts with only the start symbol)
    Then each iteration all productions are applied and all reachable symbols
    are noted. This continues until no new symbols are reached.
        Then all productions which left hand side cant be reached are removed.

    :param grammar: A context free grammar
    :return: A context free grammar with no unreachable productions
    """
    reachable = {grammar["starting_symbol"]}
    nonterminals_reached_in_iteration = reachable
    grouped_productions = {
        symbol: right_hand_sides
        for (symbol,), right_hand_sides in group_right_hand_sides_by_left_hand_sides(
            grammar["productions"]
        ).items()
    }
    while nonterminals_reached_in_iteration:
        nonterminals_reached_last_iteration = nonterminals_reached_in_iteration
        nonterminals_reached_in_iteration = set()
        for reached_symbol in nonterminals_reached_last_iteration:
            if (
                reached_symbol in grammar["terminals"]
                or reached_symbol not in grouped_productions.keys()
            ):
                continue  # this symbol is not a nonterminal with associated productions
            for right_hand_side in grouped_productions[reached_symbol]:
                for symbol in right_hand_side:
                    if symbol not in reachable:
                        nonterminals_reached_in_iteration.add(symbol)
        reachable.update(nonterminals_reached_in_iteration)
    new_productions = set()

    for symbol in reachable.intersection(grouped_productions.keys()):
        new_productions.update(
            (
                ((symbol,), right_hand_side)
                for right_hand_side in grouped_productions[symbol]
            )
        )
    return {
        "terminals": grammar["terminals"],
        "nonterminals": grammar["nonterminals"],
        "productions": new_productions,
        "starting_symbol": grammar["starting_symbol"],
    }


@call_by_value
def to_unused_symbol_free_form(grammar: dict) -> dict:
    """This function removes all symbols which are not used by productions

    This simply iterates over all productions and looks for used symbols and
    then intersects those with the provided symbol sets.

    Note though, that the starting symbol will be kept in the nonterminal set
    even if it is never used in a production, as it is required to exist by
    definition.

    :param grammar: A recursively enumerable grammar
    :return: A grammar without symbols which are not used
    """
    alphabet = set()
    for production in grammar["productions"]:
        for side in production:
            for symbol in side:
                alphabet.add(symbol)
    return {
        "terminals": alphabet.intersection(grammar["terminals"]),
        "nonterminals": alphabet.intersection(grammar["nonterminals"]) | {grammar["starting_symbol"]},
        "productions": grammar["productions"],
        "starting_symbol": grammar["starting_symbol"],
    }


@call_by_value
def to_left_recursion_free_form(grammar: dict) -> dict:
    """Remove all left recursions from context free grammar

    :param grammar:
    :return:
    """
    sorted_nonterminals = sorted(grammar["nonterminals"])
    productions = grammar["productions"]
    new_nonterminals = set()
    for high_nonterminal in sorted_nonterminals:
        new_nonterminal = find_new_nonterminal(
            {
                "nonterminals": new_nonterminals.union(sorted_nonterminals),
                "terminals": grammar["terminals"],
            },
            f"{high_nonterminal}_left_reduction_removal",
        )
        new_nonterminals.add(new_nonterminal)
        for production in {
            production
            for production in productions
            if production[0][0] == high_nonterminal
            and production[1]
            and production[1][0] in sorted_nonterminals
            and production[1][0] < high_nonterminal
        }:
            low_nonterminal = production[1][0]
            for low_production in {
                production
                for production in productions
                if production[0][0] == low_nonterminal
            }:
                _, right_hand_side = low_production
                productions.add(
                    ((high_nonterminal,), right_hand_side + production[1][1:])
                )
            productions.remove(production)

        for production in {
            production
            for production in productions
            if production[1]
            and production[0][0] == production[1][0] == high_nonterminal
        }:
            productions.add(((new_nonterminal,), production[1][1:]))
            productions.add(
                ((new_nonterminal,), production[1][1:] + (new_nonterminal,))
            )
            productions.remove(production)

        for production in {
            production
            for production in productions
            if production[0][0] == high_nonterminal
            and (not production[1] or production[1][0] != high_nonterminal)
        }:
            productions.add(((high_nonterminal,), production[1] + (new_nonterminal,)))

    grammar["nonterminals"] |= new_nonterminals
    grammar["productions"] = productions
    return grammar


@call_by_value
def to_greibach_normal_form(grammar: dict) -> dict:
    """Transform grammar into the greibach normal form

    :param grammar:
    :return:
    """
    if not has_chomsky_normal_form(grammar):
        grammar = to_chomsky_normal_form(grammar)
    grammar = to_left_recursion_free_form(grammar)
    grammar = to_clean_form(grammar)
    productions = grammar["productions"]
    for nonterminal in sorted(grammar["nonterminals"], reverse=True):
        for production in productions.copy():
            (left_hand_symbol,), right_hand_side = production
            if right_hand_side and right_hand_side[0] == nonterminal:
                for replacement_production in productions.copy():
                    if replacement_production[0][0] == nonterminal:
                        productions.add(
                            (
                                (left_hand_symbol,),
                                replacement_production[1] + right_hand_side[1:],
                            )
                        )
                productions.remove(production)
    grammar["productions"] = productions
    return grammar
