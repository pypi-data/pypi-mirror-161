import logging

from autoreduce_db.reduction_viewer.models import Experiment, ReductionRun
from django_tables2.config import RequestConfig
from autoreduce_frontend.autoreduce_webapp.icat_cache import ICATCache
from autoreduce_frontend.autoreduce_webapp.settings import DEVELOPMENT_MODE
from autoreduce_frontend.autoreduce_webapp.view_utils import check_permissions, login_and_uows_valid, render_with
from autoreduce_frontend.reduction_viewer.tables import ExperimentSummaryTable

LOGGER = logging.getLogger(__package__)


@login_and_uows_valid
@check_permissions
@render_with('experiment_summary.html')
# pylint:disable=no-member,too-many-locals,broad-except
def experiment_summary(request, reference_number=None):
    """Render experiment summary."""
    try:
        experiment = Experiment.objects.get(reference_number=reference_number)
        runs = ReductionRun.objects.filter(experiment=experiment, batch_run=False).order_by('-last_updated')
        experiment_summary_table = ExperimentSummaryTable(runs)
        RequestConfig(request, paginate={"per_page": 10}).configure(experiment_summary_table)

        try:
            if DEVELOPMENT_MODE:
                # If we are in development mode use user/password for ICAT from
                # django settings e.g. do not attempt to use same authentication
                # as the user office
                with ICATCache() as icat:
                    experiment_details = icat.get_experiment_details(int(reference_number))
            else:
                with ICATCache(AUTH='uows', SESSION={'sessionid': request.session['sessionid']}) as icat:
                    experiment_details = icat.get_experiment_details(int(reference_number))

        except Exception as icat_e:
            LOGGER.error(icat_e)
            experiment_details = {
                'reference_number': '',
                'start_date': '',
                'end_date': '',
                'title': '',
                'summary': '',
                'instrument': '',
                'pi': '',
            }

        context_dictionary = {
            'runs': runs,
            'experiment_summary_table': experiment_summary_table,
            'experiment': experiment,
            'run_count': len(runs),
            'experiment_details': experiment_details,
            'per_page': request.GET.get('per_page', 10),
            'current_page': request.GET.get('page', 1),
        }

    except Exception as exception:
        LOGGER.error(exception)
        context_dictionary = {"error": str(exception)}

    return context_dictionary
