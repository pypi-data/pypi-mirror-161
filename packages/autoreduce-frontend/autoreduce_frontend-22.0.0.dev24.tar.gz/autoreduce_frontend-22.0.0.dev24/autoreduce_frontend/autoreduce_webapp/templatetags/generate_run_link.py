from django.urls import reverse
from django.template import Library

register = Library()


@register.simple_tag
def generate_run_link(instrument_name, run) -> str:
    """
    Generates the url and the GET parameters given the instrument and run.

    Used to render runs:list entries.

    """

    if run.batch_run:
        run_number = run.pk
        url = reverse('runs:batch_summary',
                      kwargs={
                          "instrument_name": instrument_name,
                          "pk": run_number,
                          "run_version": run.run_version
                      })
    else:
        run_number = run.run_number
        url = reverse('runs:summary',
                      kwargs={
                          "instrument_name": instrument_name,
                          "run_number": run_number,
                          "run_version": run.run_version
                      })
    return f"{url}"
