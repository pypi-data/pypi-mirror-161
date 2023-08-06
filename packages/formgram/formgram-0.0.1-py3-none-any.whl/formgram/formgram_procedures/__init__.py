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



"""This package provides functions to analyze and work with grammars of formal languages.

.. _grammar description:

It has a number of subpackages organizing those functions into loose categories.
Those subpackages are

#. classifiers
    which provides functions which can be used to analyze grammars
#. txt_interface
    which provides a single function to import grammars from a string
#. helper_functions
    which provides needed functions to other subpackages, which don't directly have anything to do with formal grammars
#. transformations
    which provides functions to turn grammars into grammars of other forms

The grammar object which is used anywhere else in this code is a :class:`dict` with keys

* "terminals"
    a :class:`set` of :class:`str` disjoint with nonterminals
* "nonterminals"
    a :class:`set` of :class:`str` disjoint with terminals
* "productions"
    a :class:`set` of production :class:`tuple`, each consisting of two :class:`tuple` consisting of entries of the
    terminals or nonterminals set.

    ``{(('S',), ('a',)), (('S',), ('a', 'S'))}``
* "starting_symbol"
    a :class:`str` from the nonterminals set

The :mod:`formgram_classes.txt_interface` subpackage provides :func:`formgram_classes.txt_interface.parse` which takes a string
formatted in a variant of the `Backus-Naur Form <https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form>`__ extended to
allow arbitrary words on the left hand side of ``::=``.

:example:
>>> from formgram.formgram_procedures.txt_interface import parse
>>> from formgram.formgram_procedures.classifiers.chomsky_classifiers import get_chomsky_type
>>> grammar_string = ''' <S> ::= 'a' <S> | <S> <S>
>>> 'a' <S> ::= 'a'
>>> '''
>>> grammar_dict = parse(grammar_string)
>>> get_chomsky_type(grammar_dict)
<ChomskyType.UNRESTRICTED: 0>
"""
