# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""

from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage

from autoreduce_frontend.selenium_tests.tests.base_tests import ConfigureNewJobsBaseTestCase


# pylint:disable=no-member
class TestBatchRunSummaryPage(ConfigureNewJobsBaseTestCase):
    """
    Test cases for the InstrumentSummary page when the Rerun form is NOT
    visible.
    """

    fixtures = ConfigureNewJobsBaseTestCase.fixtures + ["run_with_one_variable", "batch_run_with_one_variable"]

    def setUp(self) -> None:
        """Set up RunSummaryPage before each test case."""
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 2, 0, batch_run=True)
        self.page.launch()

    def test_reduction_job_panel_displayed(self):
        """Test that the reduction job panel is showing the right things."""
        # only one run in the fixture, get it for assertions
        run = ReductionRun.objects.last()
        assert self.page.reduction_job_panel.is_displayed()
        assert self.page.run_description_text() == f"Run description: {run.run_description}"
        # because it's started_by: -1, determined in `started_by_id_to_name`
        assert self.page.started_by_text() == "Started by: Development team"
        assert self.page.status_text() == "Status: Completed"
        assert self.page.instrument_text() == f"Instrument: {run.instrument.name}"
        assert self.page.rb_number_text() == f"RB Number: {run.experiment.reference_number}"
        assert self.page.last_updated_text() == "Last Updated: 19 Oct 2020, 6:35 p.m."
        assert self.page.data_path_text() == "Data: /tmp"
        assert self.page.reduction_host_text() == "Host: test-host-123"

    def test_non_existent_run(self):
        """
        Test that going to the run summary for a non-existent run will redirect
        back to the runs list page and show a warning message to the user.
        """
        self.page = RunSummaryPage(self.driver, self.instrument_name, 12345, 0, batch_run=True)
        self.page.launch()
        self.driver.get(f"{self.driver.current_url}&filter=batch_runs")
        self.page = RunsListPage(self.driver, self.instrument_name)

        assert self.page.top_alert_message_text == 'Run 12345-0 does not exist. '\
                                                   'Redirected to the instrument page.'
