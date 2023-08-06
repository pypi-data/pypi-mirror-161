from django.http import HttpResponseNotFound

from autoreduce_db.reduction_viewer.models import Instrument, ReductionRun
from autoreduce_frontend.autoreduce_webapp.view_utils import render_with, require_admin


@render_with('admin/graph_home.html')
# pylint:disable=no-member
def graph_home(_):
    """
    Render graph page.

    Note:
        _ is replacing the passed in request parameter.
    """
    instruments = Instrument.objects.all()
    context_dictionary = {'instruments': instruments}

    return context_dictionary


@require_admin
@render_with('admin/graph_instrument.html')
# pylint:disable=no-member
def graph_instrument(request, instrument_name):
    """Render instrument specific graphing page."""
    instrument = Instrument.objects.filter(name=instrument_name)
    if not instrument:
        return HttpResponseNotFound('<h1>Instrument not found</h1>')

    runs = (
        ReductionRun.objects.
        # Get the foreign key 'status' now, otherwise many queries made from
        # load_runs which is very slow
        select_related('status')
        # Only get these attributes, to speed it up
        .only('status', 'started', 'finished', 'last_updated', 'created', 'run_number', 'run_description',
              'run_version').filter(instrument=instrument.first()).order_by('-created'))

    try:
        if 'last' in request.GET:
            runs = runs[:int(request.GET.get('last'))]
    except ValueError:
        # Non integer value entered as 'last' parameter so just show all runs
        pass

    # Reverse list so graph displayed in correct order
    runs = runs[::-1]

    for run in runs:
        if run.started and run.finished:
            run.run_time = (run.finished - run.started).total_seconds()
        else:
            run.run_time = 0

    context_dictionary = {'runs': runs, 'instrument': instrument.first().name}

    return context_dictionary
