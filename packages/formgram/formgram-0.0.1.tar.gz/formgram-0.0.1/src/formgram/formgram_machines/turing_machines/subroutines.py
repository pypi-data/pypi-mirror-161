"""This module provides functions to add subroutines to turing machines

Each function takes machine, start_state, stop_state as parameters,
where start_state and stop_state must be states of the given machine.

The functions will than add states and transitions to the machine to provide
the wished functionality.
The transitions will start at the `start_state` and end with `stop_state`
to connect the added functionality into the existing machine.

The functions do NOT add new symbols to the tape alphabet to ensure consistency.
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

import inspect
from functools import wraps
from typing import Callable

from formgram.formgram_procedures.helper_functions.decorators import call_by_value
from formgram.formgram_procedures.helper_functions.set_functions import find_new_unique_string


def __check_state_inclusion(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        arguments = inspect.signature(function).bind(*args, **kwargs).arguments
        start_state = arguments["start_state"]
        stop_state = arguments["stop_state"]
        machine = arguments["machine"]

        if start_state not in machine["states"]:
            raise ValueError(f"state {start_state} not in the machine states")
        if stop_state not in machine["states"]:
            raise ValueError(f"state {start_state} not in the machine states")
        return function(*args, **kwargs)

    return wrapper


@__check_state_inclusion
@call_by_value
def add_move_to_matching_symbol_subroutine(machine: dict, start_state: str, stop_state: str, matching_symbols: set,
                                           direction: str) -> dict:
    """

    :param machine:
    :return:
    """
    if direction not in ["L", "R"]:
        # The "direction" S for stationary would not go anywhere
        raise ValueError(f"Found {direction} as direction, which is neither L nor R")

    internal_state = find_new_unique_string(previous_symbols=machine["states"],
                                            string_base=f"GO_{direction}_TILL_{matching_symbols}_FROM_{start_state}_TO_{stop_state}")

    for symbol in (machine["alphabet"] | machine["control_symbols"]) - matching_symbols:
        machine["transitions"].add(((start_state, symbol), (internal_state, symbol, direction)))
        machine["transitions"].add(((internal_state, symbol), (internal_state, symbol, direction)))

    for symbol in matching_symbols:
        machine["transitions"].add(((start_state, symbol), (stop_state, symbol, "S")))
        machine["transitions"].add(((internal_state, symbol), (stop_state, symbol, "S")))

    return machine


@__check_state_inclusion
@call_by_value
def add_delete_next_n_symbols_subroutine(machine: dict, start_state: str, stop_state: str, number_of_steps_to_move: int = 1) -> dict:
    """

    Assumes:
    * that the given tape has no blank symbols between two non-blank symbols
    * that the subroutine is started on a non-blank symbol


    :param machine:
    :return:
    """
    tape_symbols = machine["alphabet"] | machine["control_symbols"]
    blank = machine["blank_symbol"]

    to_read_direction = "R"
    to_write_direction = "L"

    # create new states

    # We dont know how the states will be named, only what the base string is
    # so we keep track of the actual states by storing them in a dict with their
    # base key string as key
    state_dict = {}

    for blank_symbols_read in range(number_of_steps_to_move):
        for steps_taken in range(number_of_steps_to_move + 1):
            base_strings = [f"move_to_read_{number_of_steps_to_move}_steps_step_number_{steps_taken}_blank_symbols_read_{blank_symbols_read}"]
            if steps_taken > 0:
                # steps taken 0 is only needed for the extra step to the right the routine needs to take after each loop
                base_strings += [f"move_to_write_{number_of_steps_to_move}_steps_step_number_{steps_taken + 1}_after_heaving_read_symbol_{symbol}_total_blank_symbols_read_{blank_symbols_read}" for symbol in tape_symbols]
            for base_string in base_strings:
                new_state = find_new_unique_string(previous_symbols=machine["states"], string_base=base_string)
                machine["states"].add(new_state)
                state_dict[base_string] = new_state

    # create the into into the subroutine
    # the start state needs to transition into the subroutine internal states
    non_blank_symbols = tape_symbols - {machine["blank_symbol"]}  # It is assumed, that this subroutine is only called on non-blank symbols
    for symbol in non_blank_symbols:
        state_to = state_dict[f"move_to_read_{number_of_steps_to_move}_steps_step_number_1_blank_symbols_read_0"]
        machine["transitions"].add(((start_state, symbol), (state_to, symbol, to_read_direction)))

    # create the internal "go to forth n steps" transitions
    for symbol in tape_symbols:
        for steps_right in range(number_of_steps_to_move):
            for blank_symbols_read in range(number_of_steps_to_move - 1):
                state_from = state_dict[f"move_to_read_{number_of_steps_to_move}_steps_step_number_{steps_right + 1}_blank_symbols_read_{blank_symbols_read}"]
                if steps_right + 2 <= number_of_steps_to_move:
                    state_to = state_dict[f"move_to_read_{number_of_steps_to_move}_steps_step_number_{steps_right + 2}_blank_symbols_read_{blank_symbols_read}"]
                    machine["transitions"].add(((state_from, symbol), (state_to, symbol, to_read_direction)))
                else:
                    if symbol == blank:
                        blank_symbols_read += 1
                    state_to = state_dict[f"move_to_write_{number_of_steps_to_move}_steps_step_number_1_after_heaving_read_symbol_{symbol}_total_blank_symbols_read_{blank_symbols_read}"]
                    machine["transitions"].add(((state_from, symbol), (state_to, symbol, to_write_direction)))

    # create the internal "go back n steps then write" transitions
    for symbol in tape_symbols:
        for state_symbol in tape_symbols:
            for steps_left in range(number_of_steps_to_move):
                for blank_symbols_read in range(number_of_steps_to_move):
                    state_from = f"move_to_write_{number_of_steps_to_move}_steps_step_number_{steps_left + 1}_after_heaving_read_symbol_{state_symbol}_total_blank_symbols_read_{blank_symbols_read}"
                    if steps_left + 2 <= number_of_steps_to_move:
                        state_to = f"move_to_write_{number_of_steps_to_move}_steps_step_number_{steps_left + 2}_after_heaving_read_symbol_{state_symbol}_total_blank_symbols_read_{blank_symbols_read}"
                        machine["transitions"].add(((state_from, symbol), (state_to, symbol, to_write_direction)))
                    else:
                        if blank_symbols_read < number_of_steps_to_move:
                            state_to = f"move_to_read_{number_of_steps_to_move}_steps_step_number_0_blank_symbols_read_{blank_symbols_read}"
                        else:
                            state_to = stop_state
                        machine["transitions"].add(((state_from, symbol), (state_to, state_symbol, to_read_direction)))

    return machine


@__check_state_inclusion
@call_by_value
def add_insert_specific_symbols_subroutine(machine: dict, start_state: str, stop_state: str, symbols_to_insert: tuple) -> dict:
    """

    :param machine:
    :param start_state:
    :param stop_state:
    :param symbols_to_insert:
    :return:
    """
    tape_symbols = machine["alphabet"] | machine["control_symbols"]
    blank = machine["blank_symbol"]

    marking_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"], string_base="marked_first_symbol")
    machine["states"].add(marking_state)

    machine = add_insert_specific_symbol_between_subroutine(machine, start_state=start_state, stop_state=marking_state, symbol_to_insert=blank)

    second_symbol_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"], string_base="move_to_second_symbol")
    machine["states"].add(marking_state)

    machine = add_move_to_matching_symbol_subroutine(machine, start_state=marking_state, stop_state=second_symbol_state,
                                                     matching_symbols={blank}, direction="L")

    move_to_symbol_state = second_symbol_state
    for i in range(len(symbols_to_insert))[1:]:
        write_symbol_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"],
                                           string_base=f"write_symbol_no{i + 1}_")
        machine["states"].add(write_symbol_state)
        machine = add_move_n_steps_subroutine(machine, start_state=move_to_symbol_state, stop_state=write_symbol_state,
                                              steps=i, direction="R")

        goto_start_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"],
                                           string_base=f"move_to_marked_start_no{i + 1}_")
        machine["states"].add(goto_start_state)
        machine = add_insert_specific_symbol_between_subroutine(machine, start_state = write_symbol_state, stop_state= goto_start_state, symbol_to_insert= symbols_to_insert[i])

        move_to_symbol_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"],
                                           string_base=f"move_to_symbol_no{i + 1}_")
        machine["states"].add(move_to_symbol_state)
        machine = add_move_to_matching_symbol_subroutine(machine, start_state=goto_start_state, stop_state=move_to_symbol_state,
                                                         matching_symbols={blank}, direction="L")

    machine = add_insert_specific_symbol_between_subroutine(machine, start_state=move_to_symbol_state, stop_state=stop_state, symbol_to_insert=symbols_to_insert[0])
    return machine


@__check_state_inclusion
@call_by_value
def add_insert_specific_symbol_between_subroutine(machine: dict, start_state: str, stop_state: str, symbol_to_insert: str) -> dict:
    """

    :param machine:
    :param start_state:
    :param stop_state:
    :param symbol_to_insert:
    :return:
    """

    tape_symbols = machine["alphabet"] | machine["control_symbols"]
    blank = machine["blank_symbol"]
    non_blank_symbols = tape_symbols - {blank}

    # create new states

    # We dont know how the states will be named, only what the base string is
    # so we keep track of the actual states by storing them in a dict with their
    # base key string as key
    state_dict = {}

    for symbol in tape_symbols:
        base_string = f"insert_symbol_{symbol}"
        new_state = find_new_unique_string(previous_symbols = machine["states"] | tape_symbols, base_string = base_string)
        state_dict[base_string] = new_state
        machine["states"].add(new_state)

    for symbol in non_blank_symbols:
        machine["transitions"].add(((start_state, symbol), (state_dict[f"insert_symbol_{symbol}"], symbol_to_insert, "R")))

    machine["transitions"].add(((start_state, blank), (stop_state, symbol_to_insert, "R")))

    for saved_symbol in non_blank_symbols:
        for symbol in non_blank_symbols:
            machine["transitions"].add(((state_dict[f"insert_symbol_{saved_symbol}"], symbol), (state_dict[f"insert_symbol_{symbol}"], saved_symbol, "R")))

        machine["transitions"].add(((state_dict[f"insert_symbol_{saved_symbol}"], blank), (stop_state, saved_symbol, "R")))

    return machine


@__check_state_inclusion
@call_by_value
def add_move_n_steps_subroutine(machine: dict, start_state: str, stop_state: str, steps: int, direction: str) -> dir:
    """

    :param machine:
    :param direction:
    :param start_state:
    :param stop_state:
    :return:
    """

    tape_symbols = machine["alphabet"] | machine["control_symbols"]

    # create new states

    # We dont know how the states will be named, only what the base string is
    # so we keep track of the actual states by storing them in a dict with their
    # base key string as key
    state_dict = {}

    if direction not in ["L", "R"]:
        raise ValueError(f"direction must be L or R; {direction} given")

    direction_string = "right" if direction == "R" else "left"
    for step in range(steps - 1):
        base_string = f"take_{steps}_steps_{direction_string}_number_{step + 2}"
        new_state = find_new_unique_string(previous_symbols = machine["states"] | tape_symbols, base_string = base_string)
        state_dict[base_string] = new_state
        machine["states"].add(new_state)

    state_sequence = [start_state] + [ state_dict[f"take_{steps}_steps_{direction_string}_number_{step}"] for i in range(steps)] + [stop_state]

    for symbol in tape_symbols:
        for state_index in range(len(state_sequence)):
            transition = ((state_sequence[state_index], symbol), (state_sequence[state_index + 1], symbol, direction))
            machine["transitions"].add(transition)

    return machine


@__check_state_inclusion
@call_by_value
def add_confirm_read_string(machine: dict, start_state: str, stop_state: str, to_confirm: tuple) -> dict:
    """Add subroutine which reads the `to_confirm` tuple of symbols or halts in a rejecting state

    It returns the head back to the previous position after confirming that the next symbols are the given ones

    :param machine:
    :param to_confirm:
    :param start_state:
    :param stop_state:
    :return:
    """

    last_state = start_state
    tape_symbols = machine["alphabet"] | machine["control_symbols"]
    for i, symbol in enumerate(to_confirm):
        new_state = find_new_unique_string(previous_symbols=tape_symbols | machine["sates"], string_base=f"confirmed_{symbol}")
        machine["states"].add(new_state)
        machine["transitions"].add(((last_state, symbol), (new_state, symbol, "R")))
        last_state = new_state

    return add_move_n_steps_subroutine(machine=machine, start_state=last_state, stop_state=stop_state,
                                       steps=len(to_confirm), direction="L")


@__check_state_inclusion
@call_by_value
def add_replace_string_subroutine(machine: dict, start_state: str, stop_state: str, to_replace: tuple, to_write) -> dict:
    """



    :param machine:
    :param to_replace:
    :param to_write:
    :param start_state:
    :param stop_state:
    :return:
    """

    tape_symbols = machine["alphabet"] | machine["control_symbols"]
    writing_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"], string_base="start_writing")
    machine["states"].add(writing_state)
    deleting_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"], string_base="start_deleting")
    machine["states"].add(deleting_state)

    machine = add_confirm_read_string(machine=machine, start_state=start_state, stop_state=deleting_state,
                                      to_confirm=to_replace)
    machine = add_delete_next_n_symbols_subroutine(machine, number_of_steps_to_move=len(to_replace), start_state=deleting_state, stop_state=writing_state)
    machine = add_insert_specific_symbols_subroutine(machine, symbols_to_insert=to_write, start_state=writing_state, stop_state=stop_state)
    return machine


@__check_state_inclusion
@call_by_value
def add_move_to_random_place_subroutine(machine: dict, start_state: str, stop_state: str) -> dict:
    """

    :param machine:
    :param start_state:
    :param stop_state:
    :return:
    """

    tape_symbols = machine["alphabet"] | machine["control_symbols"]
    non_blank_symbols = tape_symbols - {machine["blank_symbol"]}
    first_symbol_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"], string_base="go_a_step_to_the_right")
    random_state = find_new_unique_string(previous_symbols=tape_symbols | machine["states"], string_base="go_a_random_number_of_steps")
    machine = add_move_to_matching_symbol_subroutine(machine=machine, start_state=start_state, stop_state=first_symbol_state, matching_symbols={machine["blank_symbol"]}, direction="L")
    machine = add_move_n_steps_subroutine(machine=machine, start_state=first_symbol_state, stop_state=random_state, steps=1, direction="R")
    for symbol in non_blank_symbols:
        machine["transitions"].add(((random_state, symbol), (random_state, symbol, "R")))
        machine["transitions"].add(((random_state, symbol), (stop_state, symbol, "S")))
    return machine
