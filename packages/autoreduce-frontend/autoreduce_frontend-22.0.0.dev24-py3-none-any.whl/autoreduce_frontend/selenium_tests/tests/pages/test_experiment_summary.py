# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the experiment summary page."""
from autoreduce_frontend.selenium_tests.pages.experiment_summary_page import ExperimentSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (AccessibilityTestMixin, BaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin)


# pylint:disable=no-member
class TestExperimentSummaryPage(BaseTestCase, AccessibilityTestMixin, FooterTestMixin, NavbarTestMixin):
    """
    Test cases for the Experiment Summary page
    """

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """Set up RunSummaryPage before each test case."""
        super().setUp()
        self.page = ExperimentSummaryPage(self.driver, 1234567)
        self.page.launch()

    def test_reduction_job_panel_displayed(self):
        """Test that the reduction job panel is showing the right things."""
        assert self.page.reduction_job_panel.is_displayed()

    def test_table_column_attributes(self):
        """Test that the attributes (class name etc.) to the status column are being added."""
        self.page.launch()
        status_list = self.page.get_status_from_table()
        assert len(status_list) > 0
