# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Utility functions for the Django views."""
# pylint:disable=no-member
import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render
import httpagentparser

from autoreduce_db.reduction_viewer.models import Notification
from autoreduce_db.reduction_viewer.models import ReductionRun, Experiment
from autoreduce_frontend.autoreduce_webapp.views import render_error
from autoreduce_frontend.autoreduce_webapp.icat_cache import ICATCache, ICATConnectionException
# Below import is a template on the repository
from autoreduce_frontend.autoreduce_webapp.settings import (DEVELOPMENT_MODE, LOGIN_URL, OUTDATED_BROWSERS,
                                                            UOWS_LOGIN_URL, USER_ACCESS_CHECKS)

LOGGER = logging.getLogger(__package__)


def has_valid_login(request):
    """
    Check that the user is correctly logged in and their session is still
    considered valid.
    """
    LOGGER.debug("Checking if user is authenticated")
    if DEVELOPMENT_MODE:
        LOGGER.debug("DEVELOPMENT_MODE True so allowing access")
        return True
    if request.user.is_authenticated and 'sessionid' in request.session:
        LOGGER.debug("User is authenticated and has a sessionid from the UOWS")
        return True

    return False


def handle_redirect(request):
    """Redirect the user to either capture the session id or to go and log in."""
    if request.GET.get('sessionid'):
        return redirect(
            request.build_absolute_uri(LOGIN_URL) + "?next=" +
            request.build_absolute_uri().replace('?sessionid=', '&sessionid='))

    return redirect(UOWS_LOGIN_URL + request.build_absolute_uri())


def login_and_uows_valid(func):
    """Function decorator to check whether the user's session is still valid."""

    def request_processor(request, *args, **kws):
        if has_valid_login(request):
            return func(request, *args, **kws)

        return handle_redirect(request)

    return request_processor


def require_staff(function_name):
    """Function decorator to check whether the user is a staff memeber."""

    def request_processor(request, *args, **kws):
        if has_valid_login(request):
            if request.user.is_staff:
                return function_name(request, *args, **kws)
            else:
                raise PermissionDenied()
        else:
            return handle_redirect(request)

    return request_processor


def require_admin(func):
    """Function decorator to check whether the user is a superuser."""

    def request_processor(request, *args, **kws):
        if has_valid_login(request):
            if request.user.is_superuser:
                return func(request, *args, **kws)
            else:
                raise PermissionDenied()
        else:
            return handle_redirect(request)

    return request_processor


def get_notifications(request):
    """Gets the notifications that the user should be able to see."""
    if request.user.is_staff and request.user.is_authenticated:
        return Notification.objects.filter(is_active=True)
    else:
        return Notification.objects.filter(is_active=True, is_staff_only=False)


def render_with(template):
    """
    Decorator for Django views that sends returned dict to render function
    with given template and RequestContext as context instance.
    """

    def renderer(function_name):

        def populate_template_dict(request, output):
            if 'request' not in output:
                output['request'] = request

            notifications = get_notifications(request)

            if 'notifications' not in output:
                output['notifications'] = notifications
            else:
                output['notifications'].extend(notifications)

            if 'bad_browsers' not in output:
                # Load in the list of not accepted browsers from the settings
                bad_browsers = []
                for browser, version in OUTDATED_BROWSERS.items():
                    bad_browsers.append((browser, version))

                # Get the family and version from the user_agent
                data = httpagentparser.detect(request.META.get('HTTP_USER_AGENT', ''))
                family = data["browser"]["name"]
                version = data["browser"]["version"]

                # Make sure we are only comparing against a single integer
                if '.' in version:
                    version = int(version[0:(version.index('.'))])
                else:
                    version = int(version)

                # Check whether the browser is outdated
                outdated = False
                for browser in bad_browsers:
                    if browser[0] == family and version <= browser[1]:
                        outdated = True

                # Change to more user-friendly language
                if family == "IE":
                    family = "Microsoft Internet Explorer"

                output['bad_browsers'] = bad_browsers
                output['current_browser'] = family
                output['version'] = version
                output['outdated'] = outdated

            return output

        def wrapper(request, *args, **kw):
            output = function_name(request, *args, **kw)
            if isinstance(output, dict):
                output = populate_template_dict(request, output)
                return render(request, template, output)
            return output

        return wrapper

    return renderer


def check_permissions(func):
    """
    Check that the user has permission to access the given experiment and/or
    instrument. Queries ICATCache to check owned instruments and experiments.
    """

    def request_processor(request, *args, **kwargs):
        if USER_ACCESS_CHECKS and not request.user.is_superuser:
            # Get the things to check by from the arguments supplied.
            experiment_reference = None
            owned_instrument_name = None
            viewed_instrument_name = None
            optional_instrument_names = set()
            if "run_number" in kwargs:
                # Get the experiment and instrument from the given run number
                run = ReductionRun.objects.filter(run_number=int(kwargs["run_number"])).first()
                experiment_reference = run.experiment.reference_number
                viewed_instrument_name = run.instrument.name
            else:
                # Get the experiment reference if it's supplied
                if "reference_number" in kwargs:
                    experiment_reference = int(kwargs["reference_number"])
                    # Find the associated instrument
                    experiment_obj = Experiment.objects.filter(reference_number=experiment_reference).first()
                    if experiment_obj:
                        optional_instrument_names = {run.instrument.name for run in experiment_obj.reduction_runs.all()}
                else:
                    # Look for an instrument name under 'instrument_name', or,
                    # failing that, 'instrument'
                    owned_instrument_name = kwargs.get("instrument_name", kwargs.get("instrument"))

            try:
                check_icat_permissions(request, experiment_reference, owned_instrument_name, viewed_instrument_name,
                                       optional_instrument_names)
            except ICATConnectionException as excep:
                return render_error(request, str(excep))

        # If we're here, the access checks have passed
        return func(request, *args, **kwargs)

    return request_processor


def check_icat_permissions(request: HttpRequest,
                           experiment_reference: int,
                           owned_instrument_name: str = None,
                           viewed_instrument_name: str = None,
                           optional_instrument_names: set = None):
    """
    Check ICAT instrument and experiment permissions from request.

    Args:
        request: The sent HTTP request.

        experiment_reference: The experiment reference number.

        owned_instrument_name: The name of the instrument found from the
        experiment reference number.

        viewed_instrument_name: The name of the instrument found from the run
        number.

        param optional_instrument_names: A set of instrument names found from
        the experiment.
    """
    with ICATCache(AUTH='uows', SESSION={'sessionid': request.session['sessionid']}) as icat:
        owned_instrument_list = icat.get_owned_instruments(int(request.user.username))
        valid_instrument_list = icat.get_valid_instruments(int(request.user.username))

        # Check for access to the instrument
        if owned_instrument_name or viewed_instrument_name:
            optional_instrument_names.add(
                owned_instrument_name if owned_instrument_name is not None else viewed_instrument_name)

            # Check access to an owned instrument
            if owned_instrument_name is not None \
                    and owned_instrument_name not in owned_instrument_list:
                raise PermissionDenied()  # No access allowed

            # Check access to a valid instrument (able to view some runs etc.)
            if viewed_instrument_name is not None \
                    and viewed_instrument_name not in \
                    owned_instrument_list + valid_instrument_list:
                raise PermissionDenied()  # No access allowed

        # Check for access to the experiment; if the user owns one of the
        # associated instruments, we don't need to check this
        if optional_instrument_names and optional_instrument_names.intersection(owned_instrument_list):
            pass
        elif experiment_reference is not None and experiment_reference not in \
                icat.get_associated_experiments(int(request.user.username)):
            raise PermissionDenied()
