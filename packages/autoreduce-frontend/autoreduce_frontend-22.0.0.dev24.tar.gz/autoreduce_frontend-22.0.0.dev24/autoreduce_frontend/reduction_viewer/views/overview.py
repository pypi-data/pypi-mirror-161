from autoreduce_db.reduction_viewer.models import Instrument
from autoreduce_frontend.autoreduce_webapp.view_utils import login_and_uows_valid, render_with


@login_and_uows_valid
@render_with('overview.html')
# pylint:disable=no-member
def overview(_):
    """
    Render the overview landing page (redirect from /index).

    Note:
        _ is replacing the passed in request parameter.
    """
    context_dictionary = {}
    instruments = Instrument.objects.values_list("name", flat=True)
    if instruments:
        context_dictionary = {'instrument_list': instruments}
    return context_dictionary
