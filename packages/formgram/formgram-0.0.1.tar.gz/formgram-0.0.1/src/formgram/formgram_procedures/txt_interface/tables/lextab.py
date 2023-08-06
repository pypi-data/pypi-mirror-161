

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

# lextab.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion = "3.10"
_lextokens = set(("ARROW", "NEWLINE", "NONTERMINAL", "OR", "TERMINAL"))
_lexreflags = 64
_lexliterals = ""
_lexstateinfo = {"INITIAL": "inclusive"}
_lexstatere = {
    "INITIAL": [
        (
            "(?P<t_NEWLINE>\\n+)|(?P<t_NONTERMINAL><(?:[^\\\\<>\\'\\\"]|\\\\<|\\\\>|\\\\\\\\|\\\\\\'|\\\\\\\")+>)|(?P<t_TERMINAL>['\\\"](?:[^\\\\<>\\'\\\"]|\\\\<|\\\\>|\\\\\\\\|\\\\\\'|\\\\\\\")+['\\\"])|(?P<t_ignore_COMMENT>\\#.*)|(?P<t_ARROW>::=)|(?P<t_OR>\\|)",
            [
                None,
                ("t_NEWLINE", "NEWLINE"),
                ("t_NONTERMINAL", "NONTERMINAL"),
                ("t_TERMINAL", "TERMINAL"),
                (None, None),
                (None, "ARROW"),
                (None, "OR"),
            ],
        )
    ]
}
_lexstateignore = {"INITIAL": " \t\r"}
_lexstateerrorf = {"INITIAL": "t_error"}
_lexstateeoff = {"INITIAL": "t_eof"}
