from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from autoreduce_frontend.autoreduce_webapp.icat_cache import ICATConnectionException
from autoreduce_frontend.autoreduce_webapp.settings import DEVELOPMENT_MODE
from autoreduce_frontend.autoreduce_webapp.uows_client import UOWSClient
from autoreduce_frontend.autoreduce_webapp.views import render_error
from autoreduce_frontend.reduction_viewer.view_utils import deactivate_invalid_instruments, make_return_url


@deactivate_invalid_instruments
def index(request):
    """Render the index page."""
    return_url = make_return_url(request, request.GET.get('next'))

    use_query_next = request.build_absolute_uri(request.GET.get('next'))
    default_next = 'overview'

    authenticated = False

    if DEVELOPMENT_MODE:
        user = authenticate(username="super", password="super", backend="django.contrib.auth.backends.ModelBackend")
        login(request, user)
        authenticated = True
    else:
        if 'sessionid' in request.session.keys():
            authenticated = request.user.is_authenticated and UOWSClient().check_session(request.session['sessionid'])

    if authenticated:
        return_url = use_query_next if request.GET.get('next') else default_next
    elif request.GET.get('sessionid'):
        request.session['sessionid'] = request.GET.get('sessionid')
        try:
            user = authenticate(token=request.GET.get('sessionid'))
        except ICATConnectionException as excep:
            return render_error(request, str(excep))

        if user is not None:
            if user.is_active:
                login(request, user)
                return_url = use_query_next if request.GET.get('next') else default_next

    return redirect(return_url)
