# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""

from django.urls import reverse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_frontend.autoreduce_webapp.templatetags.encode_b64 import encode_b64
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (ConfigureNewJobsBaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin)


# pylint:disable=no-member
class TestRunSummaryPage(ConfigureNewJobsBaseTestCase, FooterTestMixin, NavbarTestMixin):
    """
    Test cases for the InstrumentSummary page when the Rerun form is NOT
    visible.
    """

    fixtures = ConfigureNewJobsBaseTestCase.fixtures + ["run_with_one_variable"]

    def setUp(self) -> None:
        """Set up RunSummaryPage before each test case."""
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 99999, 0)
        self.page.launch()

    def test_reduction_job_panel_displayed(self):
        """Test that the reduction job panel is showing the right things."""
        # only one run in the fixture, get it for assertions
        run = ReductionRun.objects.first()
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

    def test_reduction_job_panel_reset_to_values_first_used_for_run(self):
        """
        Test that the button to reset the variables to the values first used for
        the run works.
        """
        self.page.toggle_button.click()
        self.page.variable1_field = "the new value in the field"

        self.page.reset_to_initial_values.click()

        # need to re-query the driver because resetting replaces the elements
        assert self.page.variable1_field.get_attribute("value") == "value1"

    def test_reduction_job_panel_reset_to_current_reduce_vars(self):
        """
        Test that the button to reset the variables to the values from the
        reduce_vars script works.
        """
        self.page.toggle_button.click()
        self.page.variable1_field = "the new value in the field"

        self.page.reset_to_current_values.click()

        # need to re-query the driver because resetting replaces the elements
        assert self.page.variable1_field.get_attribute("value") == "test_variable_value_123"

    def test_rerun_form(self):
        """
        Test that the rerun form shows contents from Variable in database (from
        the fixture) and not reduce_vars.py.
        """
        rerun_form = self.page.rerun_form
        assert not rerun_form.is_displayed()
        self.page.toggle_button.click()
        assert rerun_form.is_displayed()
        assert rerun_form.find_element(By.ID,
                                       f"var-standard-{encode_b64('variable1')}").get_attribute("value") == "value1"
        labels = rerun_form.find_elements(By.TAG_NAME, "label")

        WebDriverWait(self.driver, 10).until(lambda _: labels[0].text == "Re-run description")
        WebDriverWait(self.driver, 10).until(lambda _: labels[1].text == "variable1")
        WebDriverWait(self.driver, 10).until(lambda _: labels[2].text == "Software*")

    def test_back_to_instruments_goes_back(self):
        """Test that clicking back goes back to the instrument."""
        back = self.page.cancel_button
        assert back.is_displayed()
        assert back.text == f"Back to {self.instrument_name} runs"
        back.click()
        assert reverse("runs:list", kwargs={"instrument": self.instrument_name}) in self.driver.current_url

    def test_reset_single_to_initial(self):
        """
        Tests changing the value of a variable field and resetting to the
        initial value, by using the inline button.
        """
        self.page.toggle_button.click()
        initial_value = self.page.variable1_field_val
        self.page.variable1_field = "the new value in the field"
        assert self.page.variable1_field_val != initial_value

        self.page.variable1_field_reset_buttons.to_initial.click()
        assert self.page.variable1_field_val == initial_value

    def test_reset_single_to_script(self):
        """
        Test that changing the value of a variable field and resetting to the
        script value, by using the inline button.
        """
        self.page.toggle_button.click()
        initial_value = "test_variable_value_123"
        self.page.variable1_field = "the new value in the field"
        assert self.page.variable1_field_val != initial_value

        self.page.variable1_field_reset_buttons.to_script.click()
        assert self.page.variable1_field_val == initial_value

    def test_toggle_data_path_button(self):
        """
        Test that selecting data toggle path runs script to
        alternative between '/' and '\\'
        """
        self.page.toggle_data_path_button.click()
        assert self.page.data_path_text() == "Data: \\tmp"
        self.page.toggle_data_path_button.click()
        assert self.page.data_path_text() == "Data: /tmp"

    def test_non_existent_run(self):
        """
        Test that going to the run summary for a non-existent run will redirect
        back to the runs list page and show a warning message to the user.
        """
        self.page = RunSummaryPage(self.driver, self.instrument_name, 12345, 0)
        self.page.launch()
        self.page = RunsListPage(self.driver, self.instrument_name)

        assert self.page.top_alert_message_text == 'Run 12345-0 does not exist. '\
                                                   'Redirected to the instrument page.'
