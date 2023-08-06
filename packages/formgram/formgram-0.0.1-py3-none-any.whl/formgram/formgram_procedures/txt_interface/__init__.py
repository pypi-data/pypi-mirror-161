"""This package uses yacc to parse strings into grammar dicts

:examples:
>>> grammar_string = ''' # comments look like this and are permitted in the string
>>> <START> ::= <A> | 's' <START>
>>> 's''s'<A> ::= 's'<A>'s'
>>> <A> ::= <START> <START>
>>> 's'<A>'s' ::= 'a'
>>> <A> ::=  # this is an epsilon rule
>>> '''
>>> grammar = parse(grammar_string)
>>> grammar
{
    "terminals": {"s", "a"},
    "nonterminals": {"START", "A"},
    "productions": {
        (("START", ), ("A", )),
        (("START", ), ("s", "START")),
        (("s", "s", "A"), ("s", "A", "s")),
        (("A", ), ("START", "START")),
        (("s", "A", "s"), ("a", )),
        (("A", ), ())
    },
    "starting_symbol": "START"
}
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

from formgram.formgram_procedures.txt_interface.backus_naur_parser import parse
