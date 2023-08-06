# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from django.urls import reverse

from autoreduce_frontend.selenium_tests.pages.configure_new_runs_page import ConfigureNewRunsPage
from autoreduce_frontend.selenium_tests.pages.variables_summary_page import VariableSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (ConfigureNewJobsBaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin, AccessibilityTestMixin)


# pylint:disable=duplicate-code
class TestConfigureNewRunsPage(ConfigureNewJobsBaseTestCase, NavbarTestMixin, FooterTestMixin, AccessibilityTestMixin):
    fixtures = ConfigureNewJobsBaseTestCase.fixtures + ["two_runs"]

    def setUp(self) -> None:
        """Sets up the ConfigureNewRunsPage before each test case"""
        super().setUp()
        self.page = ConfigureNewRunsPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_reset_values_does_reset_the_values(self):
        """Test that the button to reset the variables to the values from the reduce_vars script works"""
        self.page.variable1_field = "the new value in the field"
        self.page.reset_to_current_values.click()

        # need to re-query the driver because resetting replaces the elements
        assert self.page.variable1_field_val == "test_variable_value_123"  # pylint:disable=no-member

    def test_back_to_instruments_goes_back(self):
        """
        Test: Clicking back goes back to the instrument
        """
        back = self.page.cancel_button
        assert back.is_displayed()
        assert back.text == "Cancel"
        back.click()
        assert reverse("runs:list", kwargs={"instrument": self.instrument_name}) in self.driver.current_url

    def test_go_to_other_goes_to_experiment(self):
        """Test: clicking the link to configure by experiment goes to configure by experiment"""
        self.page.go_to_other.click()
        url = reverse("runs:variables_by_experiment",
                      kwargs={
                          "instrument": self.instrument_name,
                          "experiment_reference": 1234567
                      })
        assert url in self.driver.current_url

    def test_go_to_other_goes_to_run_range(self):
        """Test: Clicking the link to configure by run range goes to run range"""
        self.page = ConfigureNewRunsPage(self.driver, self.instrument_name, experiment_reference=1234567)
        self.page.launch()

        self.page.go_to_other.click()
        url = reverse("runs:variables", kwargs={"instrument": self.instrument_name, "start": 100001})
        assert url in self.driver.current_url


class TestConfigureNewRunsPageSkippedOnly(ConfigureNewJobsBaseTestCase, NavbarTestMixin, FooterTestMixin):
    fixtures = ConfigureNewJobsBaseTestCase.fixtures + ["skipped_run"]

    def setUp(self) -> None:
        """Sets up the ConfigureNewRunsPage before each test case"""
        super().setUp()
        self.page = ConfigureNewRunsPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_configure_skipped_only_run_vars(self):
        """Test that configuring new runs works even with only skipped runs present"""
        self.page.variable1_field = "the new value in the field"

        self.page.submit_button.click()
        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.current_arguments_by_run.text == 'Current Arguments\nRuns\n99999\n99999\n'\
                                                        'standard_vars\nvariable1: value1\nadvanced_vars'

        assert "Runs\n100000\nOngoing" in summary.upcoming_arguments_by_run.text

    def test_configure_skipped_only_exp_vars(self):
        """Test that configuring new runs works even with only skipped runs present"""
        self.page = ConfigureNewRunsPage(self.driver, self.instrument_name, experiment_reference=1234567)
        self.page.launch()
        self.page.variable1_field = "the new value in the field"

        self.page.submit_button.click()
        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.current_arguments_by_run.text == 'Current Arguments\nRuns\n99999\nOngoing\n'\
                                                        'standard_vars\nvariable1: value1\nadvanced_vars'
        assert summary.upcoming_arguments_by_experiment.is_displayed()
        assert "Experiment\n#1234567" in summary.upcoming_arguments_by_experiment.text
