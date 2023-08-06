import json
from typing import Any
import requests
from requests.exceptions import ConnectionError  # pylint:disable=redefined-builtin
from autoreduce_db.reduction_viewer.models import Instrument
from autoreduce_utils.settings import AUTOREDUCE_API_URL
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import FormView
from django.shortcuts import render

from autoreduce_frontend.utilities import input_processing
from autoreduce_frontend.reduction_viewer.views.common import (UNAUTHORIZED_MESSAGE, prepare_arguments_for_render,
                                                               make_reduction_arguments)

UNKNOWN_ERROR_MESSAGE = "Unknown error encountered"
RUN_EMPTY_MESSAGE = "Run field was invalid or empty"
UNABLE_TO_CONNECT_MESSAGE = "Unable to connect to the Autoreduce job submission service. If the error "\
                            "persists please let the Autoreduce team know at ISISREDUCE@stfc.ac.uk"

PARSING_ERROR_MESSAGE = "Encountered error: {} while parsing: '{}'"


class BatchRunSubmit(FormView):
    template_name = 'batch_run.html'

    def get_context_data(self, **kwargs):
        context = {}
        instrument = Instrument.objects.prefetch_related('reduction_runs').get(name=kwargs.get('instrument'))

        # pylint:disable=no-member
        runs_for_instrument = instrument.reduction_runs.filter(batch_run=True)
        last_run = instrument.get_last_for_rerun(runs_for_instrument)

        standard_vars, advanced_vars, variable_help = prepare_arguments_for_render(last_run.arguments,
                                                                                   last_run.instrument.name)
        context['message'] = self.request.GET.get("error", None)
        context['instrument'] = instrument
        context['standard_variables'] = standard_vars
        context['advanced_variables'] = advanced_vars
        context['variable_help'] = variable_help
        return context

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def render_error(self, request, message: str, runs, **kwargs):
        """Render the GET page but with an additional error message"""
        context = self.get_context_data(**kwargs)
        context["error"] = message
        context["runs"] = runs
        return render(request, self.template_name, context)

    def render_confirm(self, request, instrument: str, runs, kwargs):
        """Render the GET page but with an additional error message"""
        context = self.get_context_data(**kwargs)
        context["runs"] = runs
        context["instrument_name"] = instrument
        return render(request, "batch_run_confirmation.html", context)

    # pylint:disable=too-many-return-statements
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        instrument_name = kwargs["instrument"]

        input_runs = request.POST.get("runs", None)
        if not input_runs:
            return self.render_error(request, RUN_EMPTY_MESSAGE, input_runs, **kwargs)

        try:
            auth_token = str(request.user.auth_token)
        except AttributeError as err:  # pylint:disable=unused-variable
            return self.render_error(request, UNAUTHORIZED_MESSAGE, input_runs, **kwargs)
        runs = input_processing.parse_user_run_numbers(input_runs)
        args_for_range = make_reduction_arguments(request.POST.items(), instrument_name)

        try:
            response = requests.post(f"{AUTOREDUCE_API_URL}/runs/batch/{kwargs['instrument']}",
                                     json={
                                         "runs": runs,
                                         "reduction_arguments": args_for_range,
                                         "user_id": request.user.id,
                                         "description": request.POST.get("run_description", "")
                                     },
                                     headers={"Authorization": f"Token {auth_token}"})
        except ConnectionError as err:
            return self.render_error(request, UNABLE_TO_CONNECT_MESSAGE, input_runs, **kwargs)
        except Exception as err:  # pylint:disable=broad-except
            return self.render_error(request, str(err), input_runs, **kwargs)

        try:
            if response.status_code != 200:
                content = json.loads(response.content)
                return self.render_error(request, content.get("message", UNKNOWN_ERROR_MESSAGE), input_runs, **kwargs)
        except Exception as err:  # pylint:disable=broad-except
            return self.render_error(request, PARSING_ERROR_MESSAGE.format(err, response.content), input_runs, **kwargs)
        return self.render_confirm(request, instrument_name, runs, kwargs)
