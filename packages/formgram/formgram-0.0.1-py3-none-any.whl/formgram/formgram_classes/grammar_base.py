"""This Module

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

from dataclasses import dataclass
from typing import Collection, Sequence, Tuple

from formgram.formgram_machines.finite_automata.classifiers import is_total, is_deterministic
from formgram.formgram_machines.finite_automata.grammar_interface import from_right_regular_grammar
from formgram.formgram_machines.finite_automata.simulation_functions import does_accept
from formgram.formgram_machines.finite_automata.transformations import to_deterministic
from formgram.formgram_procedures.classifiers.chomsky_classifiers import get_chomsky_type
from formgram.formgram_procedures.transformations.context_free import to_chomsky_normal_form, to_greibach_normal_form
from formgram.formgram_procedures.transformations.monotone import to_context_sensitive_form
from formgram.formgram_procedures.transformations.regular import to_left_linear_form, to_right_linear_form, \
    to_left_regular_form, to_right_regular_form
from formgram.formgram_procedures.txt_interface.backus_naur_parser import parse
from formgram.formgram_procedures.utility.unrestricted.helper import to_backus_naur_form


@dataclass(frozen=True)
class GrammarData:
    """Container for all internal values for any Grammar

    As it is a dataclass this already provides an __init__
    As it is frozen all internal values for any Grammar are fixed,
    this is so to prevent a Regular Grammar getting any non-regular productions
    """

    terminals: Collection[str]
    nonterminals: Collection[str]
    starting_symbol: str
    productions: Collection[Sequence[str]]


class Grammar(GrammarData):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) == dict:
            super().__init__(**args[0])  # construct from dictionary
        elif len(args) == 1 and type(args[0]) == str:
            super().__init__(**parse(args[0]))  # create a dictionary from bnf string
        else:
            super().__init__(*args, **kwargs)  # insert each argument manually

    def to_dict(self):
        return {
            "starting_symbol": self.starting_symbol,
            "nonterminals": self.nonterminals,
            "terminals": self.terminals,
            "productions": self.productions,
        }

    def __str__(self):
        return to_backus_naur_form(self.to_dict())

    def __repr__(self):
        return self.to_dict().__repr__()

    def elevate(self):
        """Return a new object of appropriate class corresponding to chomsky type

        :return:
        """
        chomsky_type = get_chomsky_type(self.to_dict())
        if chomsky_type == 0:
            return Grammar(self.to_dict())
        elif chomsky_type == 1:
            return MonotoneGrammar(self.to_dict())
        elif chomsky_type == 2:
            return ContextFreeGrammar(self.to_dict())
        else:
            return RegularGrammar(self.to_dict())


class MonotoneGrammar(Grammar):
    def to_context_sensitive(self) -> Grammar:
        return MonotoneGrammar(**to_context_sensitive_form(self.to_dict()))


class ContextFreeGrammar(MonotoneGrammar):
    def to_chomsky_normal_form(self) -> Grammar:
        return ContextFreeGrammar(**to_chomsky_normal_form(self.to_dict()))

    def to_greibach_normal_form(self) -> Grammar:
        return ContextFreeGrammar(**to_greibach_normal_form(self.to_dict()))


class RegularGrammar(ContextFreeGrammar):
    def to_left_linear_form(self):
        return RegularGrammar(**to_left_linear_form(self.to_dict()))

    def to_right_linear_form(self):
        return RegularGrammar(**to_right_linear_form(self.to_dict()))

    def to_left_regular_form(self):
        return RegularGrammar(**to_left_regular_form(self.to_dict()))

    def to_right_regular_form(self):
        return RegularGrammar(**to_right_regular_form(self.to_dict()))


@dataclass(frozen=True)
class FiniteAutomatonData:
    nodes: Collection[str]
    starting_nodes: Collection[str]
    accepting_nodes: Collection[str]
    alphabet: Collection[str]
    edges: Collection[Tuple[str, str, str]]


class FiniteAutomaton(FiniteAutomatonData):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) == dict:
            super().__init__(**args[0])  # construct from dictionary
        elif len(args) == 1 and type(args[0]) == RegularGrammar:
            super().__init__(
                **from_right_regular_grammar(args[0].to_right_regular_form.to_dict())
            )  # construct from BNF
        else:
            super().__init__(*args, **kwargs)  # insert each argument manually

    def __to_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "starting_nodes": self.starting_nodes,
            "accepting_nodes": self.accepting_nodes,
            "alphabet": self.alphabet,
            "edges": self.edges,
        }

    def does_accept(self, word: Sequence[str]) -> bool:
        return does_accept(machine=self.__to_dict(), word=word)

    def is_total(self) -> bool:
        return is_total(machine=self.__to_dict())

    def is_deterministic(self) -> bool:
        return is_deterministic(machine=self.__to_dict())

    def to_deterministic(self):
        return FiniteAutomaton(to_deterministic(self.__to_dict()))
