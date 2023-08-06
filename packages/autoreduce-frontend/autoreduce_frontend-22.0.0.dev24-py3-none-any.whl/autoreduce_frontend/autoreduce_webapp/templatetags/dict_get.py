# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Asserts the variable type of tables
"""

from django.template import Library

# pylint:disable=invalid-name
register = Library()


@register.simple_tag
def dict_get(dictionary: dict, variable_name: str):
    """Tag for retrieving the value for a key from a dictionary"""
    if dictionary:
        return dictionary.get(variable_name, "")
    else:
        return ""
