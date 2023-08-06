#! /usr/bin/env python3
"""This module provides the parser for grammars

The class BackusNaurParser can be used to parse any grammar in Backus Naur form

A grammar of Backus Naur form
has: all nonterminals in `<>` brackets
all terminals in `''` quotes
a left and right hand seperator of `::=`
one production per line
possibly multiple right hand sides per production seperated by `|`

:examples:
>>> grammar_string = \"\"\"
>>> <START> ::= <A> | 's' <START>
>>> 's''s'<A> ::= 's'<A>'s'
>>> <A> ::= <START> <START>
>>> 's'<A>'s' ::= 'a'
>>> <A> ::=
>>> \"\"\"
>>> grammar = parse(grammar_string)
>>> #alternatively
>>> parser = BackusNaurParser()
>>> same_grammar = parser.run(grammar_string)
>>> #note that the last line right hand side is empty, thus an epsilon rule
>>> grammar
{"terminals": {"s", "a"},
 "nonterminals": {"START", "A"},
 "productions": {
 (("START", ), ("A", )),
  (("START", ), ("s", "START")),
  (("s", "s", "A"), ("s", "A", "s")),
  (("A", ), ("START", "START")),
  (("s", "A", "s"), ("a", )),
  (("A", ), ())},
 "starting_symbol": "START"}

As yacc works with docstrings there are no further docstrings in the classes of
this module which are not used by yacc
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

import re

import ply.lex as lex
import ply.yacc as yacc


def unescape(s, escape_list=["<", ">", "\\", "'", '"']):
    new_s = ""
    escape_toggle = False
    for char in s:
        if char == "\\" and not escape_toggle:
            escape_toggle = not escape_toggle
            continue
        if char in escape_list and not escape_toggle:
            raise ValueError(f"unescaped symbol {char}")
        if char in escape_list and escape_toggle:
            new_s += char
            escape_toggle = not escape_toggle
            continue
        if char not in escape_list and escape_toggle:
            raise ValueError(f"escaped wrong symbol {char}")
        new_s += char
    return new_s


class BackusNaurLexer:
    tokens = ("NONTERMINAL", "TERMINAL", "ARROW", "OR", "NEWLINE")

    t_ARROW = r"::="
    t_OR = r"\|"
    t_ignore = " \t\r"
    t_ignore_COMMENT = r"\#.*"

    def t_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        return t

    def t_NONTERMINAL(self, t):
        r"<(?:[^\\<>\'\"]|\\<|\\>|\\\\|\\\'|\\\")+>"
        r = r"<((?:[^\\<>'\"]|\\<|\\>|\\\\|\\\'|\\\")+)>"
        s = re.match(r, t.value).group(1)
        t.value = unescape(s)
        return t

    def t_TERMINAL(self, t):
        r"['\"](?:[^\\<>\'\"]|\\<|\\>|\\\\|\\\'|\\\")+['\"]"
        r = r"['\"]((?:[^\\<>\']|\\<|\\>|\\\\|\\\'|\\\")+)['\"]"
        s = re.match(r, t.value).group(1)
        t.value = unescape(s)
        return t

    def t_error(self, t):
        if not hasattr(self, "errors"):
            self.errors = []
        self.errors.append(
            f'Illegal Symbol "{t.value[0]}" at Position {t.lexpos} (line {t.lineno})'
        )
        t.lexer.skip(1)

    def t_eof(self, t):
        if hasattr(self, "errors"):
            raise ValueError("\n".join(self.errors))

    def __init__(self, debug: bool = False, optimize: bool = True):
        self.lexer = lex.lex(
            module=self,
            debug=debug,
            optimize=optimize,
            lextab="formgram.formgram_procedures.txt_interface.tables.lextab",
        )


class BackusNaurParser:
    tokens = BackusNaurLexer.tokens

    def p_trim(self, p):
        """trim : start
        | NEWLINE trim"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[1][0] == "\n":
                p[0] = p[2]
            else:
                p[0] = p[1]

    def p_start(self, p):
        """start : production newlines productions
        | production newlines
        | production
        """
        if len(p) > 3:
            p[0] = {
                "nonterminals": p[1]["nonterminals"] | p[3]["nonterminals"],
                "terminals": p[1]["terminals"] | p[3]["terminals"],
                "productions": p[1]["productions"] | p[3]["productions"],
            }
            p[0]["starting_symbol"] = p[1]["left_side"][0]
        else:
            p[0] = p[1]
            p[0]["starting_symbol"] = p[1]["left_side"][0]
            del p[0]["left_side"]

    def p_newlines(self, p):
        """newlines : NEWLINE
        | NEWLINE newlines
        """
        pass

    def p_productions(self, p):
        """productions : production newlines productions
        | production newlines
        | production"""
        if len(p) > 3:
            p[0] = {
                "nonterminals": p[1]["nonterminals"] | p[3]["nonterminals"],
                "terminals": p[1]["terminals"] | p[3]["terminals"],
                "productions": p[1]["productions"] | p[3]["productions"],
            }
        else:
            p[0] = p[1]

    def p_production(self, p):
        """production : side ARROW
        | side ARROW right_hand_sides"""
        if len(p) > 3:
            p[0] = {
                "nonterminals": p[1]["nonterminals"] | p[3]["nonterminals"],
                "terminals": p[1]["terminals"] | p[3]["terminals"],
                "productions": {(p[1]["side"], rhs) for rhs in p[3]["sides"]},
                "left_side": p[1]["side"],
            }
        else:
            p[0] = {
                "nonterminals": p[1]["nonterminals"],
                "terminals": p[1]["terminals"],
                "productions": {(p[1]["side"], ())},
                "left_side": p[1]["side"],
            }

    def p_right_hand_sides(self, p):
        """right_hand_sides : side OR right_hand_sides
        | OR right_hand_sides
        | side
        | side OR"""
        if len(p) == 4:
            p[0] = {
                "nonterminals": p[3]["nonterminals"] | p[1]["nonterminals"],
                "terminals": p[3]["terminals"] | p[1]["terminals"],
                "sides": p[3]["sides"] | {p[1]["side"]},
            }
        elif len(p) == 3:
            if p[1] == "|":
                p[0] = {
                    "nonterminals": p[2]["nonterminals"],
                    "terminals": p[2]["terminals"],
                    "sides": p[2]["sides"] | {()},
                }
            else:
                p[0] = {
                    "nonterminals": p[1]["nonterminals"],
                    "terminals": p[1]["terminals"],
                    "sides": {p[1]["side"]} | {()},
                }
        else:
            p[0] = {
                "nonterminals": p[1]["nonterminals"],
                "terminals": p[1]["terminals"],
                "sides": {p[1]["side"]},
            }

    def p_side_NONTERMINAL(self, p):
        """side : NONTERMINAL side
        | NONTERMINAL
        """
        if len(p) == 3:
            p[0] = {
                "nonterminals": p[2]["nonterminals"] | {p[1]},
                "side": (p[1],) + p[2]["side"],
                "terminals": p[2]["terminals"],
            }
        else:
            p[0] = {"nonterminals": {p[1]}, "side": (p[1],), "terminals": set()}

    def p_side_TERMINAL(self, p):
        """side : TERMINAL side
        | TERMINAL"""
        if len(p) == 3:
            p[0] = {
                "terminals": p[2]["terminals"] | {p[1]},
                "side": (p[1],) + p[2]["side"],
                "nonterminals": p[2]["nonterminals"],
            }
        else:
            p[0] = {"terminals": {p[1]}, "side": (p[1],), "nonterminals": set()}

    def p_error(self, p):
        raise ValueError(
            f"Could not finish parsing; No rule for Token {p.type}({p.value}) at position {p.lexpos} (line {p.lineno})"
        )

    def __init__(self, debug: bool = False, optimize: bool = True):
        self.lexer = BackusNaurLexer(debug=debug, optimize=optimize)
        self.parser = yacc.yacc(
            module=self,
            debug=debug,
            optimize=optimize,
            tabmodule="formgram.formgram_procedures.txt_interface.tables.parsetab",
        )

    @classmethod
    def run(cls, string, debug: bool = False, optimize: bool = True):
        return BackusNaurParser(debug=debug, optimize=optimize).parser.parse(string)


def parse(grammar_string: str, debug: bool = False, optimize: bool = True) -> dict:
    """This function parses a string to a grammar dict

    Strictly speaking this is just a wrapper of the BackusNaurParser class.

    :param grammar_string: A string as described in the module description
    :param debug: A boolean flag to decide if a log is to be created
    :param optimize: A boolean flag to decide if the precomputed tables are to be used
    :return: A grammar in form of dict as described in the module description
    """
    return BackusNaurParser.run(grammar_string, debug=debug, optimize=optimize)
