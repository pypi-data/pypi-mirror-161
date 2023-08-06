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



"""This package holds modules providing functionality needed elsewhere

The code in them is needed by other subpackages, but deemed non-informative
for purposes of education on formal languages


Following are the modules:

#. decorators
    Provides decorator ``@call_by_value``, which copies each argument before passing it to the decorated function
#. input_validator
    Provides function ``validate_grammar_form`` which tests a given dict on fulfilment of grammar assumptions
#. production_grouping
    Provides functions to organize grammar productions into dictionaries
#. sequence_functions
    Provides functions to determine the common prefix or suffix of any arbitrary collection of sequences
#. set_functions
    Provides the function ``powerset`` which outputs the powerset of a given set
"""