import logging

from autoreduce_db.reduction_viewer.models import (Instrument, Status)
from autoreduce_qp.queue_processor.reduction.service import ReductionScript
from autoreduce_frontend.autoreduce_webapp.view_utils import (check_permissions, login_and_uows_valid, render_with)
from autoreduce_frontend.reduction_viewer.forms import RerunForm
from autoreduce_frontend.reduction_viewer.views.common import prepare_arguments_for_render

LOGGER = logging.getLogger(__package__)


# pylint:disable=inconsistent-return-statements
@login_and_uows_valid
@check_permissions
@render_with('rerun_jobs.html')
def rerun_jobs(request, instrument=None):
    """
    Handles run submission request
    """
    LOGGER.info('Submitting runs')
    # pylint:disable=no-member
    instrument = Instrument.objects.prefetch_related('reduction_runs').get(name=instrument)
    if request.method == 'GET':
        processing_status = Status.get_processing()
        queued_status = Status.get_queued()

        # pylint:disable=no-member
        runs_for_instrument = instrument.reduction_runs.filter(batch_run=False)
        last_run = instrument.get_last_for_rerun(runs_for_instrument)

        standard_vars, advanced_vars, variable_help = prepare_arguments_for_render(last_run.arguments,
                                                                                   last_run.instrument.name)
        script_present = ReductionScript(instrument).exists()
        rerun_form = RerunForm(script_present=script_present)
        # pylint:disable=no-member
        context_dictionary = {
            'instrument': instrument,
            'last_instrument_run': last_run,
            'processing': runs_for_instrument.filter(status=processing_status),
            'queued': runs_for_instrument.filter(status=queued_status),
            'standard_variables': standard_vars,
            'advanced_variables': advanced_vars,
            'variable_help': variable_help,
            'rerun_form': rerun_form
        }

        return context_dictionary
