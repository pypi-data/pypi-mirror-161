
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

import copy
from functools import wraps
from typing import Callable


def call_by_value(function: Callable) -> Callable:
    """This decorator makes sure that all arguments are copied

    Makes use of copy.deepcopy to copy all arguments before passing to function

    :param function: The decorated function
    :return: The wrapped function, which first makes deep copies of all arguments
        before passing those on to the inner function
    :example:
    >>> a = [1,2,3]
    >>>
    >>> def bar(arr):
    >>>     for i, x in enumerate(arr):
    >>>         arr[i] = x**2
    >>>     return arr
    >>>
    >>> @call_by_value
    >>> def foo(arr):
    >>>     return bar(arr)
    >>>
    >>> foo(a)  # won't change the mutable argument
    [1, 4, 9]
    >>> a
    [1, 2, 3]
    >>> bar(a)  # will change the mutable argument
    [1, 4, 9]
    >>> a
    [1, 4, 9]
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        """This modified function deep copies every argument and passes them on

        :param args:
        :param kwargs:
        :return:
        """
        return function(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    return wrapper
