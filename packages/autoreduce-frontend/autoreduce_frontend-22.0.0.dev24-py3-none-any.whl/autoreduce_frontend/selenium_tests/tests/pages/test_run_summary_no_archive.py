# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""
from selenium.webdriver.support.ui import WebDriverWait
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (AccessibilityTestMixin, BaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin)


# pylint:disable=no-member
class TestRunSummaryPageNoArchive(NavbarTestMixin, BaseTestCase, FooterTestMixin, AccessibilityTestMixin):
    fixtures = BaseTestCase.fixtures + ["run_with_one_variable"]

    @classmethod
    def setUpClass(cls):
        """Set the instrument for all test cases."""
        super().setUpClass()
        cls.instrument_name = "TESTINSTRUMENT"

    def setUp(self) -> None:
        """Set up RunSummaryPage before each test case."""
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 99999, 0)
        self.page.launch()

    def test_opening_run_summary_without_reduce_vars(self):
        """
        Test that opening the run summary without a reduce_vars.py file present
        for the instrument will not show the "Reset to current" buttons as there
        are no current values.
        """
        self.page.toggle_button.click()
        assert WebDriverWait(self.driver, 10).until(lambda _: self.page.vars_warning_message.is_displayed())
        assert "The reduce_vars.py script is missing" in self.page.vars_warning_message.text
