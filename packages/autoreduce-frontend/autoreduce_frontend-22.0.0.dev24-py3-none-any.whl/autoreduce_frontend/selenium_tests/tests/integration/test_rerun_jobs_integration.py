# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from django.urls import reverse
from autoreduce_frontend.selenium_tests.pages.rerun_jobs_page import RerunJobsPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseIntegrationTestCase
from autoreduce_frontend.selenium_tests.utils import submit_and_wait_for_result


class TestRerunJobsPageIntegration(BaseIntegrationTestCase):
    fixtures = BaseIntegrationTestCase.fixtures + ["rerun_jobs_integration"]

    @classmethod
    def setUpClass(cls):
        """Starts external services and sets instrument for all test cases"""
        super().setUpClass()
        cls.data_archive.add_reduction_script(cls.instrument_name,
                                              """def main(input_file, output_dir): print('some text')""")
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                """standard_vars={"variable1":"test_variable_value_123"}""")
        # used by find_run_in_database to find the run that we're looking for
        cls.rb_number = 1234567
        cls.run_number = 62000

    def setUp(self) -> None:
        """Sets up RerunJobsPage before each test case"""
        super().setUp()
        self.page = RerunJobsPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_submit_rerun_same_variables(self):
        """
        Test: Just opening the submit page and clicking rerun
        """
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments == result[1].arguments

    def test_submit_rerun_same_script(self):
        """
        Test: Open the submit page, select reuse stored script, and clicking rerun
        """
        # Check if radio button is selected, and if it isn't, click it
        if not self.page.reuse_script_radio.is_selected():
            self.page.reuse_script_radio.click()
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments == result[1].arguments

    def test_submit_rerun_use_reducepy(self):
        """
        Test: Open the submit page, select use reduce.py, and clicking rerun
        """
        # Check if radio button is selected, and if it isn't, click it
        if not self.page.use_reducepy_file_radio.is_selected():
            self.page.use_reducepy_file_radio.click()
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments == result[1].arguments

    def test_submit_rerun_changed_variable_arbitrary_value(self):
        """
        Test: Open submit page, change a variable, submit the run
        """
        # change the value of the variable field

        new_value = "the new value in the field"
        self.page.variable1_field = new_value
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1
        assert result[1].arguments.as_dict()["standard_vars"]["variable1"] == new_value

    def test_submit_rerun_after_clicking_reset_current_script(self):
        """
        Test: Submitting a run after clicking the "Reset to values in the current reduce_vars script"
              uses the values saved in the current reduce_vars script
        """
        self.page.reset_to_current_values.click()
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[1].arguments.as_dict()["standard_vars"]["variable1"] == "test_variable_value_123"

    def test_submit_confirm_page(self):
        """
        Test: Submitting a run leads to the correct page
        """
        result = submit_and_wait_for_result(self)
        expected_url = reverse("runs:run_confirmation", kwargs={"instrument": self.instrument_name})
        assert expected_url in self.driver.current_url
        assert len(result) == 2

    def test_empty_run_range(self):
        """
        Test form validation shown an error message when an empty run range is sent
        """
        assert not self.page.form_validation_message.is_displayed()
        self.page.run_range_field = ""
        self.page.submit_button.click()
        assert self.page.form_validation_message.is_displayed()

    def test_invalid_run_range(self):
        """
        Test form validation shown an error message when an invalid run range is sent
        """
        assert not self.page.form_validation_message.is_displayed()
        self.page.run_range_field = "-1"
        self.page.submit_button.click()
        assert self.page.form_validation_message.is_displayed()

    def test_non_existent_run_range(self):
        """
        Test form validation shown an error message when a non existent run range is sent
        """
        assert not self.page.form_validation_message.is_displayed()
        expected_run = "123123123"
        self.page.run_range_field = expected_run
        self.page.submit_button.click()

        expected_url = reverse("runs:run_confirmation", kwargs={"instrument": self.instrument_name})
        assert expected_url in self.driver.current_url

        assert self.page.error_container.is_displayed()
        assert self.page.error_message_text() == f"Run number {expected_run} hasn't been ran by autoreduction yet."


class TestRerunJobsPageIntegrationSkippedOnly(BaseIntegrationTestCase):
    fixtures = BaseIntegrationTestCase.fixtures + ["skipped_run"]

    @classmethod
    def setUpClass(cls):
        """Starts external services and sets instrument for all test cases"""
        super().setUpClass()
        cls.data_archive.add_reduction_script(cls.instrument_name,
                                              """def main(input_file, output_dir): print('some text')""")
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                """standard_vars={"variable1":"test_variable_value_123"}""")

        cls.rb_number = 1234567
        cls.run_number = 99999

    def setUp(self) -> None:
        """Sets up RerunJobsPage before each test case"""
        super().setUp()
        self.page = RerunJobsPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_submit_rerun_after_clicking_reset_current_script(self):
        """
        Test: Submitting a run after clicking the "Reset to values in the current reduce_vars script"
              uses the values saved in the current reduce_vars script
        """
        self.page.reset_to_current_values.click()
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[1].arguments.as_dict()["standard_vars"]["variable1"] == "test_variable_value_123"
