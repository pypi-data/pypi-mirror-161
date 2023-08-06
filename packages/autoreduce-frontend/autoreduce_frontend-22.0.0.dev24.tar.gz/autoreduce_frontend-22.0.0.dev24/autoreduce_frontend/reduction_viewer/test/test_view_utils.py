from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from unittest.mock import Mock, mock_open, patch
from parameterized import parameterized
from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_frontend.autoreduce_webapp.settings import DATA_ANALYSIS_BASE_URL
from autoreduce_frontend.reduction_viewer.view_utils import (convert_software_string_to_dict, get_interactive_plot_data,
                                                             make_data_analysis_url, started_by_id_to_name, order_runs,
                                                             data_status)
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase


def test_make_data_analysis_url_no_instrument_in_string():
    """Test running with a string that doesn't have /instrument/"""
    assert make_data_analysis_url("apples") == ""


def test_make_data_analysis_url_good_url():
    """Test with good string"""
    result = make_data_analysis_url("/instrument/TestInstrument/RBNumber/RB1234567/autoreduced")
    assert "TestInstrument/RBNumber/RB1234567/autoreduced" in result
    assert DATA_ANALYSIS_BASE_URL in result


def test_get_interactive_plot_data():
    """
    Test that get_interactive_plot_data will read only the json calls as expected
    """
    locations = ["location1.png", "location1.json", "location2.jpg", "location2.json"]
    mopen: Mock = mock_open()
    with patch("autoreduce_frontend.reduction_viewer.view_utils.open", mopen, create=True):
        get_interactive_plot_data(locations)
    mopen.assert_any_call(locations[1], mode='r', encoding='utf-8')
    mopen.assert_any_call(locations[3], mode='r', encoding='utf-8')
    assert mopen.call_count == 2


@parameterized.expand([
    [-1, "Development team"],
    [0, "Autoreduction service"],
])
def test_started_by_id_to_name(user_id: int, expected_name: str):
    """
    Test that started_by_id_to_name will return the correct name
    """
    assert started_by_id_to_name(user_id) == expected_name


@patch("autoreduce_frontend.reduction_viewer.view_utils.get_user_model")
@patch("autoreduce_frontend.reduction_viewer.view_utils.LOGGER")
def test_started_by_id_to_name_missing_user(logger: Mock, get_user_model_mock: Mock):
    """
    Test that started_by_id_to_name will log the error if the user does not exist
    """
    get_user_model_mock.return_value.objects.get.side_effect = ObjectDoesNotExist
    assert started_by_id_to_name(100) is None
    logger.error.assert_called_once()


# Test convert_software_string_to_dict in view_utils
def test_convert_software_string_to_dict():
    """
    Test that convert_software_string_to_dict will return the correct dictionary
    """
    assert convert_software_string_to_dict("Mantid-6.2.0") == {'name': 'Mantid', 'version': '6.2.0'}


class ReductionRunTestCase(TestCase):
    fixtures = BaseTestCase.fixtures + ["autoreduce_frontend/autoreduce_webapp/fixtures/eleven_runs.json"]

    def test_order_runs(self):
        """
        Test to ensure ordering of Runs functions as expected
        """
        runs = ReductionRun.objects.all()
        assert runs.count() > 0
        runs = order_runs("-run_number", runs=runs)
        assert runs.first().run_number == 100009
        runs = order_runs("run_number", runs=runs)
        assert runs.first().run_number == 99999
        runs = order_runs("-created", runs=runs)
        assert runs.first().run_number == 99999
        runs = order_runs("created", runs=runs)
        assert runs.first().run_number == 100000
        runs = order_runs("doesn't_exist", runs=runs)
        assert runs.first().run_number == 100009


def test_status_column_colour():
    assert data_status("Error") == "text-danger run-status"
    assert data_status("Processing") == "text-warning run-status"
    assert data_status("Queued") == "text-info run-status"
    assert data_status("Completed") == "text-success run-status"
    assert data_status("Skipped") == "text-dark run-status"
