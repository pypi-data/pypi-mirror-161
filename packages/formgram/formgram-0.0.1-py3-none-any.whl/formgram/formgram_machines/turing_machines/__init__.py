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



"""
A Turing machine is in this module assumed to be a dictionary with following keys

#. states:
    Is a set of strings for the internal states of the machine
#. alphabet:
    Is a set of strings which can be on the tape
#. control_symbols:
    Is a set of strings which can also be on the tape. Especially the `blank` symbol
#. initial_state:
    Is an element of `states` which is the state of a freshly started machine
#. accepting_states:
    Is a subset of `states` which decides if a halting machine accepts
#. blank_symbol:
    Is an element of control_symbols which symbolizes an unwritten cell on tape
#. transitions:
    Is a set of tuples which the machine uses to operate. Each of the entries
    is of the form ``(current_state, read_symbol), (next_state, write_symbol, head_move_direction)``


A configuration of a Turing machine is a Tuple ``(machine_state, head_position, tape)``
here

#. machine_state:
    Is an element of the states set of the corresponding machine
#. head_position:
    Is the index which shows where the read/write-head of the corresponding machine is in relation to the tape
#. tape:
    Is a Tuple of symbols from the alphabet and control_symbols set of the corresponding machine

"""