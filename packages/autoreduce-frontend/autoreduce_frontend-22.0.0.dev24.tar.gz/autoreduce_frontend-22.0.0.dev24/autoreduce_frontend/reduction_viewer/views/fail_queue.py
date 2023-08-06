import json
import logging
from django.db.models import Q
from django_tables2.config import RequestConfig

from autoreduce_db.reduction_viewer.models import ReductionRun, Status
from autoreduce_frontend.autoreduce_webapp.view_utils import (login_and_uows_valid, render_with, require_admin)
from autoreduce_frontend.reduction_viewer.tables import FailQueueTable
from autoreduce_frontend.reduction_viewer.forms import FailedQueueOptionsForm

LOGGER = logging.getLogger(__package__)


@require_admin
@login_and_uows_valid
@render_with('fail_queue.html')
# pylint:disable=no-member,too-many-locals,broad-except
def fail_queue(request):
    """Render status of failed queue."""
    # Render the page
    error_status = Status.get_error()
    failed_jobs = ReductionRun.objects.filter(Q(status=error_status)
                                              & Q(hidden_in_failviewer=False)).order_by('-created')
    if len(failed_jobs) == 0:
        return {'queue': []}

    fail_queue_table = FailQueueTable(failed_jobs)
    RequestConfig(request, paginate={"per_page": 10}).configure(fail_queue_table)

    options_form = FailedQueueOptionsForm(initial={'per_page': request.GET.get('per_page', 10)})

    context_dictionary = {
        'queue': failed_jobs,
        'fail_queue_table': fail_queue_table,
        'status_success': Status.get_completed(),
        'status_failed': Status.get_error(),
        'per_page': request.GET.get('per_page', 10),
        'current_page': request.GET.get('page', 1),
        'options_form': options_form
    }

    if request.method == 'POST':
        # Perform the specified action
        action = request.POST.get("action", "default")
        selected_run_string = request.POST.get("selectedRuns", [])
        selected_runs = json.loads(selected_run_string)
        try:
            for run in selected_runs:
                run_number = int(run[0])
                run_version = int(run[1])

                reduction_run = failed_jobs.get(pk=run_number, run_version=run_version)

                if action == "hide":
                    reduction_run.hidden_in_failviewer = True
                    reduction_run.save()
                elif action == "default":
                    pass

        except Exception as exception:
            fail_str = f'Selected action failed: {type(exception).__name__} {exception}'
            LOGGER.info("Failed to carry out fail_queue action - %s", fail_str)
            context_dictionary["message"] = fail_str

    return context_dictionary
