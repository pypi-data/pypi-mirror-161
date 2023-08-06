import json
import logging

from autoreduce_db.reduction_viewer.models import (Instrument, ReductionArguments, ReductionRun, Status)
from django.shortcuts import redirect

from autoreduce_frontend.autoreduce_webapp.view_utils import (check_permissions, login_and_uows_valid, render_with)
from autoreduce_frontend.reduction_viewer.views.common import prepare_arguments_for_render, make_reduction_arguments

LOGGER = logging.getLogger(__package__)

# pylint:disable=no-member


@login_and_uows_valid
@check_permissions
@render_with('configure_new_runs.html')
def configure_new_runs(request, instrument=None, start=0, experiment_reference=0):
    """
    Handles request to view instrument variables
    """
    instrument_name = instrument

    if request.method == 'POST':
        return configure_new_runs_post(request, instrument_name)
    else:
        return configure_new_runs_get(instrument, start, experiment_reference)


def configure_new_runs_post(request, instrument_name):
    """
    Submission to modify variables. Acts on POST request.

    Depending on the parameters it either makes them for a run range (when start is given, end is optional)
    or for experiment reference (when experiment_reference is given).
    """
    start = int(request.POST.get("run_start")) if request.POST.get("run_start", None) else None
    experiment_reference = int(request.POST.get("experiment_reference_number")) if request.POST.get(
        "experiment_reference_number", None) else None

    if not start and not experiment_reference:
        return {"message": "Invalid run range or experiment reference submitted."}

    instrument = Instrument.objects.get(name=instrument_name)

    args_for_range = make_reduction_arguments(request.POST.items(), instrument_name)
    arguments_json = json.dumps(args_for_range, separators=(',', ':'))

    def update_or_create(instrument, arguments_json, kwargs):
        try:
            args = ReductionArguments.objects.get(instrument=instrument, **kwargs)
            args.raw = arguments_json
            args.save()
        except ReductionArguments.DoesNotExist:
            ReductionArguments.objects.create(instrument=instrument, raw=arguments_json, **kwargs)

    if start:
        update_or_create(instrument, arguments_json, {'start_run': start})
    else:
        update_or_create(instrument, arguments_json, {'experiment_reference': experiment_reference})
    return redirect('runs:variables_summary', instrument=instrument_name)


# pylint:disable=too-many-locals
def configure_new_runs_get(instrument_name, start=0, experiment_reference=0):
    """
    GET for the configure new runs page
    """
    instrument = Instrument.objects.get(name__iexact=instrument_name)

    editing = (start > 0 or experiment_reference > 0)

    existing_arguments = None
    last_run = instrument.get_last_for_rerun(instrument.reduction_runs.filter(batch_run=False))
    run_start = start if start else last_run.run_number + 1

    if experiment_reference:
        try:
            existing_arguments = instrument.arguments.get(experiment_reference=experiment_reference)
        except ReductionArguments.DoesNotExist:
            pass
    elif start:
        try:
            existing_arguments = instrument.arguments.get(start_run=start)
        except ReductionArguments.DoesNotExist:
            pass

    if existing_arguments:
        standard_vars, advanced_vars, variable_help = prepare_arguments_for_render(existing_arguments,
                                                                                   last_run.instrument.name)
    else:
        # load the arguments from the latest rerun
        standard_vars, advanced_vars, variable_help = prepare_arguments_for_render(last_run.arguments,
                                                                                   last_run.instrument.name)

    context_dictionary = {
        'instrument': instrument,
        'last_instrument_run': last_run,
        'processing': ReductionRun.objects.filter(instrument=instrument, status=Status.get_processing()),
        'queued': ReductionRun.objects.filter(instrument=instrument, status=Status.get_queued()),
        'standard_variables': standard_vars,
        'advanced_variables': advanced_vars,
        'variable_help': variable_help,
        'run_start': run_start,
        # used to determine whether the current form is for an experiment reference
        'current_experiment_reference': experiment_reference,
        # used to create the link to an experiment reference form, using this number
        'submit_for_experiment_reference': last_run.experiment.reference_number,
        'minimum_run_start': run_start,
        'minimum_run_end': run_start + 1,
        'upcoming_run_variables': "",
        'editing': editing,
        'tracks_script': '',
    }

    return context_dictionary
