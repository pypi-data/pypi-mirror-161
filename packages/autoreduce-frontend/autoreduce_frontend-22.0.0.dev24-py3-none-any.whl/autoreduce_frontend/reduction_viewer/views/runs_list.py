import traceback
import logging

from autoreduce_db.reduction_viewer.models import Experiment, Instrument, ReductionRun, Status
from autoreduce_qp.queue_processor.variable_utils import VariableUtils
from django_tables2 import RequestConfig

from autoreduce_frontend.autoreduce_webapp.view_utils import check_permissions, login_and_uows_valid, render_with
from autoreduce_frontend.reduction_viewer.view_utils import order_runs
from autoreduce_frontend.reduction_viewer.tables import ExperimentTable, ReductionRunTable
from autoreduce_frontend.reduction_viewer.forms import RunsListOptionsForm

LOGGER = logging.getLogger(__package__)


@login_and_uows_valid
@check_permissions
@render_with('runs_list.html')
# pylint:disable=no-member,unused-argument,too-many-locals,broad-except
def runs_list(request, instrument=None):
    """Render instrument summary."""
    try:
        filter_by = request.GET.get('filter', 'run')
        instrument_obj = Instrument.objects.get(name=instrument)
    except Instrument.DoesNotExist:
        return {'message': "Instrument not found."}

    sort_by = request.GET.get('sort', '-run_number')

    try:
        runs = ReductionRun.objects.only('status', 'last_updated', 'run_version',
                                         'run_description').select_related('status').filter(instrument=instrument_obj,
                                                                                            batch_run=False)
        last_instrument_run = runs.filter(batch_run=False).last()
        first_instrument_run = runs.filter(batch_run=False).first()

        runs = order_runs(sort_by=sort_by, runs=runs)

        run_table = ReductionRunTable(runs)
        RequestConfig(request, paginate={"per_page": 10}).configure(run_table)

        options_form = RunsListOptionsForm(initial={
            'per_page': request.GET.get('per_page', 10),
            'filter': request.GET.get('filter', "run")
        })

        if len(runs) == 0:
            return {'message': "No runs found for instrument."}

        current_variables = {}
        try:
            current_variables.update(VariableUtils.get_default_variables(instrument_obj.name, raise_exc=True))
        except FileNotFoundError:
            error_reason = "reduce_vars.py is missing for this instrument"
        except (ImportError, SyntaxError):
            error_reason = "reduce_vars.py has an import or syntax error"
        else:
            error_reason = ""

        context_dictionary = {
            'instrument': instrument_obj,
            'instrument_name': instrument_obj.name,
            'runs': runs,
            'last_instrument_run': last_instrument_run,
            'first_instrument_run': first_instrument_run,
            'processing': runs.filter(status=Status.get_processing(), batch_run=False),
            'queued': runs.filter(status=Status.get_queued(), batch_run=False),
            'filtering': filter_by,
            'sort': sort_by,
            'has_variables': bool(current_variables),
            'error_reason': error_reason,
            'run_table': run_table,
            'per_page': request.GET.get('per_page', 10),
            'current_page': request.GET.get('page', 1),
            'options_form': options_form,
            'info_message': request.GET.get('message', ''),
        }

        if filter_by == 'experiment':
            experiments_and_runs = {}
            experiments = Experiment.objects.filter(reduction_runs__instrument=instrument_obj). \
                order_by('-reference_number').distinct()
            for experiment in experiments:
                associated_runs = runs.filter(experiment=experiment). \
                    order_by('-created')
                experiments_and_runs[experiment] = associated_runs
            experiment_table = ExperimentTable(experiments)
            RequestConfig(request, paginate={"per_page": 10}).configure(experiment_table)
            context_dictionary['experiments'] = experiments_and_runs
            context_dictionary['experiment_table'] = experiment_table
        elif filter_by == 'batch_runs':
            runs = ReductionRun.objects.only('status', 'last_updated', 'run_version',
                                             'run_description').filter(instrument=instrument_obj, batch_run=True)
            runs = order_runs(sort_by=sort_by, runs=runs)
            run_table = ReductionRunTable(runs)
            RequestConfig(request, paginate={"per_page": 10}).configure(run_table)
            context_dictionary['run_table'] = run_table

    except Exception:
        LOGGER.error(traceback.format_exc())
        return {'message': "An unexpected error has occurred when loading the instrument."}

    return context_dictionary
