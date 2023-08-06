import logging
from django.shortcuts import redirect
from django.urls import reverse
from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_qp.queue_processor.reduction.service import ReductionScript
from autoreduce_frontend.autoreduce_webapp.view_utils import (check_permissions, login_and_uows_valid, render_with)

from autoreduce_frontend.plotting.plot_handler import PlotHandler
from autoreduce_frontend.reduction_viewer.forms import RerunForm
from autoreduce_frontend.reduction_viewer.views.common import get_arguments_from_file, prepare_arguments_for_render
from autoreduce_frontend.reduction_viewer.view_utils import (get_interactive_plot_data, get_navigation_runs,
                                                             linux_to_windows_path, make_data_analysis_url,
                                                             windows_to_linux_path, started_by_id_to_name)

LOGGER = logging.getLogger(__package__)


def redirect_run_does_not_exist(instrument_name, run_number, run_version):
    """
    Redirects to the runs:list page if the run does not exist, and shows which run was not found.

    Args:
        instrument_name: The instrument name of the run.
        run_number: The run number of the run.
        run_version: The run version of the run.
    """
    return redirect(f'{reverse("runs:list", kwargs={"instrument": instrument_name})}'
                    f'?message=Run {run_number}-{run_version} does not exist. Redirected to the instrument page.')


# pylint:disable=no-member,too-many-locals,broad-except
@login_and_uows_valid
@check_permissions
@render_with('run_summary.html')
def run_summary(request, instrument_name=None, run_number=None, run_version=0):
    """Render run summary."""
    history = ReductionRun.objects.filter(instrument__name=instrument_name,
                                          batch_run=False,
                                          run_numbers__run_number=run_number).order_by('-run_version').select_related(
                                              'status').select_related('experiment').select_related('instrument')
    if len(history) == 0:
        return redirect_run_does_not_exist(instrument_name, run_number, run_version)

    return run_summary_run(request, history, instrument_name, run_version, run_number)


@login_and_uows_valid
@check_permissions
@render_with('run_summary.html')
# pylint:disable=no-member,too-many-locals,broad-except,invalid-name
def run_summary_batch_run(request, instrument_name=None, pk=None, run_version=0):
    """Gathers the context and renders a run's summary"""
    history = ReductionRun.objects.filter(instrument__name=instrument_name, pk=pk).order_by(
        '-run_version').select_related('status').select_related('experiment').select_related('instrument')
    if len(history) == 0:
        return redirect_run_does_not_exist(instrument_name, pk, run_version)

    return run_summary_run(request, history, instrument_name, run_version, pk)


def run_summary_run(request, history, instrument_name=None, run_version=0, run_number=0):
    """Gathers the context and renders a run's summary"""
    try:
        run = next(run for run in history if run.run_version == int(run_version))
    except StopIteration:
        return redirect_run_does_not_exist(instrument_name, run_number, run_version)

    started_by = started_by_id_to_name(run.started_by)

    # Run status value of "s" means the run is skipped
    is_skipped = run.status.value == "s"
    is_rerun = len(history) > 1

    location_list = run.reduction_location.all()
    reduction_location = ""
    if location_list:
        reduction_location = location_list[0].file_path
    if reduction_location and '\\' in reduction_location:
        reduction_location = reduction_location.replace('\\', '/')

    path_type = request.GET.get("path_type", "linux")  # defaults to Linux
    if path_type == "linux":
        data_location = "\n".join(
            [windows_to_linux_path(data_location.file_path) for data_location in run.data_location.all()])
    elif path_type == "windows":
        data_location = "\n".join(
            [linux_to_windows_path(data_location.file_path) for data_location in run.data_location.all()])

    data_analysis_link_url = make_data_analysis_url(reduction_location) if reduction_location else ""
    rb_number = run.experiment.reference_number
    standard_vars, advanced_vars, variable_help = prepare_arguments_for_render(run.arguments, run.instrument.name)
    default_standard_variables, _, __ = get_arguments_from_file(run.instrument.name)

    # picks the unique identifier for a run - for batch runs, it's the pk,
    # and for normal runs it's just the run number
    run_unique_id = run.pk if run.batch_run else run.run_number
    runs = ",".join([str(r.run_number) for r in run.run_numbers.all()])

    page_type = request.GET.get('sort', '-run_number')
    next_run, previous_run, newest_run, oldest_run = get_navigation_runs(instrument_name, run, page_type)

    script_present = ReductionScript(instrument_name).exists()
    rerun_form = RerunForm(script_present=script_present)

    context_dictionary = {
        'run': run,
        'runs': runs,
        'run_unique_id': run_unique_id,
        'run_version': run_version,
        'has_reduce_vars': bool(default_standard_variables),
        'has_reduce_script': script_present,
        'batch_run': run.batch_run,
        'standard_variables': standard_vars,
        'advanced_variables': advanced_vars,
        'variable_help': variable_help,
        'instrument': instrument_name,
        'is_skipped': is_skipped,
        'is_rerun': is_rerun,
        'history': history,
        'data_location': data_location,
        'reduction_location': reduction_location,
        'started_by': started_by,
        'data_analysis_link_url': data_analysis_link_url,
        'current_page': int(request.GET.get('page', 1)),
        'per_page': int(request.GET.get('per_page', 10)),
        'page_type': page_type,
        'filtering': request.GET.get('filter', 'run'),
        'new_path_type': 'linux' if path_type == 'windows' else 'windows',
        'newest_run': newest_run,
        'oldest_run': oldest_run,
        'next_run': next_run,
        'previous_run': previous_run,
        'rerun_form': rerun_form,
        'script_present': script_present,
    }

    if reduction_location:
        try:
            plot_handler = PlotHandler(data_filepath=run.data_location.first().file_path,
                                       server_dir=reduction_location,
                                       rb_number=rb_number)
            local_plot_locs, server_plot_locs = plot_handler.get_plot_file()
            if local_plot_locs:
                context_dictionary['static_plots'] = [
                    location for location in local_plot_locs if not location.endswith(".json")
                ]

                context_dictionary['interactive_plots'] = get_interactive_plot_data(server_plot_locs)
        except Exception as exception:  # pylint: disable=broad-except
            # Lack of plot images is recoverable - we shouldn't stop the whole
            # page rendering if something is wrong with the plot images - but
            # display an error message
            err_msg = "Encountered error while retrieving plots for this run"
            LOGGER.error("%s. Instrument: %s, run %s. RB Number %s Error: %s", err_msg, run.instrument.name, run,
                         rb_number, exception)
            context_dictionary["plot_error_message"] = f"{err_msg}."

    return context_dictionary
