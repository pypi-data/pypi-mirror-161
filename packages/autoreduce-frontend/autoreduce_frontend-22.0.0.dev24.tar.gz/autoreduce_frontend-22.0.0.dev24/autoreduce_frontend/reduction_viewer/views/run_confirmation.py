# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

import json
import logging

import requests
from autoreduce_db.reduction_viewer.models import (ReductionRun, Status, Software)
from autoreduce_utils.settings import AUTOREDUCE_API_URL
from django.db.models.query import QuerySet
# without this import the exception does NOT get captured in the except ConnectionError
# even though it shadows a built-in, this import is necessary
from requests.exceptions import ConnectionError  # pylint:disable=redefined-builtin

from autoreduce_frontend.autoreduce_webapp.view_utils import (check_permissions, login_and_uows_valid, render_with)
from autoreduce_frontend.reduction_viewer.views.common import UNAUTHORIZED_MESSAGE, make_reduction_arguments
from autoreduce_frontend.utilities import input_processing

LOGGER = logging.getLogger(__package__)


# pylint:disable=too-many-return-statements,too-many-branches,too-many-statements,too-many-locals
@login_and_uows_valid
@check_permissions
@render_with('run_confirmation.html')
def run_confirmation(request, instrument: str):
    """
    Handles request for user to confirm re-run
    """
    range_string = request.POST.get('runs')
    run_description = request.POST.get('run_description')
    software = Software.objects.get(pk=request.POST.get('software'))
    script_choice = request.POST.get('script_choice')

    # pylint:disable=no-member
    queue_count = ReductionRun.objects.filter(instrument__name=instrument, status=Status.get_queued()).count()
    context_dictionary = {
        # list stores (run_number, run_version)
        'runs': [],
        'variables': None,
        'queued': queue_count,
        'instrument_name': instrument,
        'run_description': run_description
    }

    try:
        run_numbers = input_processing.parse_user_run_numbers(range_string)
    except SyntaxError as exception:
        context_dictionary['error'] = exception.msg
        return context_dictionary

    if not run_numbers:
        context_dictionary['error'] = f"Could not correctly parse range input {range_string}"
        return context_dictionary

    # Determine user level to set a maximum limit to the number of runs that can be re-queued
    if request.user.is_superuser:
        max_runs = 500
    elif request.user.is_staff:
        max_runs = 50
    else:
        max_runs = 20

    if len(run_numbers) > max_runs:
        context_dictionary["error"] = (f'{len(run_numbers)} runs were requested, '
                                       f'but only {max_runs} runs can be queued at a time')
        return context_dictionary

    related_runs: QuerySet[ReductionRun] = ReductionRun.objects.filter(
        instrument__name=instrument,
        batch_run=False,  # batch_runs are handled in BatchRunSubmit
        run_numbers__run_number__in=run_numbers)
    # Check that RB numbers are the same for the range entered
    # pylint:disable=no-member
    rb_number = related_runs.values_list('experiment__reference_number', flat=True).distinct()
    if len(rb_number) > 1:
        context_dictionary['error'] = 'Runs span multiple experiment numbers ' \
                                      '(' + ','.join(str(i) for i in rb_number) + ')' \
                                      ' please select a different range.'
        return context_dictionary

    try:
        new_script_arguments = make_reduction_arguments(request.POST.items(), instrument)
        context_dictionary['variables'] = new_script_arguments
    except ValueError as err:
        context_dictionary['error'] = err
        return context_dictionary

    try:
        auth_token = str(request.user.auth_token)
    except AttributeError as err:  # pylint:disable=unused-variable
        context_dictionary['error'] = UNAUTHORIZED_MESSAGE
        return context_dictionary
    # run_description gets stored in run_description in the ReductionRun object
    max_run_description_length = ReductionRun._meta.get_field('run_description').max_length
    if len(run_description) > max_run_description_length:
        context_dictionary["error"] = (f'The description contains {len(run_description)} characters, '
                                       f'a maximum of {max_run_description_length} are allowed')
        return context_dictionary
    for run_number in run_numbers:
        matching_previous_runs = related_runs.filter(run_numbers__run_number=run_number).order_by('-run_version')
        run_suitable, reason = find_reason_to_avoid_re_run(matching_previous_runs, run_number)
        if not run_suitable:
            context_dictionary['error'] = reason
            return context_dictionary

        most_recent_run: ReductionRun = matching_previous_runs.first()
        # list stores (run_number, run_version)
        context_dictionary["runs"].append((run_number, most_recent_run.run_version + 1))

    if script_choice == 'use_stored_reduction_script':
        stored_reduction_script = most_recent_run.script.text
    else:
        stored_reduction_script = None

    try:
        response = requests.post(f"{AUTOREDUCE_API_URL}/runs/{instrument}",
                                 json={
                                     "runs": run_numbers,
                                     "reduction_arguments": new_script_arguments,
                                     "user_id": request.user.id,
                                     "description": run_description,
                                     "software": {
                                         "name": software.name,
                                         "version": software.version
                                     },
                                     "reduction_script": stored_reduction_script,
                                 },
                                 headers={"Authorization": f"Token {auth_token}"})
    except ConnectionError as err:  # pylint:disable=broad-except
        context_dictionary['error'] = "Unable to connect to the Autoreduce job submission service. If the error "\
                    "persists please let the Autoreduce team know at ISISREDUCE@stfc.ac.uk"
        return context_dictionary

    except Exception as err:  # pylint:disable=broad-except
        context_dictionary['error'] = "Encountered unexpected error, "\
                f"please let the Autoreduce team know at ISISREDUCE@stfc.ac.uk: {err}"
        return context_dictionary

    try:
        if response.status_code != 200:
            content = json.loads(response.content)
            context_dictionary['error'] = content.get("message", "Unknown error encountered")
            return context_dictionary
    except Exception as err:  # pylint:disable=broad-except
        context_dictionary['error'] = f"Encountered unexpected error: {err} while parsing '{response.content}', "\
                f"please let the Autoreduce team know at ISISREDUCE@stfc.ac.uk: {err}"
        return context_dictionary
    return context_dictionary


def find_reason_to_avoid_re_run(matching_previous_runs, run_number):
    """
    Check whether the most recent run exists
    """
    most_recent_run = matching_previous_runs.first()

    # Check old run exists - if it doesn't exist there's nothing to re-run!
    if most_recent_run is None:
        return False, f"Run number {run_number} hasn't been ran by autoreduction yet."

    # Prevent multiple queueings of the same re-run
    queued_runs = matching_previous_runs.filter(status=Status.get_queued()).first()
    if queued_runs is not None:
        return False, f"Run number {queued_runs.run_number} is already queued to run"

    return True, ""
