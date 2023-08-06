from django.db.models import Q

from autoreduce_db.reduction_viewer.models import ReductionRun, Status
from autoreduce_frontend.autoreduce_webapp.icat_cache import ICATCache, ICATConnectionException
from autoreduce_frontend.autoreduce_webapp.settings import USER_ACCESS_CHECKS
from autoreduce_frontend.autoreduce_webapp.view_utils import login_and_uows_valid, render_with
from autoreduce_frontend.autoreduce_webapp.views import render_error

from autoreduce_frontend.reduction_viewer.view_utils import started_by_id_to_name


@login_and_uows_valid
@render_with('run_queue.html')
# pylint:disable=no-member
def run_queue(request):
    """Render status of queue."""
    # Get all runs that should be shown
    queued_status = Status.get_queued()
    processing_status = Status.get_processing()
    pending_jobs = ReductionRun.objects.filter(Q(status=queued_status)
                                               | Q(status=processing_status)).order_by('created')

    # Filter those which the user shouldn't be able to see
    if USER_ACCESS_CHECKS and not request.user.is_superuser:
        try:
            with ICATCache(AUTH='uows', SESSION={'sessionid': request.session['sessionid']}) as icat:
                pending_jobs = filter(lambda job: job.experiment.reference_number in icat.get_associated_experiments(
                    int(request.user.username)), pending_jobs)  # Check RB numbers
                pending_jobs = filter(
                    lambda job: job.instrument.name in icat.get_owned_instruments(int(request.user.username)),
                    pending_jobs)  # Check instrument
        except ICATConnectionException as excep:
            return render_error(request, str(excep))
    # Initialise list to contain the names of user/team that started runs
    started_by = []

    # Cycle through all filtered runs and retrieve the name of the user/team
    # that started the run
    for run in pending_jobs:
        started_by.append(started_by_id_to_name(run.started_by))

    # Zip the run information with the user/team name to enable simultaneous
    # iteration with django
    context_dictionary = {'queue': zip(pending_jobs, started_by)}

    return context_dictionary
