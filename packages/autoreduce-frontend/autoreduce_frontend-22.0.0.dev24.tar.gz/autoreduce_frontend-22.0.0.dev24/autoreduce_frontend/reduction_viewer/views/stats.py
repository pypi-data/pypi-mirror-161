from autoreduce_db.reduction_viewer.models import ReductionRun, Status
from autoreduce_frontend.autoreduce_webapp.view_utils import render_with, require_admin


@require_admin
@render_with('admin/stats.html')
# pylint:disable=no-member
def stats(_):
    """
    Render run statistics page.

    Note:
        _ is replacing the passed in request parameter.
    """
    statuses = []
    for status in Status.objects.all():
        status_count = (
            ReductionRun.objects.
            # Get the foreign key 'status' now, otherwise many queries made from
            # load_runs which is very slow
            select_related('status')
            # Only get these attributes, to speed it up
            .only('status').filter(status__value=status.value).count())
        statuses.append({'name': status, 'count': status_count})

    context_dictionary = {
        'statuses': statuses,
    }

    return context_dictionary
