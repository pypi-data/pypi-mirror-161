"""This module provides functions which work on any iterable

Currently the only function provided is the powerset function

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

import itertools
from typing import Collection, Iterable


def powerset(collection: Collection) -> Iterable:
    """This function returns an iterable powerset of the provided Collection

    Itertools are used for this as that package is quite optimized. It is a bit
    worse on very small collections but a lot faster for big collections compared
    to the naive for loop implementation

    :param collection: The Collection to return the powerset of
    :return: An itertools.chain object of the powerset of the provided Collection

    :examples:
    >>> list(powerset([1,2,3]))
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]

    """
    return itertools.chain.from_iterable(
        itertools.combinations(collection, length)
        for length in range(len(collection) + 1)
    )


def find_new_unique_string(previous_symbols: Collection, string_base: str) -> str:
    """Create a new string not in `previous_symbols` by adding numerals

    :rtype: object
    :param previous_symbols:
    :param string_base:
    :return:
    """
    if string_base not in previous_symbols:
        return string_base
    i = 2
    while f"{string_base}_{i}" in previous_symbols:
        i += 1
    return f"{string_base}_{i}"
