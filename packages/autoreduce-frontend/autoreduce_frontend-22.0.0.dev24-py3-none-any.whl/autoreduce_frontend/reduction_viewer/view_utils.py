# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Utility functions for the view of django models."""
# pylint:disable=no-member
import functools
import logging
import os
from typing import Dict, Tuple

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import url_has_allowed_host_and_scheme
from autoreduce_db.reduction_viewer.models import Instrument, ReductionRun
from autoreduce_qp.queue_processor.reduction.service import ReductionScript
from autoreduce_frontend.autoreduce_webapp.settings import DATA_ANALYSIS_BASE_URL
from autoreduce_frontend.autoreduce_webapp.settings import (ALLOWED_HOSTS, UOWS_LOGIN_URL)
from autoreduce_frontend.autoreduce_webapp.templatetags.colour_table_row import colour_table_row

LOGGER = logging.getLogger(__package__)


def deactivate_invalid_instruments(func):
    """Deactivate instruments if they are invalid."""

    @functools.wraps(func)
    def request_processor(request, *args, **kws):
        """
        Function decorator that checks the reduction script for all active
        instruments and deactivates any that cannot be found.

        Active: instruments that have a script file, or have previous runs
        with a stored script.
        """
        instruments = Instrument.objects.all()
        for instrument in instruments:
            script_path = ReductionScript(instrument.name)
            instrument.is_active = False
            if script_path.exists() or len(ReductionRun.objects.filter(instrument=instrument)) > 0:
                instrument.is_active = True
            instrument.save(update_fields=['is_active'])

        return func(request, *args, **kws)

    return request_processor


def get_interactive_plot_data(plot_locations):
    """Get the data for the interactive plots from the saved JSON files."""
    json_files = [location for location in plot_locations if location.endswith(".json")]

    output = {}
    for filepath in json_files:
        name = os.path.basename(filepath)
        with open(filepath, mode='r', encoding='utf-8') as file:
            data = file.read()
        output[name] = data

    return output


def make_data_analysis_url(reduction_location: str) -> str:
    """
    Makes a URL for the data.analysis website that will open the location of the
    data.
    """
    if "/instrument/" in reduction_location:
        return DATA_ANALYSIS_BASE_URL + reduction_location.split("/instrument/")[1]
    return ""


def windows_to_linux_path(path: str) -> str:
    """Convert Windows path to Linux path."""
    # '\\isis\inst$\' maps to '/isis/'
    path = path.replace(r'\\isis\inst$' + '\\', '/isis/')
    path = path.replace('\\', '/')
    return path


def linux_to_windows_path(path: str) -> str:
    """Convert Linux path to Windows path."""
    # '\\isis\inst$\' maps to '/isis/'
    path = path.replace('/isis/', r'\\isis\inst$' + '\\')
    path = path.replace('/', '\\')
    return path


def started_by_id_to_name(started_by_id=None):
    """
    Return the name of the user or team that submitted an autoreduction run.

    Args:
        started_by_id: The ID of the user who started the run, or a control code
        if not started by a user.

    Returns:
        If started by a valid user, return '[forename] [surname]'.

        If started automatically, return 'Autoreducton service'.

        If started manually, return 'Development team'.

        Otherwise, return None.
    """
    if started_by_id is None or started_by_id < -1:
        return None

    if started_by_id == -1:
        return "Development team"

    if started_by_id == 0:
        return "Autoreduction service"

    try:
        user = get_user_model()
        user_record = user.objects.get(id=started_by_id)
        return f"{user_record.first_name} {user_record.last_name}"
    except ObjectDoesNotExist as exception:
        LOGGER.error(exception)
        return None


def make_return_url(request, next_url):
    """
    Make the return URL based on whether a next_url is present in the url. If
    there is a next_url, verify that the url is safe and allowed before using
    it. If not, default to the host.
    """
    if next_url:
        if url_has_allowed_host_and_scheme(next_url, ALLOWED_HOSTS, require_https=True):
            return UOWS_LOGIN_URL + request.build_absolute_uri(next_url)
        else:
            # The next_url was not safe so don't use it - build from
            # request.path to ignore GET parameters
            return UOWS_LOGIN_URL + request.build_absolute_uri(request.path)
    else:
        return UOWS_LOGIN_URL + request.build_absolute_uri()


def order_runs(sort_by: str, runs: ReductionRun.objects):
    """
    Sort a queryset of runs based on the passed GET sort_by param
    """
    if sort_by == "-run_number":
        runs = runs.order_by('-run_numbers__run_number', '-run_version')
    elif sort_by == "run_number":
        runs = runs.order_by('run_numbers__run_number', 'run_version')
    elif sort_by == "-created":
        runs = runs.order_by('-created')
    elif sort_by == "created":
        runs = runs.order_by('created')
    else:
        runs = runs.order_by('-run_numbers__run_number', 'run_version')

    return runs


# pylint:disable=no-method-argument
def data_status(status):
    """Function to add text-(status) class to status column for formatting

        Returns:
        "text- " concatonated with status fetched from record for formatting with colour_table_row

        """
    return "text-" + colour_table_row(status) + " run-status"


def get_navigation_runs(instrument_name: str, run: ReductionRun, page_type: str) -> Tuple[ReductionRun]:
    """
    Return a tuple of runs that will be used for navigation in the view.

    Args:
        instrument_name: The name of the instrument.
        run: The run that is currently being viewed.
        page_type: The type of page that is being viewed.
    """

    runs = ReductionRun.objects.filter(instrument__name=instrument_name, batch_run=run.batch_run)
    runs = order_runs(sort_by=page_type, runs=runs)

    if not run.batch_run:
        next_run = runs.filter(run_numbers__run_number__gt=run.run_number).last()
        previous_run = runs.filter(run_numbers__run_number__lt=run.run_number).first()
    else:
        next_run = runs.filter(pk__gt=run.pk).last()
        previous_run = runs.filter(pk__lt=run.pk).first()

    if next_run is None:
        next_run = run

    if previous_run is None:
        previous_run = run

    newest_run = runs.first()
    oldest_run = runs.last()

    return next_run, previous_run, newest_run, oldest_run


def convert_software_string_to_dict(software_str: str) -> Dict[str, str]:
    """
    Convert the software string to a dictionary.
    """
    software_name = software_str.split('-')[0]
    software_version = software_str.split('-')[1]
    software_dict = {'name': software_name, 'version': software_version}
    return software_dict
