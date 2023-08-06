"""This Module encapsulates the helper functions of this package

The helper functions are functions which grant little to no insight into the
workings of formal languages and grammars but are non the less needed for other
functions to work.

Often times they are extracted from other functions for readability sake.
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

from typing import Sequence


def get_common_prefix(*sequences: Sequence) -> Sequence:
    """This function returns the longest common prefix of the input Sequences

    This is achieved by iterating over the shortest of the input Sequences
    until any other sequence has a differing symbol.

    If one is found the Sequence of symbols until that differing one is returned.
    Else the whole shortest Sequence must be the longest common prefix

    :param sequences: Multiple arguments of the same Sequence type
    :return: The longest common prefix of those Sequences
    :examples:

    >>> a = "hello world"
    >>> b = "hello wilhelm"
    >>> get_common_prefix(a, b)
    "hello w"

    >>> a = (1, 2, 3, 4)
    >>> b = (1, 2)
    >>> c = (1, 2, 3)
    >>> get_common_prefix(a, b, c)
    (1, 2)
    """
    # first get the minimum length sequence
    min_sequence = min(sequences, key=lambda seq: len(seq))

    # iterate over the minimum length sequence until any other sequence differs
    for index, symbol in enumerate(min_sequence):
        if any([seq[index] != symbol for seq in sequences]):
            return min_sequence[:index]  # [:index] is interval [0,index) integers
    return min_sequence  # no symbol differed, return shortest string


def get_common_suffix(*sequences: Sequence) -> Sequence:
    """This function returns the longest common suffix of the input Sequences

    This is achieved by reversing the sequences and calling get_common_prefix
    and then reversing that prefix again

    :param sequences: Multiple arguments of the same Sequence type
    :return: The longest common suffix of those Sequences
    :examples:

    >>> a = "hello world, how are you?"
    >>> b = "hello wilhelm, how can I call you?"
    >>> get_common_suffix(a, b)
    " you?"

    >>> a = (1, 2, 3, 4)
    >>> b = (1, 2, 4)
    >>> c = (1, 4)
    >>> get_common_prefix(a, b, c)
    (4,)
    """
    return get_common_prefix(*map(lambda seq: seq[::-1], sequences))[::-1]
