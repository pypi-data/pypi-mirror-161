import django_tables2 as tables
from django_tables2 import Table
from autoreduce_db.reduction_viewer.models import ReductionRun, Experiment
from autoreduce_frontend.reduction_viewer.view_utils import data_status, started_by_id_to_name


class ReductionRunTable(Table):
    '''Table model for displaying Reduction Runs (and batch-runs)'''

    run_number = tables.TemplateColumn(
        """{% load generate_run_link %} <a href="{% generate_run_link record.instrument record %}?
page={{ current_page }}&per_page={{ per_page }}&sort={{ sort }}&filter={{ filtering }}">{{ record.title }}
</a>""",
        attrs={"td": {
            "class": "run-num-links"
        }},
        accessor="run_numbers__run_number")

    status = tables.Column(attrs={"td": {"class": lambda record: data_status(str(record.status))}})

    created = tables.DateTimeColumn(attrs={"td": {"class": "created-dates"}})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ReductionRun
        row_attrs = {"class": "run-row"}
        fields = (
            'run_number',
            'instrument',
            'status',
            'created',
        )
        sequence = (
            'run_number',
            'instrument',
            'status',
            'created',
        )


class ExperimentTable(Table):
    '''Table model for displaying Experiments'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    reference_number = tables.TemplateColumn(
        """<a href="{% url \'experiment_summary\' record.reference_number %}" onClick="event.stopPropagation();">
RB{{ record.reference_number }}</a>""",
        attrs={"td": {
            "class": "experiment-num-links"
        }})

    class Meta:
        model = Experiment
        row_attrs = {"class": "experiment-row", "data-target": "#RB{{ experiment.reference_number }}"}
        fields = ('reference_number', )


class ExperimentSummaryTable(Table):
    '''Table model for displaying Reduction Runs (and batch-runs)'''

    run_number = tables.TemplateColumn(
        """{% load generate_run_link %} <a href="{% generate_run_link record.instrument record %}?
page={{ current_page }}&per_page={{ per_page }}&sort={{ sort }}&filter={{ filtering }}">{{ record.title }}
</a>""",
        attrs={"td": {
            "class": "run-num-links"
        }},
        accessor="run_numbers__run_number")

    status = tables.Column(attrs={"td": {"class": lambda record: data_status(str(record.status))}})

    last_updated = tables.DateTimeColumn(attrs={"td": {"class": "last-updated-dates"}})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ReductionRun
        attrs = {'class': 'table table-striped table-bordered'}
        row_attrs = {"class": "run-row"}
        fields = (
            'run_number',
            'started_by',
            'status',
            'last_updated',
        )
        sequence = (
            'run_number',
            'status',
            'last_updated',
            'started_by',
        )

    @staticmethod
    def render_started_by(value):
        '''
        Render method for started_by column to populate with name
        instead of id.
        '''
        return started_by_id_to_name(value)


class FailQueueTable(Table):
    '''Table model for displaying Failed Runs (and batch-runs)'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    run_number = tables.TemplateColumn(
        """{% load generate_run_link %} <a href="{% generate_run_link record.instrument record %}?
page={{ current_page }}&per_page={{ per_page }}&sort={{ sort }}&filter={{ filtering }}">{{ record.title }}
</a>""",
        attrs={"td": {
            "class": "failed-run-link"
        }},
        accessor="run_numbers__run_number")

    checkbox = tables.CheckBoxColumn(
        accessor="pk",
        attrs={
            "th__input": {
                "id": "selectAllRuns"
            },
            "td__input": {
                "class": "runCheckbox",
                "id": lambda record: "selectRun" + str(record.pk) + "-" + str(record.run_version),
                "data-run_number": lambda record: record.pk,
                "data-run_version": lambda record: record.run_version,
                "data-rb_number": lambda record: record.experiment.reference_number
            }
        },
        orderable=False)

    message = tables.Column(attrs={"td": {"style": "width:600px; word-break: break-word; font-weight: bold;"}})

    created = tables.DateTimeColumn(attrs={"td": {"title": lambda record: record.created}})

    class Meta:
        model = ReductionRun
        attrs = {'class': 'table table-striped table-bordered'}
        row_attrs = {"class": "run-row"}
        fields = ('run_number', 'instrument', 'message', 'created')
        sequence = ('checkbox', 'run_number', 'instrument', 'message', 'created')
