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



"""This subpackage provides various modules to gain information about grammars

It features multiple modules:

#. :mod:`formgram_classes.classifers.chomsky_classifiers`
    Featuring functions of the format ``is_<X>`` and importantly :func:`get_chomsky_type`
#. :mod:`formgram_classes.classifers.form_classifiers`
    Featuring functions of the format ``has_<X>_form``

:example:

>>> from formgram.formgram_procedures.txt_interface import parse
>>> from formgram.formgram_procedures.classifiers.chomsky_classifiers import get_chomsky_type
>>> from formgram.formgram_procedures.classifiers.form_classifiers import has_chomsky_normal_form
>>> grammar_text = '''<S> ::= <S> <S> | "s"'''
>>> grammar_dict = parse(grammar_text)
>>> get_chomsky_type(grammar_dict)
<ChomskyType.CONTEXT_FREE: 2>
>>> has_chomsky_normal_form(grammar_dict)
True
"""
