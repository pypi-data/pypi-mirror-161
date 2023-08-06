from autoreduce_db.reduction_viewer.models import Experiment, ReductionRun
from django_tables2 import RequestConfig

from autoreduce_frontend.autoreduce_webapp.view_utils import (check_permissions, login_and_uows_valid, render_with)
from autoreduce_frontend.reduction_viewer.filters import ExperimentFilter, ReductionRunFilter
from autoreduce_frontend.reduction_viewer.tables import ExperimentTable, ReductionRunTable
from autoreduce_frontend.reduction_viewer.forms import SearchOptionsForm


@login_and_uows_valid
@check_permissions
@render_with('search.html')
def search(request):
    """Render search page."""
    run_list = ReductionRun.objects.none()
    run_description_qualifier = request.GET.get("run_description_qualifier", "contains")
    run_filter = ReductionRunFilter(request.GET, run_description_qualifier=run_description_qualifier, queryset=run_list)
    run_table = ReductionRunTable(run_list, order_by="-run_number")

    filter_by = "run"

    experiment_list = Experiment.objects.none()
    experiment_filter = ExperimentFilter(request.GET, queryset=experiment_list)
    experiment_table = ExperimentTable(experiment_list, order_by="-reference_number")
    RequestConfig(request, paginate={"per_page": 10}).configure(experiment_table)

    if 'run_number' in request.GET:
        run_list = ReductionRun.objects.all()
        run_description_qualifier = request.GET.get("run_description_qualifier", "contains")
        run_filter = ReductionRunFilter(request.GET,
                                        run_description_qualifier=run_description_qualifier,
                                        queryset=run_list)
        run_table = ReductionRunTable(run_filter.qs, order_by="-run_number")
        RequestConfig(request, paginate={"per_page": 10}).configure(run_table)
    if "reference_number" in request.GET:
        experiment_list = Experiment.objects.all()
        experiment_filter = ExperimentFilter(request.GET, queryset=experiment_list)
        experiment_table = ExperimentTable(experiment_filter.qs, order_by="-reference_number")
        RequestConfig(request, paginate={"per_page": 10}).configure(experiment_table)
        filter_by = "experiment"

    options_form = SearchOptionsForm(initial={'pagination': request.GET.get('per_page', 10)})
    run_message = "Sorry, no runs found for this criteria."
    experiment_message = "Sorry, no experiments found for this criteria."
    context_dictionary = {
        'run_filter': run_filter,
        'experiment_filter': experiment_filter,
        'run_table': run_table,
        'experiment_table': experiment_table,
        'run_message': run_message,
        'experiment_message': experiment_message,
        'options_form': options_form,
        'per_page': request.GET.get('per_page', 10),
        'current_page': int(request.GET.get('page', 1)),
        'sort': request.GET.get('sort', '-run_number'),
        'run_description_qualifier': run_description_qualifier,
        'filtering': filter_by,
    }
    return context_dictionary
