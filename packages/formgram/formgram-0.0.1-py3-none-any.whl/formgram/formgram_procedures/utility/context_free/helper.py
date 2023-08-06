"""
TODO write docu
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

def collect_nullable_symbols(grammar: dict) -> set:
    """Return the subset of nonterminals which can produce the empty word

     This function iterates over the collection of productions collecting all
     nonterminals which can directly produce the empty word.
     This collection of nullable nonterminals is then expanded each iteration by
     all nonterminals which can directly produce any word of only nullable symbols.
     The iterations continue until no new nonterminals are found.

    :examples:
    >>> grammar_string = '''
    >>> <S> ::= <A> <A> <A> | <A> <B> <A> |
    >>> <A> ::=
    >>> <B> ::= 'b'
    >>> '''
    >>> from formgram.formgram_procedures import parse
    >>> grammar = parse(grammar_string)
    >>> collect_nullable_symbols(grammar)
    {"S", "A"}

    :param grammar: The grammar to collect nullable nonterminals of
    :return: The set of nullable nonterminals
    """
    nullable_symbols = set()
    while True:
        newly_found_nullable_symbols = set()
        for (non_terminal,), right_hand_side in grammar["productions"]:
            if non_terminal not in nullable_symbols and nullable_symbols.issuperset(
                right_hand_side
            ):
                newly_found_nullable_symbols.add(non_terminal)
        nullable_symbols.update(newly_found_nullable_symbols)
        if not newly_found_nullable_symbols:
            return nullable_symbols
