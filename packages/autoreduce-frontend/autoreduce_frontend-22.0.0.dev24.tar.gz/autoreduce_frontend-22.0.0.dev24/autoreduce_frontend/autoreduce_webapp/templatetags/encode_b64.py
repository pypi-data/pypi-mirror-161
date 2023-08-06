# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Asserts the variable type of tables
"""

import base64
from django.template import Library

# pylint:disable=invalid-name
register = Library()


@register.simple_tag
def encode_b64(value):
    """
    Encodes the name in a urlsafe base64 representaiton.
    Used to encode variable names with any character without
    special handling for having whitespaces or special characters.
    """
    # pylint:disable=no-member
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("utf-8")
