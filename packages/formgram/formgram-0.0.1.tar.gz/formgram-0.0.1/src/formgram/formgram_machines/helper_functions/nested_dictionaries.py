
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

from formgram.formgram_procedures.helper_functions.decorators import call_by_value


@call_by_value
def insert_to_nested_dict(nested_dict: dict, insert: tuple) -> dict:
    """This function creates a new nested dictionary, with a new insertion

    The "core" of the nested dicts are sets.

    :examples:
    >>> d = {"a": {"b":  {"c": {1}}}
    >>> insert_to_nested_dict(d, ("a","b","d",{1,2,3}))
    {"a": {"b": {"c": {1}, "d": {1,2,3}}}

    :param nested_dict:
    :param insert: subscribable Iterable
    :return:
    """
    i = 0
    current = nested_dict
    try:
        for i, element in enumerate(insert[:-1]):
            current = current[element]
        current.add(insert[-1])
    except KeyError as e:
        structure = {insert[-1]}  # create the core as a set with single entry
        for element in list(insert)[i + 1 : -1][::-1]:  # nest dicts around the core
            structure = {element: structure}
        current[insert[i]] = structure
    return nested_dict


def create_nested_dict(edges: set) -> dict:
    """Create a nested dictionary from a set

    :examples:
    >>> edges = [("A", "a", "A"),
    >>>     ("A", None, "B"),
    >>>     ("A", "a", "C"),
    >>>     ("B", "b", "B"),]
    >>> create_nested_dict(edges)
    {
        "A" : {
            "a" : {"A", "C"},
            None : {"B", },
        },
        "B" : {
            "b" : {"B", },
    }

    :param edges:
    :return:
    """
    new_nested_dict = {}
    for data_tuple in edges:
        new_nested_dict = insert_to_nested_dict(new_nested_dict, data_tuple)
    return new_nested_dict
