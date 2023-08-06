# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Tests for JobQueuePage
"""
from autoreduce_frontend.selenium_tests.pages.job_queue_page import JobQueuePage
from autoreduce_frontend.selenium_tests.tests.base_tests import (FooterTestMixin, BaseTestCase, NavbarTestMixin,
                                                                 AccessibilityTestMixin)

from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage


class TestJobQueuePage(NavbarTestMixin, BaseTestCase, FooterTestMixin, AccessibilityTestMixin):
    """
    Test cases for JobQueuePage
    """
    fixtures = BaseTestCase.fixtures + ["test_job_queue_fixture"]

    def setUp(self):
        """
        Setup and launch job queue page
        """
        super().setUp()
        self.page = JobQueuePage(self.driver)
        self.page.launch()

    def test_runs_shown_in_table(self):
        """
        Test: All expected runs on table
        """
        expected_runs = ["123", "456"]
        self.assertCountEqual(expected_runs, self.page.get_run_numbers_from_table())

    def test_runs_have_correct_status(self):
        """
        Test runs have expected statuses
        """
        self.assertEqual("Processing", self.page.get_status_from_run(123))
        self.assertEqual("Queued", self.page.get_status_from_run(456))


class TestJobQueuePageBatchRunInQueue(BaseTestCase):
    """
    Test cases for JobQueuePage
    """
    fixtures = BaseTestCase.fixtures + ["test_job_queue_fixture_batch_run"]

    def setUp(self):
        """
        Setup and launch job queue page
        """
        super().setUp()
        self.page = JobQueuePage(self.driver)
        self.page.launch()

    def test_runs_shown_in_table(self):
        """
        Test: All expected runs on table
        """
        expected_runs = ["Batch 123 → 125", "456"]
        self.assertCountEqual(expected_runs, self.page.get_run_numbers_from_table())

    def test_runs_have_correct_status(self):
        """
        Test runs have expected statuses
        """
        self.assertEqual("Processing", self.page.get_status_from_run(123, 125))
        self.assertEqual("Queued", self.page.get_status_from_run(456))

    def test_click_run_link_in_table(self):
        """
        Test: Clicking a queued run correctly changes the page to the run's summary page
              The assertion is done within the click_run method
        """
        self.page.click_run(run_number=456)  # 456 taken from fixture
        run_summary_page = RunSummaryPage(self.driver, "TESTINSTRUMENT", 456, 0)
        assert run_summary_page.reduction_job_panel.is_displayed()

    def test_click_batch_run_link_in_table(self):
        """
        Test: Clicking a queued batch run correctly changes the page to the run's summary page
        """
        self.page.click_batch_run(primary_key=1)  # 1 taken from fixture
        run_summary_page = RunSummaryPage(self.driver, "TESTINSTRUMENT", 1, 0, batch_run=True)
        assert run_summary_page.reduction_job_panel.is_displayed()
