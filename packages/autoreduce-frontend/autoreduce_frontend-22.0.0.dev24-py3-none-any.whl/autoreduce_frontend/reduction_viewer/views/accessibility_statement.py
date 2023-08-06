# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

import logging
from autoreduce_frontend.autoreduce_webapp.view_utils import render_with

LOGGER = logging.getLogger(__package__)


@render_with('accessibility_statement.html')
# pylint:disable=redefined-builtin
def accessibility_statement(_):
    """
    Render accessibility statement page.

    Note:
        _ is replacing the passed in request parameter.
    """
    return {}
