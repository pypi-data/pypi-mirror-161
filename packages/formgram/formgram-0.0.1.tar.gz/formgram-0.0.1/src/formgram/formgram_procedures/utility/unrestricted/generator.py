"""

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

from formgram.formgram_procedures.classifiers.chomsky_classifiers import is_context_free
from formgram.formgram_procedures.helper_functions.production_grouping import group_right_hand_sides_by_left_hand_sides
from formgram.formgram_procedures.transformations.context_free import to_monotone_start_form, to_epsilon_free_form
from formgram.formgram_procedures.utility.monotone.generator import apply_grouped_productions_to_word


def generate_words_with_limited_steps(grammar: dict, steps: int) -> set:
    """generate all words the grammar can produce with length shorter or equal to max_length

    :param grammar:
    :param steps:
    :return:
    """
    if is_context_free(grammar):
        grammar = to_monotone_start_form(grammar)
        grammar = to_epsilon_free_form(grammar)
    grouped_sides = group_right_hand_sides_by_left_hand_sides(grammar["productions"])
    current_words = {(grammar["starting_symbol"],)}
    reached_words = current_words.copy()
    for i in range(steps):
        to_iterate = (
            word
            for word in current_words
            if any({symbol not in grammar["terminals"] for symbol in word})
        )
        current_words = set()
        for word in to_iterate:
            creatable_words = apply_grouped_productions_to_word(word, grouped_sides)
            current_words.update(creatable_words)
        current_words.difference_update(reached_words)
        reached_words.update(current_words)

    return {
        word
        for word in reached_words
        if all({symbol in grammar["terminals"] for symbol in word})
    }
