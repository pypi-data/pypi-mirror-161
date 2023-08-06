from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from autoreduce_frontend.autoreduce_webapp.uows_client import UOWSClient
from autoreduce_frontend.autoreduce_webapp.view_utils import login_and_uows_valid


@login_and_uows_valid
def logout(request):
    """Render the logout page."""
    session_id = request.session.get('sessionid')
    if session_id:
        UOWSClient().logout(session_id)
    django_logout(request)
    request.session.flush()
    return redirect('overview')
