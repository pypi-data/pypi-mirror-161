# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Handle page responses for the web app."""
# pylint: disable=unused-argument,bare-except,no-member
from django.http import HttpRequest
from django.shortcuts import render

from autoreduce_frontend.autoreduce_webapp.settings import EMAIL_ERROR_RECIPIENTS


def render_error(request: HttpRequest, message: str):
    """
    Return the error page with a message displayed.

    Args:
        request: The original sent request.

        message: The message that will be displayed.

    Return:
        The error page.
    """
    return render(request, 'error.html', {'message': message, 'admin_email': EMAIL_ERROR_RECIPIENTS[0]}, status=500)
