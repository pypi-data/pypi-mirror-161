# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from django.urls import reverse
from selenium.webdriver.common.by import By
from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_frontend.selenium_tests.pages.rerun_jobs_page import RerunJobsPage
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseIntegrationTestCase
from autoreduce_frontend.selenium_tests.utils import submit_and_wait_for_result


# pylint:disable=no-member
class TestRerunJobsRangePageIntegration(BaseIntegrationTestCase):
    fixtures = BaseIntegrationTestCase.fixtures + ["two_runs"]

    @classmethod
    def setUpClass(cls):
        """Starts all external services"""
        super().setUpClass()
        cls.data_archive.add_reduction_script(cls.instrument_name,
                                              """def main(input_file, output_dir): print('some text')""")
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                """standard_vars={"variable1":"test_variable_value_123"}""")
        cls.rb_number = 1234567
        cls.run_number = [99999, 100000]

    def setUp(self) -> None:
        """Sets up and launches RerunJobsPage before each test case"""
        super().setUp()
        self.page = RerunJobsPage(self.driver, self.instrument_name)
        self.page.launch()

    def _verify_runs_exist_and_have_variable_value(self, variable_value):
        """
        Verifies that the run with version 1 exists and has the expected value
        """

        def make_run_url(run_number):
            """Constructs the url of the run summary with a django reverse"""
            return reverse("runs:summary",
                           kwargs={
                               "instrument_name": self.instrument_name,
                               "run_number": run_number,
                               "run_version": 1
                           })

        runs_list_page = RunsListPage(self.driver, self.instrument_name)
        for run in self.run_number:
            runs_list_page.launch()
            run_number_v1 = self.driver.find_element(By.CSS_SELECTOR, f'[href*="{make_run_url(run)}"]')
            assert run_number_v1.is_displayed()
            assert RunSummaryPage(self.driver, self.instrument_name, run,
                                  1).launch().variable1_field_val == variable_value
            vars_for_run_v1 = ReductionRun.objects.filter(run_numbers__run_number=run).last().arguments.as_dict()
            for _, value in vars_for_run_v1["standard_vars"].items():
                assert value == variable_value

    def test_run_range_default_variable_value(self):
        """
        Test setting a run range with the default variable value
        """
        assert not self.page.form_validation_message.is_displayed()
        expected_run = "99999-100000"
        self.page.run_range_field = expected_run
        result = submit_and_wait_for_result(self, expected_runs=2)
        expected_url = reverse("runs:run_confirmation", kwargs={"instrument": self.instrument_name})
        assert expected_url in self.driver.current_url
        assert len(result) == 4

        self._verify_runs_exist_and_have_variable_value("value2")

    def test_run_range_new_variable_value(self):
        """
        Test setting a run range with a new variable value
        """
        expected_run = "99999-100000"
        self.page.run_range_field = expected_run
        new_value = "some_new_value"
        self.page.variable1_field = new_value
        result = submit_and_wait_for_result(self, expected_runs=2)
        expected_url = reverse("runs:run_confirmation", kwargs={"instrument": self.instrument_name})
        assert expected_url in self.driver.current_url
        assert len(result) == 4

        self._verify_runs_exist_and_have_variable_value(new_value)
