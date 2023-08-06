# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from autoreduce_db.reduction_viewer.models import Instrument
from django.http.response import JsonResponse

from autoreduce_frontend.autoreduce_webapp.view_utils import (check_permissions, login_and_uows_valid)


@login_and_uows_valid
@check_permissions
# pylint:disable=no-member
def instrument_pause(request, instrument=None):
    """
    Renders pausing of instrument returning a JSON response
    """
    instrument_obj = Instrument.objects.get(name=instrument)
    currently_paused = (request.POST.get("currently_paused").lower() == "false")
    instrument_obj.is_paused = currently_paused
    instrument_obj.save()
    return JsonResponse({'currently_paused': str(currently_paused)})  # Blank response
