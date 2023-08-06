import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_frontend.reduction_viewer.filters import validate_run_number, filter_run_number
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase

allowed_queries = ['99999', '99999,100000', '100000-100002', '100000-100005,100007-100009']
banned_queries = ['60200$', '60200,', '60200-', 'a', '60200£', '60200-23434, 23432-']


class FilterRunNumber(TestCase):
    fixtures = BaseTestCase.fixtures + ["autoreduce_frontend/autoreduce_webapp/fixtures/eleven_runs.json"]

    def test_filter_run_number(self):
        """
        Test to ensure allowable filtering of run number on Search page
        works as expected.
        """
        runs = ReductionRun.objects.all()
        for query in allowed_queries:
            filtered_qs = filter_run_number(queryset=runs, name="run_number", value=query)
            assert len(filtered_qs) > 0


def test_allowed_queries():
    """
    Test running filter with allowed queries.
    Assert no ValidationError exception is raised
    """
    try:
        for query in allowed_queries:
            validate_run_number(query)
    except ValidationError as exc:
        assert False, {exc}


def test_banned_queries():
    """
    Test running filter with banned queries.
    Assert ValidationError exception is raised
    """
    for query in banned_queries:
        with pytest.raises(ValidationError) as exc:
            validate_run_number(query)
