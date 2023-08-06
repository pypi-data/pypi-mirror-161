"""This module provides functions to simulate Turing machines


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

from typing import Iterator


def simulate_single_step(machine: dict, configuration: tuple) -> Iterator[tuple]:
    """Generate all configurations reachable by applying exactly one transition

    :param machine:
    :param configuration:
    :return:
    """
    state, head_position, tape = configuration
    symbol = tape[head_position]

    matching_transitions = (transition for transition in machine["transitions"]
                            if (read_state := transition[0][0]) == state
                            and (read_symbol := transition[0][1]) == symbol)

    for transition in matching_transitions:

        (read_state, read_symbol), (write_state, write_symbol, head_move_direction) = transition
        new_state = write_state

        # Write write_symbol to tape
        new_tape = list(tape)
        new_tape[head_position] = write_symbol

        # Set next head_position based on head_move_direction
        new_head_position = head_position
        if head_move_direction == "R":
            new_head_position += 1
        elif head_move_direction == "L":
            new_head_position -= 1

        # If needed add new cell to make sure the head is still on the tape
        if new_head_position < 0:  # Walked of the left side of the tape
            new_tape = [machine["blank_symbol"]] + new_tape
            new_head_position += 1  # Start of tape changed, need to adjust index

        elif new_head_position >= len(tape):  # Walked of right side of the tape
            new_tape += [machine["blank_symbol"]]

        yield new_state, new_head_position, tuple(new_tape)


def run_full_simulation(machine: dict, input_tape: tuple, fuel: int = 100, raise_exception_on_empty_fuel: bool = True) -> bool:
    """Simulate given nondeterministic Turing machine depth first on input tape

    The simulation is done in recursive functions called in this function, with
    three base cases:

    #. The machine halts AND is in an accepting state:
        `True` is returned
    #. The machine halts not in an accepting state:
        `False` is returned
    #. The machine runs out of fuel:
        depending on `raise_exception_on_empty_fuel` either an exception is raised
        or `False` is returned.

    `True` returns bubble up as soon as they are encountered, otherwise the rest of the configuration tree needs to be
    considered.

    In case `raise_exception_on_empty_fuel` is set, the recursive function remembers if any exception was risen in
    deeper recursion levels and raises one itself if the tree has been exhausted without encountering an accepting
    halting configuration.

    :param machine:
    :param input_tape:
    :param fuel:
    :param raise_exception_on_empty_fuel: 
    :return:
    """
    configuration = (machine["initial_state"], 0, input_tape)
    if raise_exception_on_empty_fuel:
        return _simulation_recursion_tristate(machine, configuration, fuel)
    else:
        return _simulation_recursion(machine, configuration, fuel)


def _simulation_recursion(machine: dict, configuration: tuple, fuel: int) -> bool:
    """Semi-decide if Turing machine accepts starting on configuration in less then fuel steps

    :param machine:
    :param configuration:
    :param fuel:
    :return:
    """
    state, head_position, tape = configuration
    if not fuel:
        return False
    if not list(simulate_single_step(machine, configuration)):  # config is halting
        return state in machine["accepting_states"]
    return any(_simulation_recursion(machine, next_configuration, fuel - 1) for next_configuration in simulate_single_step(machine, configuration))


def _simulation_recursion_tristate(machine: dict, configuration: tuple, fuel: int) -> bool:
    """Semi-decide if Turing machine accepts starting on configuration in less then fuel steps

    Raise an exception if the configuration tree could not be exhausted due to fuel constraints

    :param machine:
    :param configuration:
    :param fuel:
    :return:
    """
    state, head_position, tape = configuration
    if fuel <= 0:
        raise TimeoutError("out of fuel")
    if not list(simulate_single_step(machine, configuration)):  # configuration is halting
        return state in machine["accepting_state"]

    encountered_a_timeout = False
    for next_configuration in simulate_single_step(machine, configuration):
        try:
            if _simulation_recursion(machine, next_configuration, fuel - 1):
                return True
        except TimeoutError:
            encountered_a_timeout = True
    if encountered_a_timeout:
        raise TimeoutError("out of fuel")
    return False
