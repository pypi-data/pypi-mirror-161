from autoreduce_frontend.autoreduce_webapp.view_utils import render_with


@render_with('help.html')
# pylint:disable=redefined-builtin
def help(_):
    """
    Render help page.

    Note:
        _ is replacing the passed in request parameter.
    """
    return {}
